"""S3-compatible (MinIO) object-storage helper for course materials.

Week 6 scope is presigned upload URLs only: FastAPI never proxies the file
bytes. Week 8 (B5) adds the worker-side fetch helper agreed with the Backend
pod (handoff H2): ``download_material_to_temp`` downloads a stored material
object into a caller-owned temporary directory. Credentials come exclusively
from deployment configuration (``config``), never from source code.
"""

from pathlib import Path, PurePosixPath

import boto3
from botocore.config import Config

from app.config import settings


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


def generate_upload_url(object_key: str) -> str:
    """Return a time-limited presigned PUT URL for ``object_key``.

    The client uploads the file directly to storage; nothing is proxied by the
    backend.
    """
    client = _s3_client()
    return client.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": settings.s3_bucket_name,
            "Key": object_key,
        },
        ExpiresIn=settings.s3_url_expiration_seconds,
    )


def download_material_to_temp(s3_key: str, destination_dir: str | Path) -> Path:
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
    """
    filename = PurePosixPath(s3_key).name
    if not filename or filename in {".", ".."}:
        raise ValueError(f"Invalid material S3 key: {s3_key!r}")
    destination = Path(destination_dir) / filename
    client = _s3_client()
    client.download_file(settings.s3_bucket_name, s3_key, str(destination))
    return destination
