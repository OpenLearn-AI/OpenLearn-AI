"""Unit tests for the S3 storage helper and material S3 key helpers."""

import uuid

import pytest

from app.config import settings
from app.services import material_service, storage


class FakeS3Client:
    def __init__(self):
        self.generate_presigned_url_calls = []

    def generate_presigned_url(self, ClientMethod, Params, ExpiresIn):
        self.generate_presigned_url_calls.append(
            (ClientMethod, dict(Params), ExpiresIn)
        )
        return "https://storage.example/presigned-upload-url"


class FakeBoto3:
    def __init__(self):
        self.client_kwargs = None
        self.s3_client = FakeS3Client()

    def client(self, service_name, **kwargs):
        assert service_name == "s3"
        self.client_kwargs = kwargs
        return self.s3_client


@pytest.fixture
def fake_boto3(monkeypatch):
    fake = FakeBoto3()
    monkeypatch.setattr(storage, "boto3", fake)
    return fake


def test_material_key_prefix_identifies_own_namespace():
    course_id = uuid.uuid4()
    prefix = material_service.material_key_prefix(course_id)
    own = f"{prefix}abc-123.pdf"
    foreign = f"courses/{uuid.uuid4()}/materials/abc-123.pdf"
    other = "not/a/material/key"

    assert material_service.is_material_s3_key_for_course(course_id, own)
    assert not material_service.is_material_s3_key_for_course(course_id, foreign)
    assert not material_service.is_material_s3_key_for_course(course_id, other)
    assert not material_service.is_material_s3_key_for_course(course_id, prefix)


def test_material_key_is_generated_server_side_and_unique():
    course_id = uuid.uuid4()
    first = material_service.build_material_s3_key(course_id, "report.pdf")
    second = material_service.build_material_s3_key(course_id, "report.pdf")

    assert first != second
    assert first.startswith(f"courses/{course_id}/materials/")
    assert second.startswith(f"courses/{course_id}/materials/")


def test_material_key_sanitizes_client_filename():
    course_id = uuid.uuid4()
    key = material_service.build_material_s3_key(
        course_id,
        "../../etc/passwd?x=1 FILENAME.pdf",
    )

    assert key.startswith(f"courses/{course_id}/materials/")
    assert key.endswith("-passwd_x_1_FILENAME.pdf")
    assert ".." not in key
    assert "?" not in key


def test_material_key_falls_back_when_filename_empty():
    course_id = uuid.uuid4()
    key = material_service.build_material_s3_key(course_id, "...")

    assert key.startswith(f"courses/{course_id}/materials/")
    assert key.endswith("-upload")


def test_generate_upload_url_uses_configured_storage_settings(fake_boto3):
    course_id = uuid.uuid4()
    object_key = f"courses/{course_id}/materials/abc.pdf"

    url = storage.generate_upload_url(object_key)

    assert url == "https://storage.example/presigned-upload-url"
    assert fake_boto3.client_kwargs == {
        "endpoint_url": settings.s3_endpoint_url,
        "aws_access_key_id": settings.s3_access_key_id,
        "aws_secret_access_key": settings.s3_secret_access_key,
        "region_name": settings.s3_region_name,
    }

    method, params, expires_in = fake_boto3.s3_client.generate_presigned_url_calls[0]
    assert method == "put_object"
    assert params == {
        "Bucket": settings.s3_bucket_name,
        "Key": object_key,
    }
    assert expires_in == settings.s3_url_expiration_seconds


def test_presigned_url_has_finite_expiration(fake_boto3):
    course_id = uuid.uuid4()
    object_key = f"courses/{course_id}/materials/abc.pdf"

    storage.generate_upload_url(object_key)

    _, _, expires_in = fake_boto3.s3_client.generate_presigned_url_calls[0]
    assert isinstance(expires_in, int)
    assert expires_in > 0