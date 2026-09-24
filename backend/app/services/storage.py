"""S3-compatible (MinIO) object-storage helper for course materials.

Week 6 scope is presigned upload URLs only: FastAPI never proxies the file
bytes. Credentials come exclusively from deployment configuration (``config``),
never from source code.
"""

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

