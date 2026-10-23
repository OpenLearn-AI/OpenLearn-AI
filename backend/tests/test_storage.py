"""Unit tests for the S3 storage helper and material S3 key helpers."""

import hashlib
import io
import uuid

import pytest

from app.config import settings
from app.services import material_service, storage


class FakeS3Client:
    def __init__(self):
        self.generate_presigned_post_calls = []

    def generate_presigned_post(self, Bucket, Key, Conditions, ExpiresIn):
        self.generate_presigned_post_calls.append(
            {
                "Bucket": Bucket,
                "Key": Key,
                "Conditions": list(Conditions),
                "ExpiresIn": ExpiresIn,
            }
        )
        return {
            "url": "https://storage.example/bucket",
            "fields": {"key": Key, "policy": "signed-policy"},
        }


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


def test_generate_upload_post_uses_configured_storage_settings(fake_boto3):
    course_id = uuid.uuid4()
    object_key = f"courses/{course_id}/materials/abc.pdf"

    upload = storage.generate_upload_post(object_key)

    assert upload["url"] == "https://storage.example/bucket"
    assert upload["fields"]["key"] == object_key

    # Contract assertions (not exact-kwargs equality): the client must be
    # built from deployment configuration with SigV4 forced.
    kwargs = fake_boto3.client_kwargs
    assert kwargs["endpoint_url"] == settings.s3_endpoint_url
    assert kwargs["aws_access_key_id"] == settings.s3_access_key_id
    assert kwargs["aws_secret_access_key"] == settings.s3_secret_access_key
    assert kwargs["region_name"] == settings.s3_region_name
    config = kwargs.get("config")
    assert config is not None
    assert "s3v4" in str(getattr(config, "signature_version", ""))

    call = fake_boto3.s3_client.generate_presigned_post_calls[0]
    assert call["Bucket"] == settings.s3_bucket_name
    assert call["Key"] == object_key
    assert call["ExpiresIn"] == settings.s3_url_expiration_seconds


def test_upload_post_policy_caps_size_at_ten_mib(fake_boto3):
    """B-02: the signed policy rejects files over 10 MiB (and empty files)."""
    storage.generate_upload_post(f"courses/{uuid.uuid4()}/materials/abc.pdf")

    call = fake_boto3.s3_client.generate_presigned_post_calls[0]
    assert ["content-length-range", 1, 10 * 1024 * 1024] in call["Conditions"]
    assert settings.max_upload_size_bytes == 10 * 1024 * 1024


def test_upload_post_policy_is_signed_by_real_boto3(monkeypatch):
    """The real boto3 signer (local, no network) embeds the size condition."""
    import base64
    import json

    monkeypatch.setattr(settings, "s3_access_key_id", "test-access-key")
    monkeypatch.setattr(settings, "s3_secret_access_key", "test-secret-key")

    upload = storage.generate_upload_post(f"courses/{uuid.uuid4()}/materials/a.pdf")

    policy = json.loads(base64.b64decode(upload["fields"]["policy"]))
    assert ["content-length-range", 1, settings.max_upload_size_bytes] in policy[
        "conditions"
    ]


def test_upload_url_has_finite_expiration_and_short_default(fake_boto3):
    storage.generate_upload_post(f"courses/{uuid.uuid4()}/materials/abc.pdf")

    expires_in = fake_boto3.s3_client.generate_presigned_post_calls[0]["ExpiresIn"]
    assert isinstance(expires_in, int)
    assert expires_in > 0
    # P-01: the default lifetime is short (15 minutes), independent of any
    # developer-local override in backend/.env.
    from app.config import Settings

    assert Settings.model_fields["s3_url_expiration_seconds"].default == 900


# ---------------------------------------------------------------------------
# Week 9 — content hashing (streaming) and duplicate-object deletion
# ---------------------------------------------------------------------------


class ChunkedBody:
    """File-like body that serves content in small reads, mimicking botocore's
    StreamingBody behavior on top of an in-memory payload."""

    def __init__(self, content: bytes, read_size: int, fail_reads: bool = False):
        self._stream = io.BytesIO(content)
        self._read_size = read_size
        self._fail_reads = fail_reads
        self.closed = False

    def read(self, amt=-1):
        if self._fail_reads:
            raise RuntimeError("storage read failed")
        if amt is None or amt < 0:
            return self._stream.read()
        return self._stream.read(min(amt, self._read_size))

    def close(self):
        self.closed = True


class HashingFakeS3Client(FakeS3Client):
    def __init__(self):
        super().__init__()
        self.objects: dict[str, bytes] = {}
        self.get_object_calls: list[str] = []
        self.delete_calls: list[tuple[str, str]] = []
        self.fail_reads = False
        self.last_body: ChunkedBody | None = None

    def get_object(self, Bucket, Key):
        self.get_object_calls.append(Key)
        assert Bucket == settings.s3_bucket_name
        body = ChunkedBody(self.objects[Key], read_size=7, fail_reads=self.fail_reads)
        self.last_body = body
        return {"Body": body}

    def delete_object(self, Bucket, Key):
        assert Bucket == settings.s3_bucket_name
        self.delete_calls.append((Bucket, Key))


@pytest.fixture
def hashing_fake_boto3(monkeypatch):
    fake = FakeBoto3()
    fake.s3_client = HashingFakeS3Client()
    monkeypatch.setattr(storage, "boto3", fake)
    return fake


def test_compute_material_sha256_matches_hashlib_in_chunks(hashing_fake_boto3):
    """The Week 9 hash is the plain SHA-256 hex digest of the stored object's
    content, read in bounded chunks (the fake body serves 7-byte reads, so a
    correct implementation cannot depend on whole-body reads)."""
    content = b"x" * 5 + b"openlearn content payload " + bytes(range(256))
    object_key = f"courses/{uuid.uuid4()}/materials/lecture.pdf"
    hashing_fake_boto3.s3_client.objects[object_key] = content

    digest = storage.compute_material_sha256(object_key)

    assert digest == hashlib.sha256(content).hexdigest()
    assert hashing_fake_boto3.s3_client.get_object_calls == [object_key]


def test_compute_material_sha256_empty_object(hashing_fake_boto3):
    object_key = f"courses/{uuid.uuid4()}/materials/empty.pdf"
    hashing_fake_boto3.s3_client.objects[object_key] = b""

    assert storage.compute_material_sha256(object_key) == hashlib.sha256(b"").hexdigest()


def test_compute_material_sha256_closes_the_body(hashing_fake_boto3):
    """The streamed body must be closed deterministically, including when the
    storage stream errors mid-read."""
    object_key = f"courses/{uuid.uuid4()}/materials/lecture.pdf"
    hashing_fake_boto3.s3_client.objects[object_key] = b"payload"
    client = hashing_fake_boto3.s3_client

    storage.compute_material_sha256(object_key)

    assert client.last_body is not None
    assert client.last_body.closed is True


def test_compute_material_sha256_closes_body_on_read_error(hashing_fake_boto3):
    object_key = f"courses/{uuid.uuid4()}/materials/lecture.pdf"
    hashing_fake_boto3.s3_client.objects[object_key] = b"payload"
    hashing_fake_boto3.s3_client.fail_reads = True

    with pytest.raises(RuntimeError, match="storage read failed"):
        storage.compute_material_sha256(object_key)

    assert hashing_fake_boto3.s3_client.last_body.closed is True


def test_delete_material_object_uses_configured_bucket(hashing_fake_boto3):
    object_key = f"courses/{uuid.uuid4()}/materials/duplicate.pdf"

    storage.delete_material_object(object_key)

    assert hashing_fake_boto3.s3_client.delete_calls == [
        (settings.s3_bucket_name, object_key)
    ]


# ---------------------------------------------------------------------------
# Review fixes — size/ETag inspection, If-Match reads, bulk delete
# ---------------------------------------------------------------------------


class EtagFakeS3Client(HashingFakeS3Client):
    """Adds HEAD, If-Match semantics and DeleteObjects to the hashing fake."""

    def __init__(self):
        super().__init__()
        self.etags: dict[str, str] = {}
        self.if_match_calls: list[str | None] = []
        self.delete_objects_calls: list[list[str]] = []
        self.delete_errors: list[dict] = []

    def head_object(self, Bucket, Key):
        return {"ContentLength": len(self.objects[Key]), "ETag": self.etags[Key]}

    def get_object(self, Bucket, Key, IfMatch=None):
        from botocore.exceptions import ClientError

        self.if_match_calls.append(IfMatch)
        if IfMatch is not None and IfMatch != self.etags[Key]:
            raise ClientError(
                {
                    "Error": {"Code": "PreconditionFailed", "Message": "x"},
                    "ResponseMetadata": {"HTTPStatusCode": 412},
                },
                "GetObject",
            )
        return super().get_object(Bucket, Key)

    def delete_objects(self, Bucket, Delete):
        assert Bucket == settings.s3_bucket_name
        self.delete_objects_calls.append([o["Key"] for o in Delete["Objects"]])
        return {"Errors": list(self.delete_errors)} if self.delete_errors else {}


@pytest.fixture
def etag_boto3(monkeypatch):
    fake = FakeBoto3()
    fake.s3_client = EtagFakeS3Client()
    monkeypatch.setattr(storage, "boto3", fake)
    return fake


def test_get_material_object_info_returns_size_and_etag(etag_boto3):
    key = f"courses/{uuid.uuid4()}/materials/a.pdf"
    etag_boto3.s3_client.objects[key] = b"12345"
    etag_boto3.s3_client.etags[key] = '"abc"'

    info = storage.get_material_object_info(key)

    assert info.size == 5
    assert info.etag == '"abc"'


def test_sha256_reads_with_if_match_and_matches_when_unchanged(etag_boto3):
    key = f"courses/{uuid.uuid4()}/materials/a.pdf"
    etag_boto3.s3_client.objects[key] = b"payload"
    etag_boto3.s3_client.etags[key] = '"v1"'

    digest = storage.compute_material_sha256(key, expected_etag='"v1"')

    assert digest == hashlib.sha256(b"payload").hexdigest()
    assert etag_boto3.s3_client.if_match_calls == ['"v1"']


def test_sha256_raises_when_object_changed(etag_boto3):
    key = f"courses/{uuid.uuid4()}/materials/a.pdf"
    etag_boto3.s3_client.objects[key] = b"payload"
    etag_boto3.s3_client.etags[key] = '"v2"'

    with pytest.raises(storage.MaterialObjectChangedError):
        storage.compute_material_sha256(key, expected_etag='"v1"')


def test_download_with_etag_writes_file_and_rejects_changed_object(
    etag_boto3, tmp_path
):
    key = f"courses/{uuid.uuid4()}/materials/lecture.pdf"
    etag_boto3.s3_client.objects[key] = b"file-bytes"
    etag_boto3.s3_client.etags[key] = '"v1"'

    path = storage.download_material_to_temp(key, tmp_path, expected_etag='"v1"')
    assert path.read_bytes() == b"file-bytes"
    assert etag_boto3.s3_client.last_body.closed is True

    etag_boto3.s3_client.etags[key] = '"replaced"'
    with pytest.raises(storage.MaterialObjectChangedError):
        storage.download_material_to_temp(key, tmp_path, expected_etag='"v1"')


def test_delete_material_objects_batches_and_reports_failures(etag_boto3):
    keys = [f"courses/c/materials/{i}.pdf" for i in range(1001)]
    etag_boto3.s3_client.delete_errors = [{"Key": keys[3], "Code": "AccessDenied"}]

    failed = storage.delete_material_objects(keys)

    calls = etag_boto3.s3_client.delete_objects_calls
    assert [len(c) for c in calls] == [1000, 1]
    assert failed == [keys[3], keys[3]]
