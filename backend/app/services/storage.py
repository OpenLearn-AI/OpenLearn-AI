"""S3-compatible (MinIO) object-storage helper for course materials.

Week 6 scope is presigned upload URLs only: FastAPI never proxies the file
bytes. Week 8 (B5) adds the worker-side fetch helper agreed with the Backend
pod (handoff H2): ``download_material_to_temp`` downloads a stored material
object into a caller-owned temporary directory. Credentials come exclusively
from deployment configuration (``config``), never from source code.

Week 9 adds ``compute_material_sha256`` (streamed hash for dedup),
``get_material_object_info`` (size + ETag), ``delete_material_object`` and
``delete_material_objects``. All are blocking boto3 calls; async callers
must offload them with ``asyncio.to_thread``.

Uploads use a presigned POST so the 10 MiB size cap is enforced by the
storage service itself (a presigned PUT cannot limit the size). The ETag
recorded at registration pins the exact object version that was hashed:
hashing and processing both read with ``If-Match``, so a replaced object is
rejected instead of processed (``MaterialObjectChangedError``).
"""

import hashlib
import shutil
from pathlib import Path, PurePosixPath
from typing import NamedTuple

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.config import settings

#: Streaming chunk size for content hashing (1 MiB): large enough to keep
#: round-trips negligible, small enough that peak memory stays flat for any
#: object size.
_HASH_CHUNK_SIZE = 1024 * 1024

#: S3 ``DeleteObjects`` accepts at most 1000 keys per request.
_DELETE_BATCH_SIZE = 1000


class MaterialObjectChangedError(Exception):
    """The stored object no longer matches the ETag recorded at registration."""


class StoredObject(NamedTuple):
    """Size (bytes) and ETag of a stored object."""

    size: int
    etag: str


def _is_precondition_failed(exc: ClientError) -> bool:
    error = exc.response.get("Error", {}) or {}
    status = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    return str(error.get("Code", "")) == "PreconditionFailed" or status == 412


def _s3_client():
    """Build an S3-compatible client from the configured endpoint/credentials.

    SigV4 is forced explicitly: on non-AWS endpoints boto3 may fall back to
    the legacy SigV2 scheme, whose signatures cover the Content-Type header —
    breaking browser uploads that send their own Content-Type. SigV4 presigned
    URLs sign host/path only, so any browser Content-Type is accepted.
    """
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key_id,
        aws_secret_access_key=settings.s3_secret_access_key,
        region_name=settings.s3_region_name,
        config=Config(signature_version="s3v4"),
    )


def generate_upload_post(object_key: str) -> dict:
    """Return a time-limited presigned POST (``url`` + form ``fields``).

    The client uploads the file directly to storage; nothing is proxied by the
    backend. The signed policy limits the object to
    ``settings.max_upload_size_bytes`` (``content-length-range``), so storage
    rejects larger uploads.
    """
    client = _s3_client()
    return client.generate_presigned_post(
        Bucket=settings.s3_bucket_name,
        Key=object_key,
        Conditions=[["content-length-range", 1, settings.max_upload_size_bytes]],
        ExpiresIn=settings.s3_url_expiration_seconds,
    )


def download_material_to_temp(
    s3_key: str,
    destination_dir: str | Path,
    expected_etag: str | None = None,
) -> Path:
    """Download a stored material object into a caller-owned directory.

    B5 worker-side fetch helper; the pattern was approved by the Backend pod
    (handoff H2, roadmap Section 10.2) before it landed:

    * synchronous — boto3 is sync and the Celery task's event loop is
      task-local, so a blocking download delays nothing else;
    * input is the material's ``s3_key`` (bucket/credentials come from
      ``settings``; the client construction is the existing ``_s3_client()``
      reused unchanged);
    * writes the object into ``destination_dir`` — a per-task temporary
      directory created by the caller (the Celery seam) — and returns the
      local :class:`~pathlib.Path` of the downloaded file (Docling and the
      OCR source resolver are path-oriented);
    * the caller owns the directory and its cleanup: this helper creates no
      global state and deletes nothing.

    The file name is the object key's basename, preserving the original
    suffix for the downstream format detection (``services/ingestion.py``).
    Storage and authentication errors (``botocore.exceptions.ClientError``
    and friends) propagate unchanged to the caller.

    When ``expected_etag`` is given (the ETag recorded at registration) the
    object is read with ``If-Match``; an object replaced since registration
    raises :class:`MaterialObjectChangedError` instead of being processed.
    """
    filename = PurePosixPath(s3_key).name
    if not filename or filename in {".", ".."}:
        raise ValueError(f"Invalid material S3 key: {s3_key!r}")
    destination = Path(destination_dir) / filename
    client = _s3_client()
    if expected_etag is None:
        client.download_file(settings.s3_bucket_name, s3_key, str(destination))
        return destination
    try:
        response = client.get_object(
            Bucket=settings.s3_bucket_name, Key=s3_key, IfMatch=expected_etag
        )
    except ClientError as exc:
        if _is_precondition_failed(exc):
            raise MaterialObjectChangedError(
                f"Stored object changed after registration: {s3_key!r}"
            ) from exc
        raise
    body = response["Body"]
    try:
        with open(destination, "wb") as out:
            shutil.copyfileobj(body, out, _HASH_CHUNK_SIZE)
    finally:
        body.close()
    return destination


def get_material_object_info(s3_key: str) -> StoredObject:
    """Return the stored object's size and ETag (``HEAD``; no body is read).

    A missing object raises the boto3 404 ``ClientError``.
    """
    client = _s3_client()
    head = client.head_object(Bucket=settings.s3_bucket_name, Key=s3_key)
    return StoredObject(size=int(head["ContentLength"]), etag=head["ETag"])


def compute_material_sha256(s3_key: str, expected_etag: str | None = None) -> str:
    """Stream the stored object in chunks and return its SHA-256 hex digest.

    A missing object raises the boto3 ``NoSuchKey``/404 client error. When
    ``expected_etag`` is given the read uses ``If-Match``, so the digest is
    guaranteed to describe exactly that object version; a replaced object
    raises :class:`MaterialObjectChangedError`.
    """
    client = _s3_client()
    kwargs = {"IfMatch": expected_etag} if expected_etag else {}
    try:
        response = client.get_object(
            Bucket=settings.s3_bucket_name, Key=s3_key, **kwargs
        )
    except ClientError as exc:
        if expected_etag and _is_precondition_failed(exc):
            raise MaterialObjectChangedError(
                f"Stored object changed while hashing: {s3_key!r}"
            ) from exc
        raise
    digest = hashlib.sha256()
    body = response["Body"]
    try:
        while True:
            chunk = body.read(_HASH_CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
    finally:
        body.close()
    return digest.hexdigest()


def delete_material_object(s3_key: str) -> None:
    """Delete the stored object at ``s3_key`` (Week 9 duplicate cleanup)."""
    client = _s3_client()
    client.delete_object(Bucket=settings.s3_bucket_name, Key=s3_key)


def delete_material_objects(s3_keys: list[str]) -> list[str]:
    """Delete many stored objects; return the keys that could not be deleted.

    Used when a course is deleted. Missing keys are not errors in S3.
    """
    client = _s3_client()
    failed: list[str] = []
    for start in range(0, len(s3_keys), _DELETE_BATCH_SIZE):
        batch = s3_keys[start : start + _DELETE_BATCH_SIZE]
        response = client.delete_objects(
            Bucket=settings.s3_bucket_name,
            Delete={"Objects": [{"Key": key} for key in batch], "Quiet": True},
        )
        failed.extend(item["Key"] for item in response.get("Errors", []))
    return failed
