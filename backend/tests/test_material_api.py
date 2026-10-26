"""Phase 6 tests for the material upload pipeline (/v1/courses/{id}/materials/*).

Uses the established authenticated-endpoint harness (fake JWKS + overridden DB
session) and a fake boto3 so no real MinIO/S3 instance is required. Tests
verify behavior, not storage internals.

Week 9 additions: the fake S3 client also serves ``get_object`` (registration
hashes the stored object for content deduplication) and records
``delete_object`` calls (verified-duplicate cleanup), and the registration
tests cover the course-scoped deduplication and duplicate-failed retry paths.
"""
import hashlib
import io
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from botocore.exceptions import ClientError
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.db.session import get_db
from app.main import app
from app.models.course import Course
from app.models.material import (
    FAILED_STATUS,
    PENDING_STATUS,
    PROCESSING_STATUS,
    READY_STATUS,
    Material,
)
from app.models.user import User
from app.schemas.material import MaterialResponse, MaterialStatusResponse
from app.services import material_service, storage
from conftest import _create_material, _create_user

ISSUER = settings.keycloak_issuer
AUDIENCE = settings.keycloak_audience


class FakeS3Client:
    DEFAULT_PAYLOAD = b"fake-material-bytes"

    def __init__(self):
        self.calls = []
        # Stored objects by key (Week 9): served by ``get_object`` for the
        # registration hash; unknown keys hash the default payload so tests
        # only seed content when a deduplication decision depends on it.
        self.objects: dict[str, bytes] = {}
        self.missing_keys: set[str] = set()
        self.deleted_keys: list[str] = []
        # Per-key overrides: ETag returned by HEAD/GET, and reported size.
        self.etags: dict[str, str] = {}
        self.sizes: dict[str, int] = {}

    def generate_presigned_post(self, Bucket, Key, Conditions, ExpiresIn):
        self.calls.append(
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

    def _missing_error(self, operation):
        return ClientError(
            {
                "Error": {
                    "Code": "NoSuchKey",
                    "Message": "The specified key does not exist.",
                },
                "ResponseMetadata": {"HTTPStatusCode": 404},
            },
            operation,
        )

    def etag_for(self, Key):
        return self.etags.get(Key, '"default-etag"')

    def head_object(self, Bucket, Key):
        # Unknown keys serve the default payload: from the storage's point of
        # view the presigned upload happened. The missing-object case is
        # armed explicitly by the tests that need it.
        if self.missing_keys and Key in self.missing_keys:
            raise self._missing_error("HeadObject")
        payload = self.objects.get(Key, self.DEFAULT_PAYLOAD)
        return {
            "ContentLength": self.sizes.get(Key, len(payload)),
            "ETag": self.etag_for(Key),
        }

    def get_object(self, Bucket, Key, IfMatch=None):
        if self.missing_keys and Key in self.missing_keys:
            raise self._missing_error("GetObject")
        if IfMatch is not None and IfMatch != self.etag_for(Key):
            raise ClientError(
                {
                    "Error": {"Code": "PreconditionFailed", "Message": "x"},
                    "ResponseMetadata": {"HTTPStatusCode": 412},
                },
                "GetObject",
            )
        return {"Body": io.BytesIO(self.objects.get(Key, self.DEFAULT_PAYLOAD))}

    def delete_object(self, Bucket, Key):
        self.deleted_keys.append(Key)
        self.objects.pop(Key, None)

    def delete_objects(self, Bucket, Delete):
        for item in Delete["Objects"]:
            self.deleted_keys.append(item["Key"])
            self.objects.pop(item["Key"], None)
        return {}


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


@pytest.fixture
def fake_publisher(monkeypatch):
    """Fake the Week 7 Celery publisher: no Redis/REDIS_PASSWORD required.

    Records the exact arguments received and returns a deterministic job id so
    tests can assert the full registration -> enqueue -> 202 contract.
    """
    calls = []

    async def fake_enqueue_material_processing(
        material_id: uuid.UUID,
        s3_key: str,
        course_id: uuid.UUID,
        owner_id: uuid.UUID,
    ) -> str:
        calls.append(
            {
                "material_id": material_id,
                "s3_key": s3_key,
                "course_id": course_id,
                "owner_id": owner_id,
            }
        )
        return "test-job-id"

    monkeypatch.setattr(
        "app.api.materials.enqueue_material_processing",
        fake_enqueue_material_processing,
    )
    return calls


def _build_token(private_key: str, *, sub: str, roles: list[str]) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": sub,
        "iss": ISSUER,
        "aud": AUDIENCE,
        "iat": now,
        "exp": now + timedelta(minutes=15),
        "email": "user@openlearn.dev",
        "realm_access": {"roles": roles},
    }

    return jwt.encode(payload, private_key, algorithm="RS256")


async def _create_course(
    db,
    owner: User,
    title: str = "Test Course",
    description: str = "Learn things",
) -> Course:
    course = Course(
        owner_id=owner.id,
        title=title,
        description=description,
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


@asynccontextmanager
async def _api(db_session, token: str | None = None):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            yield client, headers
    finally:
        app.dependency_overrides.clear()


def _upload_url_payload(**overrides) -> dict:
    payload = {
        "title": "Lecture 1",
        "filename": "lecture-1.pdf",
    }
    payload.update(overrides)
    return payload


async def _process(
    db_session, token: str, material_id: uuid.UUID, raise_app_exceptions=True
):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    headers = {"Authorization": f"Bearer {token}"}

    try:
        transport = ASGITransport(app=app, raise_app_exceptions=raise_app_exceptions)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post(
                f"/v1/materials/{material_id}/process",
                headers=headers,
            )
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_owner_instructor_can_request_upload_url(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_boto3,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-owner-subject",
        "material-owner@example.com",
    )
    course = await _create_course(db_session, instructor)
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.post(
            f"/v1/courses/{course.id}/materials/upload-url",
            json=_upload_url_payload(),
            headers=headers,
        )

    assert response.status_code == 200

    body = response.json()

    assert body["course_id"] == str(course.id)
    assert body["title"] == "Lecture 1"
    assert body["upload_url"] == "https://storage.example/bucket"
    assert body["upload_fields"]["key"] == body["s3_key"]
    assert body["max_size_bytes"] == 10 * 1024 * 1024
    assert body["s3_key"].startswith(f"courses/{course.id}/materials/")
    assert isinstance(body["expires_in"], int)
    assert body["expires_in"] > 0

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_upload_url_uses_configured_storage_settings(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_boto3,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-settings-subject",
        "material-settings@example.com",
    )
    course = await _create_course(db_session, instructor)
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.post(
            f"/v1/courses/{course.id}/materials/upload-url",
            json=_upload_url_payload(),
            headers=headers,
        )

    assert response.status_code == 200

    # Contract assertions (not exact-kwargs equality): the client must be
    # built from deployment configuration with SigV4 forced. SigV2 presigned
    # URLs cover the Content-Type header, which breaks real browser uploads.
    kwargs = fake_boto3.client_kwargs
    assert kwargs["endpoint_url"] == settings.s3_endpoint_url
    assert kwargs["aws_access_key_id"] == settings.s3_access_key_id
    assert kwargs["aws_secret_access_key"] == settings.s3_secret_access_key
    assert kwargs["region_name"] == settings.s3_region_name
    config = kwargs.get("config")
    assert config is not None
    assert "s3v4" in str(getattr(config, "signature_version", ""))

    call = fake_boto3.s3_client.calls[0]
    assert call["Bucket"] == settings.s3_bucket_name
    assert call["Key"] == response.json()["s3_key"]
    assert call["ExpiresIn"] == settings.s3_url_expiration_seconds
    assert ["content-length-range", 1, settings.max_upload_size_bytes] in call[
        "Conditions"
    ]

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_non_owner_instructor_cannot_request_upload_url(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_boto3,
):
    private_key, _ = rsa_keypair
    owner = await _create_user(
        db_session,
        "material-nonowner-owner-subject",
        "material-nonowner-owner@example.com",
    )
    intruder = await _create_user(
        db_session,
        "material-nonowner-intruder-subject",
        "material-nonowner-intruder@example.com",
    )
    course = await _create_course(db_session, owner)

    token = _build_token(private_key, sub=intruder.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.post(
            f"/v1/courses/{course.id}/materials/upload-url",
            json=_upload_url_payload(),
            headers=headers,
        )

    assert response.status_code == 403
    assert fake_boto3.s3_client.calls == []

    await db_session.delete(owner)
    await db_session.delete(intruder)
    await db_session.commit()


@pytest.mark.asyncio
async def test_student_cannot_request_upload_url(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_boto3,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-student-owner-subject",
        "material-student-owner@example.com",
    )
    course = await _create_course(db_session, instructor)

    student = await _create_user(
        db_session,
        "material-student-subject",
        "material-student@example.com",
    )
    token = _build_token(private_key, sub=student.keycloak_subject, roles=["student"])

    async with _api(db_session, token) as (client, headers):
        response = await client.post(
            f"/v1/courses/{course.id}/materials/upload-url",
            json=_upload_url_payload(),
            headers=headers,
        )

    assert response.status_code == 403
    assert fake_boto3.s3_client.calls == []

    await db_session.delete(instructor)
    await db_session.delete(student)
    await db_session.commit()


@pytest.mark.asyncio
async def test_upload_url_unauthenticated_returns_401(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    async with _api(db_session) as (client, _headers):
        response = await client.post(
            f"/v1/courses/{uuid.uuid4()}/materials/upload-url",
            json=_upload_url_payload(),
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_url_nonexistent_course_returns_404(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-missing-course-subject",
        "material-missing-course@example.com",
    )
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.post(
            f"/v1/courses/{uuid.uuid4()}/materials/upload-url",
            json=_upload_url_payload(),
            headers=headers,
        )

    assert response.status_code == 404

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_upload_url_rejects_client_supplied_s3_key_and_fields(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    """The client can never choose the object key; it is generated server-side."""
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-nokey-subject",
        "material-nokey@example.com",
    )
    course = await _create_course(db_session, instructor)
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.post(
            f"/v1/courses/{course.id}/materials/upload-url",
            json=_upload_url_payload(s3_key="client-picked-key"),
            headers=headers,
        )

    assert response.status_code == 422

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_upload_url_sanitizes_client_filename(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_boto3,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-sanitize-subject",
        "material-sanitize@example.com",
    )
    course = await _create_course(db_session, instructor)
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.post(
            f"/v1/courses/{course.id}/materials/upload-url",
            json=_upload_url_payload(filename="../../etc/passwd?x=1 evil.pdf"),
            headers=headers,
        )

    assert response.status_code == 200

    s3_key = response.json()["s3_key"]
    assert s3_key.startswith(f"courses/{course.id}/materials/")
    assert ".." not in s3_key
    assert "?" not in s3_key
    assert s3_key.endswith("-passwd_x_1_evil.pdf")

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_register_material_creates_pending_row_and_enqueues_processing(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_boto3,
    fake_publisher,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-register-subject",
        "material-register@example.com",
    )
    course = await _create_course(db_session, instructor)
    s3_key = material_service.build_material_s3_key(course.id, "slides.pdf")

    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.post(
            f"/v1/courses/{course.id}/materials",
            json={"title": "Slides", "s3_key": s3_key},
            headers=headers,
        )

    assert response.status_code == 202

    body = response.json()
    assert body["job_id"] == "test-job-id"

    result = await db_session.execute(
        select(Material).where(Material.id == uuid.UUID(body["material_id"]))
    )
    stored = result.scalar_one()
    assert body["material_id"] == str(stored.id)
    assert stored.course_id == course.id
    assert stored.uploaded_by == instructor.id
    assert stored.status == "pending"

    assert fake_publisher == [
        {
            "material_id": stored.id,
            "s3_key": stored.s3_key,
            "course_id": stored.course_id,
            "owner_id": stored.uploaded_by,
        }
    ]

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_register_material_publish_failure_returns_500_and_leaves_pending(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_boto3,
    monkeypatch,
):
    """F8 pin: commit-before-publish.

    The material is committed ``pending`` by ``create_material`` before the
    Celery publish is attempted. If the publish raises, the request returns 500,
    no job_id is produced, and the committed ``pending`` row remains. A task
    may still have been accepted by the broker (at-least-once tail); this test
    does not assert either way.
    """
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-enqueue-fail-subject",
        "material-enqueue-fail@example.com",
    )
    course = await _create_course(db_session, instructor)
    s3_key = material_service.build_material_s3_key(course.id, "slides.pdf")

    captured: dict[str, uuid.UUID] = {}

    async def failing_enqueue(
        material_id: uuid.UUID,
        s3_key: str,
        course_id: uuid.UUID,
        owner_id: uuid.UUID,
    ):
        captured["material_id"] = material_id
        raise RuntimeError("broker unavailable")

    monkeypatch.setattr(
        "app.api.materials.enqueue_material_processing",
        failing_enqueue,
    )

    token = _build_token(
        private_key,
        sub=instructor.keycloak_subject,
        roles=["instructor"],
    )

    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            f"/v1/courses/{course.id}/materials",
            json={"title": "Slides", "s3_key": s3_key},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 500
    assert "job_id" not in response.text

    material_id = captured["material_id"]

    engine = create_async_engine(settings.database_url)
    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    try:
        async with factory() as fresh_session:
            result = await fresh_session.execute(
                select(Material).where(Material.id == material_id)
            )
            stored = result.scalar_one()
            assert stored.status == PENDING_STATUS
            assert stored.course_id == course.id
            assert stored.s3_key == s3_key
    finally:
        await engine.dispose()

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_register_material_rejects_client_uploaded_by(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-spoof-uploader-subject",
        "material-spoof-uploader@example.com",
    )
    course = await _create_course(db_session, instructor)
    s3_key = material_service.build_material_s3_key(course.id, "slides.pdf")

    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.post(
            f"/v1/courses/{course.id}/materials",
            json={
                "title": "Slides",
                "s3_key": s3_key,
                "uploaded_by": str(uuid.uuid4()),
            },
            headers=headers,
        )

    assert response.status_code == 422

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_register_material_key_must_belong_to_route_course(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_boto3,
):
    """course_id comes from the route; an s3_key minted for another course (or
    any arbitrary path) must be rejected."""
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-routecourse-subject",
        "material-routecourse@example.com",
    )
    other = await _create_user(
        db_session,
        "material-routecourse-other-subject",
        "material-routecourse-other@example.com",
    )
    course = await _create_course(db_session, instructor, title="A")
    other_course = await _create_course(db_session, other, title="B")

    foreign_key = material_service.build_material_s3_key(other_course.id, "slides.pdf")
    arbitrary_key = "not/a/material/key"

    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        for bad_key in (foreign_key, arbitrary_key):
            response = await client.post(
                f"/v1/courses/{course.id}/materials",
                json={"title": "Slides", "s3_key": bad_key},
                headers=headers,
            )
            assert response.status_code == 422

    await db_session.delete(instructor)
    await db_session.delete(other)
    await db_session.commit()


@pytest.mark.asyncio
async def test_register_material_same_key_twice_reuses_canonical(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_boto3,
    fake_publisher,
):
    """Week 9: the same s3_key holds the same object, so a second
    registration is a content duplicate and reuses the canonical material —
    no second row, no second job, and the canonical object itself is never
    deleted (the duplicate-object guard rejects the identical key)."""
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-duplicate-subject",
        "material-duplicate@example.com",
    )
    course = await _create_course(db_session, instructor)
    s3_key = material_service.build_material_s3_key(course.id, "slides.pdf")

    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        first = await client.post(
            f"/v1/courses/{course.id}/materials",
            json={"title": "Slides", "s3_key": s3_key},
            headers=headers,
        )
        second = await client.post(
            f"/v1/courses/{course.id}/materials",
            json={"title": "Slides again", "s3_key": s3_key},
            headers=headers,
        )

    assert first.status_code == 202
    assert second.status_code == 202

    first_body = first.json()
    second_body = second.json()
    assert second_body["material_id"] == first_body["material_id"]
    assert first_body["job_id"] == "test-job-id"
    assert second_body["job_id"] is None
    assert second_body["status"] == PENDING_STATUS

    assert len(fake_publisher) == 1
    assert fake_boto3.s3_client.deleted_keys == []

    result = await db_session.execute(
        select(Material).where(Material.id == uuid.UUID(first_body["material_id"]))
    )
    stored = result.scalar_one()
    assert stored.sha256 is not None
    assert stored.sha256 == hashlib.sha256(FakeS3Client.DEFAULT_PAYLOAD).hexdigest()

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_register_material_concurrent_duplicate_returns_winner(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_boto3,
    fake_publisher,
    monkeypatch,
):
    """Week 9: when a concurrent registration of the same content wins the
    (course_id, sha256) insert race, the loser gets the winner back (202,
    no job) instead of a 409, and its orphan object is deleted."""
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-duplicate-race-subject",
        "material-duplicate-race@example.com",
    )
    course = await _create_course(db_session, instructor)
    content = b"same lecture pdf"
    first_key = material_service.build_material_s3_key(course.id, "slides.pdf")
    second_key = material_service.build_material_s3_key(course.id, "slides-copy.pdf")
    fake_boto3.s3_client.objects[first_key] = content
    fake_boto3.s3_client.objects[second_key] = content

    # Simulate the race: both pre-insert lookups miss; only the lookup in
    # the IntegrityError handler sees the committed winner.
    real_lookup = material_service.find_material_by_content_hash
    calls = {"n": 0}

    async def racing_lookup(db, course_id, sha256):
        calls["n"] += 1
        if calls["n"] <= 2:
            return None
        return await real_lookup(db, course_id, sha256)

    monkeypatch.setattr(
        "app.api.materials.find_material_by_content_hash", racing_lookup
    )

    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        first = await client.post(
            f"/v1/courses/{course.id}/materials",
            json={"title": "Slides", "s3_key": first_key},
            headers=headers,
        )
        second = await client.post(
            f"/v1/courses/{course.id}/materials",
            json={"title": "Slides again", "s3_key": second_key},
            headers=headers,
        )

    assert first.status_code == 202
    assert second.status_code == 202
    assert second.json()["material_id"] == first.json()["material_id"]
    assert second.json()["job_id"] is None
    assert len(fake_publisher) == 1
    assert fake_boto3.s3_client.deleted_keys == [second_key]

    await db_session.delete(instructor)
    await db_session.commit()


# ---------------------------------------------------------------------------
# Week 9 — course-scoped SHA-256 deduplication on registration
# ---------------------------------------------------------------------------


async def _register(db_session, token: str, course_id: uuid.UUID, s3_key: str, title="Slides", raise_app_exceptions=True):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    headers = {"Authorization": f"Bearer {token}"}

    try:
        transport = ASGITransport(app=app, raise_app_exceptions=raise_app_exceptions)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post(
                f"/v1/courses/{course_id}/materials",
                json={"title": title, "s3_key": s3_key},
                headers=headers,
            )
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_register_material_missing_object_returns_404(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_boto3,
    fake_publisher,
):
    """Week 9 registration hashes the stored object; when no object was
    uploaded for the s3_key the registration cannot proceed and reports 404."""
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-missing-object-subject",
        "material-missing-object@example.com",
    )
    course = await _create_course(db_session, instructor)
    s3_key = material_service.build_material_s3_key(course.id, "slides.pdf")
    fake_boto3.s3_client.missing_keys.add(s3_key)

    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])
    response = await _register(db_session, token, course.id, s3_key)

    assert response.status_code == 404
    assert fake_publisher == []

    result = await db_session.execute(
        select(Material).where(Material.course_id == course.id)
    )
    assert result.scalars().all() == []

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize("canonical_status", [READY_STATUS, PENDING_STATUS, PROCESSING_STATUS])
async def test_register_material_duplicate_of_active_status_reuses_canonical(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_boto3,
    fake_publisher,
    canonical_status,
):
    """Week 9: a duplicate of a ready/pending/processing material returns the
    canonical material ID without enqueueing another job, and the freshly
    uploaded duplicate object is deleted after verification."""
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        f"material-dedup-{canonical_status}-subject",
        f"material-dedup-{canonical_status}@example.com",
    )
    course = await _create_course(db_session, instructor)
    content = b"identical lecture pdf"
    canonical = await _create_material(
        db_session, course, instructor,
        status=canonical_status,
        sha256=hashlib.sha256(content).hexdigest(),
    )
    duplicate_key = material_service.build_material_s3_key(course.id, "slides-copy.pdf")
    fake_boto3.s3_client.objects[duplicate_key] = content

    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])
    response = await _register(db_session, token, course.id, duplicate_key)

    assert response.status_code == 202
    body = response.json()
    assert body["material_id"] == str(canonical.id)
    assert body["job_id"] is None
    assert body["status"] == canonical_status

    assert fake_publisher == []
    assert fake_boto3.s3_client.deleted_keys == [duplicate_key]

    result = await db_session.execute(
        select(Material).where(Material.course_id == course.id)
    )
    assert [m.id for m in result.scalars().all()] == [canonical.id]

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_register_material_same_content_other_course_is_not_duplicate(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_boto3,
    fake_publisher,
):
    """Week 9 deduplication is course-scoped: identical content in another
    course of the same owner registers normally."""
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-dedup-scope-subject",
        "material-dedup-scope@example.com",
    )
    course_a = await _create_course(db_session, instructor, title="A")
    course_b = await _create_course(db_session, instructor, title="B")
    content = b"identical lecture pdf"
    await _create_material(
        db_session, course_a, instructor,
        status=READY_STATUS,
        sha256=hashlib.sha256(content).hexdigest(),
    )

    other_key = material_service.build_material_s3_key(course_b.id, "other.pdf")
    fake_boto3.s3_client.objects[other_key] = content

    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])
    response = await _register(db_session, token, course_b.id, other_key)

    assert response.status_code == 202
    body = response.json()
    assert body["job_id"] == "test-job-id"
    assert body["status"] == PENDING_STATUS
    assert len(fake_publisher) == 1

    result = await db_session.execute(
        select(Material).where(Material.course_id == course_b.id)
    )
    created = result.scalar_one()
    assert created.sha256 == hashlib.sha256(content).hexdigest()

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_register_material_duplicate_of_failed_reuses_without_retry(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_boto3,
    fake_publisher,
):
    """Week 9: a duplicate of a failed material just returns the existing
    material: no enqueue, no retry claimed, budget untouched."""
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-dedup-failed-subject",
        "material-dedup-failed@example.com",
    )
    course = await _create_course(db_session, instructor)
    content = b"identical lecture pdf"
    canonical = await _create_material(
        db_session, course, instructor,
        status=FAILED_STATUS,
        sha256=hashlib.sha256(content).hexdigest(),
    )
    duplicate_key = material_service.build_material_s3_key(course.id, "slides-copy.pdf")
    fake_boto3.s3_client.objects[duplicate_key] = content

    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])
    response = await _register(db_session, token, course.id, duplicate_key)

    assert response.status_code == 202
    body = response.json()
    assert body["material_id"] == str(canonical.id)
    assert body["job_id"] is None
    assert body["status"] == FAILED_STATUS
    assert fake_publisher == []
    assert fake_boto3.s3_client.deleted_keys == [duplicate_key]

    result = await db_session.execute(
        select(Material).where(Material.id == canonical.id)
    )
    unchanged = result.scalar_one()
    assert unchanged.status == FAILED_STATUS
    assert unchanged.retry_count == 0

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_register_material_duplicate_of_failed_with_exhausted_budget_reuses(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_boto3,
    fake_publisher,
):
    """Week 9: once the retry budget is exhausted a duplicate of a failed
    material is still reused (no enqueue, no budget change)."""
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-dedup-exhausted-subject",
        "material-dedup-exhausted@example.com",
    )
    course = await _create_course(db_session, instructor)
    content = b"identical lecture pdf"
    canonical = await _create_material(
        db_session, course, instructor,
        status=FAILED_STATUS,
        sha256=hashlib.sha256(content).hexdigest(),
    )
    canonical.retry_count = 3
    await db_session.commit()

    duplicate_key = material_service.build_material_s3_key(course.id, "slides-copy.pdf")
    fake_boto3.s3_client.objects[duplicate_key] = content

    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])
    response = await _register(db_session, token, course.id, duplicate_key)

    assert response.status_code == 202
    body = response.json()
    assert body["material_id"] == str(canonical.id)
    assert body["job_id"] is None
    assert body["status"] == FAILED_STATUS

    assert fake_publisher == []
    assert fake_boto3.s3_client.deleted_keys == [duplicate_key]

    result = await db_session.execute(
        select(Material).where(Material.id == canonical.id)
    )
    unchanged = result.scalar_one()
    assert unchanged.status == FAILED_STATUS
    assert unchanged.retry_count == 3

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.parametrize(
    "payload",
    [
        {"s3_key": "courses/x/materials/abc.pdf"},  # missing title
        {"title": "Slides"},  # missing s3_key
        {"title": "", "s3_key": "courses/x/materials/abc.pdf"},
    ],
)
@pytest.mark.asyncio
async def test_register_material_validation_errors_422(
    db_session,
    rsa_keypair,
    fake_jwks,
    payload,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-invalid-subject",
        "material-invalid@example.com",
    )
    course = await _create_course(db_session, instructor)
    s3_key = material_service.build_material_s3_key(course.id, "slides.pdf")

    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    body = dict(payload)
    if "s3_key" in body and body["s3_key"].startswith("courses/x"):
        body["s3_key"] = s3_key

    async with _api(db_session, token) as (client, headers):
        response = await client.post(
            f"/v1/courses/{course.id}/materials",
            json=body,
            headers=headers,
        )

    assert response.status_code == 422

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_register_material_student_forbidden(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-reg-student-owner-subject",
        "material-reg-student-owner@example.com",
    )
    course = await _create_course(db_session, instructor)
    s3_key = material_service.build_material_s3_key(course.id, "slides.pdf")

    student = await _create_user(
        db_session,
        "material-reg-student-subject",
        "material-reg-student@example.com",
    )
    token = _build_token(private_key, sub=student.keycloak_subject, roles=["student"])

    async with _api(db_session, token) as (client, headers):
        response = await client.post(
            f"/v1/courses/{course.id}/materials",
            json={"title": "Slides", "s3_key": s3_key},
            headers=headers,
        )

    assert response.status_code == 403

    result = await db_session.execute(
        select(Material).where(Material.s3_key == s3_key)
    )
    assert result.scalar_one_or_none() is None

    await db_session.delete(instructor)
    await db_session.delete(student)
    await db_session.commit()


@pytest.mark.asyncio
async def test_register_material_non_owner_instructor_forbidden(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair
    owner = await _create_user(
        db_session,
        "material-reg-nonowner-owner-subject",
        "material-reg-nonowner-owner@example.com",
    )
    course = await _create_course(db_session, owner)
    s3_key = material_service.build_material_s3_key(course.id, "slides.pdf")

    intruder = await _create_user(
        db_session,
        "material-reg-nonowner-intruder-subject",
        "material-reg-nonowner-intruder@example.com",
    )
    token = _build_token(private_key, sub=intruder.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.post(
            f"/v1/courses/{course.id}/materials",
            json={"title": "Slides", "s3_key": s3_key},
            headers=headers,
        )

    assert response.status_code == 403

    result = await db_session.execute(
        select(Material).where(Material.s3_key == s3_key)
    )
    assert result.scalar_one_or_none() is None

    await db_session.delete(owner)
    await db_session.delete(intruder)
    await db_session.commit()


@pytest.mark.asyncio
async def test_register_material_unauthenticated_and_404(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    async with _api(db_session) as (client, _headers):
        unauthenticated = await client.post(
            f"/v1/courses/{uuid.uuid4()}/materials",
            json={"title": "Slides", "s3_key": "courses/x/materials/abc.pdf"},
        )

    assert unauthenticated.status_code == 401

    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-reg-missing-subject",
        "material-reg-missing@example.com",
    )
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        missing_course = await client.post(
            f"/v1/courses/{uuid.uuid4()}/materials",
            json={"title": "Slides", "s3_key": "courses/x/materials/abc.pdf"},
            headers=headers,
        )

    assert missing_course.status_code == 404

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_list_materials_returns_own_course_materials(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-list-owner-subject",
        "material-list-owner@example.com",
    )
    course = await _create_course(db_session, instructor, title="List me")
    first = await _create_material(db_session, course, instructor)
    second = await _create_material(db_session, course, instructor)
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.get(
            f"/v1/courses/{course.id}/materials",
            headers=headers,
        )

    assert response.status_code == 200

    bodies = response.json()
    assert len(bodies) == 2
    assert {body["id"] for body in bodies} == {str(first.id), str(second.id)}
    for body in bodies:
        assert body["course_id"] == str(course.id)
        assert body["title"] == "Lecture Slides"
        assert body["s3_key"].startswith(f"courses/{course.id}/materials/")
        assert body["status"] == "pending"
        assert body["uploaded_by"] == str(instructor.id)
        assert body["created_at"] is not None

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_list_materials_empty_course_returns_empty_list(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-list-empty-subject",
        "material-list-empty@example.com",
    )
    course = await _create_course(db_session, instructor, title="Empty")
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.get(
            f"/v1/courses/{course.id}/materials",
            headers=headers,
        )

    assert response.status_code == 200
    assert response.json() == []

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_list_materials_forbidden_for_non_owner(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair
    owner = await _create_user(
        db_session,
        "material-list-nonowner-owner-subject",
        "material-list-nonowner-owner@example.com",
    )
    intruder = await _create_user(
        db_session,
        "material-list-nonowner-intruder-subject",
        "material-list-nonowner-intruder@example.com",
    )
    course = await _create_course(db_session, owner)
    await _create_material(db_session, course, owner)
    token = _build_token(private_key, sub=intruder.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.get(
            f"/v1/courses/{course.id}/materials",
            headers=headers,
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"

    await db_session.delete(owner)
    await db_session.delete(intruder)
    await db_session.commit()


@pytest.mark.asyncio
async def test_list_materials_unauthenticated_returns_401(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    async with _api(db_session) as (client, _headers):
        response = await client.get(
            f"/v1/courses/{uuid.uuid4()}/materials",
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_materials_nonexistent_course_returns_404(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-list-missing-subject",
        "material-list-missing@example.com",
    )
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.get(
            f"/v1/courses/{uuid.uuid4()}/materials",
            headers=headers,
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_list_materials_invalid_uuid_returns_422(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-list-baduuid-subject",
        "material-list-baduuid@example.com",
    )
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.get(
            "/v1/courses/not-a-uuid/materials",
            headers=headers,
        )

    assert response.status_code == 422

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_list_materials_ordered_by_created_at_desc_then_id(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-list-order-subject",
        "material-list-order@example.com",
    )
    course = await _create_course(db_session, instructor)

    base = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    early_1 = await _create_material(db_session, course, instructor)
    early_2 = await _create_material(db_session, course, instructor)
    late = await _create_material(db_session, course, instructor)

    early_1.created_at = base
    early_2.created_at = base
    late.created_at = base + timedelta(seconds=5)
    await db_session.commit()

    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.get(
            f"/v1/courses/{course.id}/materials",
            headers=headers,
        )

    assert response.status_code == 200
    expected_ids = [late.id, *sorted([early_1.id, early_2.id])]
    assert [body["id"] for body in response.json()] == [
        str(material_id) for material_id in expected_ids
    ]

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_get_material_status_returns_200_for_owner(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    """The status endpoint returns 200 for the user who owns the material's
    course; ownership is enforced via ``_require_owned_course``.
    """
    private_key, _ = rsa_keypair
    owner = await _create_user(
        db_session,
        "material-status-owner-subject",
        "material-status-owner@example.com",
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    token = _build_token(private_key, sub=owner.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.get(
            f"/v1/materials/{material.id}/status",
            headers=headers,
        )

    assert response.status_code == 200
    assert response.json()["material_id"] == str(material.id)
    assert response.json()["status"] == "pending"

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.parametrize("role", ["student", "instructor"])
@pytest.mark.asyncio
async def test_get_material_status_forbidden_for_non_owner(
    db_session,
    rsa_keypair,
    fake_jwks,
    role,
):
    """A material status is only readable by the user who owns its course.

    Ownership carries no role dependency: a non-owner gets 403 whether they
    hold the instructor role or not.
    """
    private_key, _ = rsa_keypair
    owner = await _create_user(
        db_session,
        "material-status-nonowner-owner-subject",
        "material-status-nonowner-owner@example.com",
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)

    intruder = await _create_user(
        db_session,
        "material-status-nonowner-intruder-subject",
        "material-status-nonowner-intruder@example.com",
    )
    token = _build_token(private_key, sub=intruder.keycloak_subject, roles=[role])

    async with _api(db_session, token) as (client, headers):
        response = await client.get(
            f"/v1/materials/{material.id}/status",
            headers=headers,
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"

    await db_session.delete(owner)
    await db_session.delete(intruder)
    await db_session.commit()


@pytest.mark.asyncio
async def test_get_material_status_unknown_material_returns_404(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-status-missing-subject",
        "material-status-missing@example.com",
    )
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.get(
            f"/v1/materials/{uuid.uuid4()}/status",
            headers=headers,
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Material not found"

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_get_material_status_unauthenticated_returns_401(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    async with _api(db_session) as (client, _headers):
        response = await client.get(
            f"/v1/materials/{uuid.uuid4()}/status",
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_material_status_invalid_uuid_returns_422(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-status-baduuid-subject",
        "material-status-baduuid@example.com",
    )
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.get(
            "/v1/materials/not-a-uuid/status",
            headers=headers,
        )

    assert response.status_code == 422

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.parametrize(
    "status",
    [PENDING_STATUS, PROCESSING_STATUS, READY_STATUS, FAILED_STATUS],
)
@pytest.mark.asyncio
async def test_get_material_status_reports_each_status_unchanged(
    db_session,
    rsa_keypair,
    fake_jwks,
    status,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-status-values-subject",
        "material-status-values@example.com",
    )
    course = await _create_course(db_session, instructor)
    material = await _create_material(db_session, course, instructor, status=status)
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.get(
            f"/v1/materials/{material.id}/status",
            headers=headers,
        )

    assert response.status_code == 200
    assert response.json()["status"] == status

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_process_material_failed_material_reenters_processing(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_publisher,
):
    """Week 9 retry control: POST /v1/materials/{id}/process re-enters a
    failed material through the shared retry budget — one atomic claim
    (retry_count 0 -> 1, committed before publish) and a fresh job."""
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-process-failed-subject",
        "material-process-failed@example.com",
    )
    course = await _create_course(db_session, instructor)
    material = await _create_material(
        db_session, course, instructor, status=FAILED_STATUS
    )

    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])
    response = await _process(db_session, token, material.id)

    assert response.status_code == 202
    body = response.json()
    assert body["material_id"] == str(material.id)
    assert body["job_id"] == "test-job-id"
    assert body["status"] == PENDING_STATUS

    # The reprocessing job references the material's own canonical object.
    assert fake_publisher == [
        {
            "material_id": material.id,
            "s3_key": material.s3_key,
            "course_id": material.course_id,
            "owner_id": material.uploaded_by,
        }
    ]

    result = await db_session.execute(
        select(Material).where(Material.id == material.id)
    )
    requeued = result.scalar_one()
    assert requeued.status == PENDING_STATUS
    assert requeued.retry_count == 1

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_process_material_ready_material_reprocesses(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_publisher,
):
    """Week 9 retry control: a ready material is explicitly reprocessable
    (the plan's claim matches ``ready`` and ``failed`` alike) and consumes
    the same retry budget."""
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-process-ready-subject",
        "material-process-ready@example.com",
    )
    course = await _create_course(db_session, instructor)
    material = await _create_material(
        db_session, course, instructor, status=READY_STATUS
    )

    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])
    response = await _process(db_session, token, material.id)

    assert response.status_code == 202
    body = response.json()
    assert body["material_id"] == str(material.id)
    assert body["status"] == PENDING_STATUS
    assert fake_publisher != []

    result = await db_session.execute(
        select(Material).where(Material.id == material.id)
    )
    requeued = result.scalar_one()
    assert requeued.status == PENDING_STATUS
    assert requeued.retry_count == 1

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize("initial_status", [PENDING_STATUS, PROCESSING_STATUS])
async def test_process_material_in_flight_returns_409(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_publisher,
    initial_status,
):
    """Week 9 retry control: an in-flight material (pending/processing) is
    rejected with 409 and nothing is enqueued — no second job can be created
    for it, mirroring the worker's own claim exclusivity."""
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-process-inflight-subject",
        "material-process-inflight@example.com",
    )
    course = await _create_course(db_session, instructor)
    material = await _create_material(
        db_session, course, instructor, status=initial_status
    )

    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])
    response = await _process(db_session, token, material.id)

    assert response.status_code == 409
    assert "already queued or processing" in response.json()["detail"]
    assert fake_publisher == []

    result = await db_session.execute(
        select(Material).where(Material.id == material.id)
    )
    unchanged = result.scalar_one()
    assert unchanged.status == initial_status
    assert unchanged.retry_count == 0

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize("initial_status", [FAILED_STATUS, READY_STATUS])
async def test_process_material_budget_exhausted_returns_409(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_publisher,
    initial_status,
):
    """Week 9 retry control: once the shared budget is exhausted, an
    eligible material is rejected with 409 — no enqueue, no budget change,
    no bypass for this endpoint."""
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-process-exhausted-subject",
        "material-process-exhausted@example.com",
    )
    course = await _create_course(db_session, instructor)
    material = await _create_material(
        db_session, course, instructor, status=initial_status
    )
    material.retry_count = 3
    await db_session.commit()

    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])
    response = await _process(db_session, token, material.id)

    assert response.status_code == 409
    assert "retry budget exhausted" in response.json()["detail"]
    assert fake_publisher == []

    result = await db_session.execute(
        select(Material).where(Material.id == material.id)
    )
    unchanged = result.scalar_one()
    assert unchanged.status == initial_status
    assert unchanged.retry_count == 3

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_process_material_publish_failure_compensates(
    db_session,
    rsa_keypair,
    fake_jwks,
    monkeypatch,
):
    """Week 9 retry control: when the queue publication fails after the
    claim, the claim is compensated (status restored, retry count
    decremented) while the retry is still pending, and the request returns
    500 — the same F8 contract as registration and dedup retries."""
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-process-retryfail-subject",
        "material-process-retryfail@example.com",
    )
    course = await _create_course(db_session, instructor)
    material = await _create_material(
        db_session, course, instructor, status=FAILED_STATUS
    )

    async def failing_enqueue(material_id, s3_key, course_id, owner_id):
        raise RuntimeError("broker unavailable")

    monkeypatch.setattr(
        "app.api.materials.enqueue_material_processing", failing_enqueue
    )

    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])
    response = await _process(
        db_session, token, material.id, raise_app_exceptions=False
    )

    assert response.status_code == 500

    engine = create_async_engine(settings.database_url)
    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    try:
        async with factory() as fresh_session:
            result = await fresh_session.execute(
                select(Material).where(Material.id == material.id)
            )
            restored = result.scalar_one()
            assert restored.status == FAILED_STATUS
            assert restored.retry_count == 0
    finally:
        await engine.dispose()

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_process_material_unknown_material_returns_404(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_publisher,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-process-404-subject",
        "material-process-404@example.com",
    )

    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])
    response = await _process(db_session, token, uuid.uuid4())

    assert response.status_code == 404
    assert fake_publisher == []

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_process_material_non_owner_instructor_forbidden(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_publisher,
):
    private_key, _ = rsa_keypair
    owner = await _create_user(
        db_session,
        "material-process-nonowner-owner-subject",
        "material-process-nonowner-owner@example.com",
    )
    intruder = await _create_user(
        db_session,
        "material-process-nonowner-intruder-subject",
        "material-process-nonowner-intruder@example.com",
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)

    token = _build_token(private_key, sub=intruder.keycloak_subject, roles=["instructor"])
    response = await _process(db_session, token, material.id)

    assert response.status_code == 403
    assert fake_publisher == []

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_process_material_student_forbidden(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_publisher,
):
    """The process trigger is a mutation: it requires the instructor role,
    same as registration — a student owning nothing gets 403."""
    private_key, _ = rsa_keypair
    owner = await _create_user(
        db_session,
        "material-process-student-owner-subject",
        "material-process-student-owner@example.com",
    )
    student = await _create_user(
        db_session,
        "material-process-student-subject",
        "material-process-student@example.com",
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)

    token = _build_token(private_key, sub=student.keycloak_subject, roles=["student"])
    response = await _process(db_session, token, material.id)

    assert response.status_code == 403
    assert fake_publisher == []

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_process_material_unauthenticated_returns_401(
    db_session,
    fake_publisher,
):
    owner = await _create_user(
        db_session,
        "material-process-anon-owner-subject",
        "material-process-anon-owner@example.com",
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)

    response = await _process(db_session, "", material.id)

    assert response.status_code == 401
    assert fake_publisher == []

    await db_session.delete(owner)
    await db_session.commit()


def test_openapi_documents_material_endpoints():
    client = TestClient(app)
    spec = client.get("/openapi.json").json()

    paths = spec["paths"]

    upload_url_path = "/v1/courses/{course_id}/materials/upload-url"
    register_path = "/v1/courses/{course_id}/materials"

    assert upload_url_path in paths
    assert register_path in paths

    status_path = "/v1/materials/{material_id}/status"

    assert status_path in paths

    status_responses = paths[status_path]["get"]["responses"]
    assert "200" in status_responses
    assert "401" in status_responses
    assert "403" in status_responses
    assert "404" in status_responses
    assert "422" in status_responses

    material_status_schema = spec["components"]["schemas"]["MaterialStatusResponse"]
    assert material_status_schema["properties"]["status"]["enum"] == [
        PENDING_STATUS,
        PROCESSING_STATUS,
        READY_STATUS,
        FAILED_STATUS,
    ]
    material_schema = spec["components"]["schemas"]["MaterialResponse"]
    assert material_schema["properties"]["status"]["enum"] == [
        PENDING_STATUS,
        PROCESSING_STATUS,
        READY_STATUS,
        FAILED_STATUS,
    ]

    upload_responses = paths[upload_url_path]["post"]["responses"]
    assert "200" in upload_responses
    assert "401" in upload_responses
    assert "403" in upload_responses
    assert "404" in upload_responses
    assert "422" in upload_responses

    register_responses = paths[register_path]["post"]["responses"]
    assert "202" in register_responses
    assert "401" in register_responses
    assert "403" in register_responses
    assert "404" in register_responses
    assert "409" in register_responses
    assert "422" in register_responses

    list_responses = paths[register_path]["get"]["responses"]
    assert "200" in list_responses
    assert "401" in list_responses
    assert "403" in list_responses
    assert "404" in list_responses

    process_path = "/v1/materials/{material_id}/process"

    assert process_path in paths

    process_responses = paths[process_path]["post"]["responses"]
    assert "202" in process_responses
    assert "401" in process_responses
    assert "403" in process_responses
    assert "404" in process_responses
    assert "409" in process_responses
    assert "429" in process_responses

    # Week 9 read API: persisted document pages.
    pages_path = "/v1/materials/{material_id}/pages"

    assert pages_path in paths

    pages_responses = paths[pages_path]["get"]["responses"]
    assert "200" in pages_responses
    assert "401" in pages_responses
    assert "403" in pages_responses
    assert "404" in pages_responses
    assert "422" in pages_responses

    pages_response_schema = (
        spec["components"]["schemas"]["MaterialPagesResponse"]
    )
    assert pages_response_schema["properties"]["material_id"]["format"] == "uuid"
    assert pages_response_schema["properties"]["pages"]["type"] == "array"
    assert (
        pages_response_schema["properties"]["pages"]["items"]["$ref"]
        == "#/components/schemas/MaterialPageResponse"
    )
    page_schema = spec["components"]["schemas"]["MaterialPageResponse"]
    assert page_schema["properties"]["page_number"]["minimum"] == 1
    assert page_schema["required"] == ["page_number", "text"]


def test_material_status_literal_accepts_exact_vocabulary_only():
    now = datetime.now(timezone.utc)

    for status_value in (PENDING_STATUS, PROCESSING_STATUS, READY_STATUS, FAILED_STATUS):
        status_response = MaterialStatusResponse(
            material_id=uuid.uuid4(),
            status=status_value,
        )
        assert status_response.status == status_value

        material = MaterialResponse(
            id=uuid.uuid4(),
            course_id=uuid.uuid4(),
            title="Slides",
            s3_key="courses/x/materials/a.pdf",
            status=status_value,
            uploaded_by=uuid.uuid4(),
            created_at=now,
        )
        assert material.status == status_value


def test_material_status_literal_rejects_unknown_status():
    with pytest.raises(ValidationError):
        MaterialStatusResponse(
            material_id=uuid.uuid4(),
            status="uploaded",
        )

    with pytest.raises(ValidationError):
        MaterialResponse(
            id=uuid.uuid4(),
            course_id=uuid.uuid4(),
            title="Slides",
            s3_key="courses/x/materials/a.pdf",
            status="uploaded",
            uploaded_by=uuid.uuid4(),
            created_at=datetime.now(timezone.utc),
        )


@pytest.mark.asyncio
async def test_api_full_flow_pending_then_ready_via_worker(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_boto3,
    fake_publisher,
    monkeypatch,
):
    """Authenticated API flow through the real ``_handle_material`` lifecycle.

    Covers: identity (``/auth/me``) -> course creation -> upload URL ->
    material registration (202 + job id) -> ``pending`` row -> real
    ``_handle_material(...)`` execution -> real database status transition to
    ``ready``.

    Not exercised: ``_process_material_content`` is monkeypatched, and the
    Celery publisher/broker is faked, so no worker or broker runs. No external
    storage download, ingestion, chunking, embedding, or vector upsert happens.
    """
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-flow-subject",
        "material-flow@example.com",
    )
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        me = await client.get("/auth/me", headers=headers)
        assert me.status_code == 200
        assert me.json()["id"] == str(instructor.id)
        assert me.json()["keycloak"]["subject"] == instructor.keycloak_subject

        course_response = await client.post(
            "/v1/courses",
            json={"title": "Flow Course", "description": "End to end"},
            headers=headers,
        )
        assert course_response.status_code == 201
        course_id = course_response.json()["id"]

        upload = await client.post(
            f"/v1/courses/{course_id}/materials/upload-url",
            json=_upload_url_payload(),
            headers=headers,
        )
        assert upload.status_code == 200
        s3_key = upload.json()["s3_key"]

        registered = await client.post(
            f"/v1/courses/{course_id}/materials",
            json={"title": "Lecture 1", "s3_key": s3_key},
            headers=headers,
        )
        assert registered.status_code == 202
        assert registered.json()["job_id"] == "test-job-id"
        material_id = uuid.UUID(registered.json()["material_id"])

    result = await db_session.execute(
        select(Material).where(Material.id == material_id)
    )
    assert result.scalar_one().status == PENDING_STATUS

    # ``app.workers.tasks.material_tasks`` imports ``app.workers.celery_app``,
    # whose Redis settings are guaranteed resolvable by tests/conftest.py.
    # No broker is contacted.
    from app.workers.tasks import material_tasks

    async def fake_process_content(*args, **kwargs):
        return None

    monkeypatch.setattr(
        material_tasks,
        "_process_material_content",
        fake_process_content,
    )

    engine = create_async_engine(settings.database_url)
    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    try:
        status = await material_tasks._handle_material(
            str(material_id),
            s3_key,
            course_id,
            str(instructor.id),
            session_factory=factory,
        )
        assert status == READY_STATUS

        # Fresh session/connection: ``AsyncSession.expire_all()`` is synchronous
        # and the worker commits on its own session.
        async with factory() as worker_db:
            final = await worker_db.execute(
                select(Material).where(Material.id == material_id)
            )
            assert final.scalar_one().status == READY_STATUS
    finally:
        # Cleanup must run even if an assertion above failed; the engine is
        # disposed even if cleanup itself fails.
        try:
            await db_session.delete(instructor)
            await db_session.commit()
        finally:
            await engine.dispose()


@pytest.mark.asyncio
async def test_get_material_pages_returns_persisted_pages_for_owner(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    """Week 9 read API: the owner reads the material's persisted page output,
    ordered by ascending page number regardless of write order."""
    private_key, _ = rsa_keypair
    owner = await _create_user(
        db_session,
        "material-pages-api-owner-subject",
        "material-pages-api-owner@example.com",
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    await material_service.replace_material_pages(
        db_session,
        material.id,
        pages=[(2, "second page text"), (1, "first page text")],
    )
    await db_session.commit()
    token = _build_token(private_key, sub=owner.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.get(
            f"/v1/materials/{material.id}/pages",
            headers=headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["material_id"] == str(material.id)
    assert body["pages"] == [
        {"page_number": 1, "text": "first page text"},
        {"page_number": 2, "text": "second page text"},
    ]

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_get_material_pages_returns_empty_list_before_first_success(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    """A material with no persisted page output — not yet processed, in
    flight, or failed — reads back as 200 with an empty list."""
    private_key, _ = rsa_keypair
    owner = await _create_user(
        db_session,
        "material-pages-api-empty-owner-subject",
        "material-pages-api-empty-owner@example.com",
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    token = _build_token(private_key, sub=owner.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.get(
            f"/v1/materials/{material.id}/pages",
            headers=headers,
        )

    assert response.status_code == 200
    assert response.json() == {"material_id": str(material.id), "pages": []}

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.parametrize("role", ["student", "instructor"])
@pytest.mark.asyncio
async def test_get_material_pages_forbidden_for_non_owner(
    db_session,
    rsa_keypair,
    fake_jwks,
    role,
):
    """Pages are only readable by the user who owns the material's course.

    Same authorization surface as the status read: ownership, no role
    dependency — a non-owner gets 403 whether they hold the instructor role
    or not.
    """
    private_key, _ = rsa_keypair
    owner = await _create_user(
        db_session,
        "material-pages-nonowner-owner-subject",
        "material-pages-nonowner-owner@example.com",
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)

    intruder = await _create_user(
        db_session,
        "material-pages-nonowner-intruder-subject",
        "material-pages-nonowner-intruder@example.com",
    )
    token = _build_token(private_key, sub=intruder.keycloak_subject, roles=[role])

    async with _api(db_session, token) as (client, headers):
        response = await client.get(
            f"/v1/materials/{material.id}/pages",
            headers=headers,
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"

    await db_session.delete(owner)
    await db_session.delete(intruder)
    await db_session.commit()


@pytest.mark.asyncio
async def test_get_material_pages_unknown_material_returns_404(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "material-pages-missing-subject",
        "material-pages-missing@example.com",
    )
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.get(
            f"/v1/materials/{uuid.uuid4()}/pages",
            headers=headers,
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Material not found"

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_get_single_material_page_for_owner(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    """Week 9: the owner reads one page; empty pages are returned too, and a
    page that does not exist is 404."""
    private_key, _ = rsa_keypair
    owner = await _create_user(
        db_session,
        "material-page-single-owner-subject",
        "material-page-single-owner@example.com",
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    await material_service.replace_material_pages(
        db_session,
        material.id,
        pages=[(1, "first page text"), (2, "")],
    )
    await db_session.commit()
    token = _build_token(private_key, sub=owner.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        first = await client.get(f"/v1/materials/{material.id}/pages/1", headers=headers)
        empty = await client.get(f"/v1/materials/{material.id}/pages/2", headers=headers)
        missing = await client.get(f"/v1/materials/{material.id}/pages/3", headers=headers)
        invalid = await client.get(f"/v1/materials/{material.id}/pages/0", headers=headers)

    assert first.status_code == 200
    assert first.json() == {"page_number": 1, "text": "first page text"}
    assert empty.status_code == 200
    assert empty.json() == {"page_number": 2, "text": ""}
    assert missing.status_code == 404
    assert missing.json()["detail"] == "Page not found"
    assert invalid.status_code == 422

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_get_single_material_page_forbidden_for_non_owner(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair
    owner = await _create_user(
        db_session,
        "material-page-single-nonowner-owner-subject",
        "material-page-single-nonowner-owner@example.com",
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    await material_service.replace_material_pages(
        db_session, material.id, pages=[(1, "secret page")]
    )
    await db_session.commit()
    intruder = await _create_user(
        db_session,
        "material-page-single-nonowner-intruder-subject",
        "material-page-single-nonowner-intruder@example.com",
    )
    token = _build_token(private_key, sub=intruder.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.get(
            f"/v1/materials/{material.id}/pages/1", headers=headers
        )

    assert response.status_code == 403

    await db_session.delete(owner)
    await db_session.delete(intruder)
    await db_session.commit()


@pytest.mark.asyncio
async def test_get_material_pages_unauthenticated_returns_401(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    async with _api(db_session) as (client, _headers):
        response = await client.get(
            f"/v1/materials/{uuid.uuid4()}/pages",
        )

    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Review fixes: size cap, ETag pinning, pagination, rate limit
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_register_material_stores_etag_of_hashed_object(
    db_session, rsa_keypair, fake_jwks, fake_boto3, fake_publisher
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session, "material-etag-subject", "material-etag@example.com"
    )
    course = await _create_course(db_session, instructor)
    s3_key = material_service.build_material_s3_key(course.id, "slides.pdf")
    fake_boto3.s3_client.etags[s3_key] = '"etag-v1"'
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    response = await _register(db_session, token, course.id, s3_key)

    assert response.status_code == 202
    material = await db_session.get(Material, uuid.UUID(response.json()["material_id"]))
    assert material.s3_etag == '"etag-v1"'

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_register_material_over_size_cap_returns_413(
    db_session, rsa_keypair, fake_jwks, fake_boto3, fake_publisher
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session, "material-toolarge-subject", "material-toolarge@example.com"
    )
    course = await _create_course(db_session, instructor)
    s3_key = material_service.build_material_s3_key(course.id, "huge.pdf")
    fake_boto3.s3_client.sizes[s3_key] = settings.max_upload_size_bytes + 1
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    response = await _register(db_session, token, course.id, s3_key)

    assert response.status_code == 413
    assert fake_publisher == []
    result = await db_session.execute(
        select(Material).where(Material.course_id == course.id)
    )
    assert result.scalars().all() == []

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_register_material_at_size_cap_is_accepted(
    db_session, rsa_keypair, fake_jwks, fake_boto3, fake_publisher
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session, "material-atcap-subject", "material-atcap@example.com"
    )
    course = await _create_course(db_session, instructor)
    s3_key = material_service.build_material_s3_key(course.id, "max.pdf")
    fake_boto3.s3_client.sizes[s3_key] = settings.max_upload_size_bytes
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    response = await _register(db_session, token, course.id, s3_key)

    assert response.status_code == 202

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_register_material_object_replaced_during_hash_returns_409(
    db_session, rsa_keypair, fake_jwks, fake_boto3, fake_publisher, monkeypatch
):
    """The hash is read with If-Match; an object replaced between HEAD and the
    read is rejected instead of registering a hash of a different version."""
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session, "material-replaced-subject", "material-replaced@example.com"
    )
    course = await _create_course(db_session, instructor)
    s3_key = material_service.build_material_s3_key(course.id, "slides.pdf")
    client = fake_boto3.s3_client
    client.etags[s3_key] = '"v1"'
    original_head = client.head_object

    def head_then_replace(Bucket, Key):
        info = original_head(Bucket, Key)
        client.etags[Key] = '"v2"'  # replaced right after HEAD
        return info

    monkeypatch.setattr(client, "head_object", head_then_replace)
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    response = await _register(db_session, token, course.id, s3_key)

    assert response.status_code == 409
    assert fake_publisher == []
    result = await db_session.execute(
        select(Material).where(Material.course_id == course.id)
    )
    assert result.scalars().all() == []

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_get_material_pages_is_paginated(db_session, rsa_keypair, fake_jwks):
    private_key, _ = rsa_keypair
    owner = await _create_user(
        db_session, "material-pages-paging-subject", "material-pages-paging@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    await material_service.replace_material_pages(
        db_session, material.id, pages=[(n, f"page {n}") for n in range(1, 6)]
    )
    await db_session.commit()
    token = _build_token(private_key, sub=owner.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        first = await client.get(
            f"/v1/materials/{material.id}/pages?limit=2", headers=headers
        )
        second = await client.get(
            f"/v1/materials/{material.id}/pages?limit=2&offset=2", headers=headers
        )
        last = await client.get(
            f"/v1/materials/{material.id}/pages?limit=2&offset=4", headers=headers
        )
        everything = await client.get(
            f"/v1/materials/{material.id}/pages", headers=headers
        )
        too_big = await client.get(
            f"/v1/materials/{material.id}/pages?limit=501", headers=headers
        )

    assert [p["page_number"] for p in first.json()["pages"]] == [1, 2]
    assert [p["page_number"] for p in second.json()["pages"]] == [3, 4]
    assert [p["page_number"] for p in last.json()["pages"]] == [5]
    assert len(everything.json()["pages"]) == 5
    assert too_big.status_code == 422

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_write_endpoints_are_rate_limited_per_user(
    db_session, rsa_keypair, fake_jwks, fake_boto3, monkeypatch
):
    monkeypatch.setattr(settings, "rate_limit_writes_per_minute", 2)
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session, "material-ratelimit-subject", "material-ratelimit@example.com"
    )
    course = await _create_course(db_session, instructor)
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        url = f"/v1/courses/{course.id}/materials/upload-url"
        codes = [
            (await client.post(url, json=_upload_url_payload(), headers=headers))
            for _ in range(3)
        ]
        # Other write endpoints share the same per-user budget.
        course_create = await client.post(
            "/v1/courses", json={"title": "Another", "description": "x"}, headers=headers
        )

    assert [r.status_code for r in codes] == [200, 200, 429]
    assert int(codes[2].headers["Retry-After"]) >= 1
    assert course_create.status_code == 429

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_rate_limit_can_be_disabled(
    db_session, rsa_keypair, fake_jwks, fake_boto3, monkeypatch
):
    monkeypatch.setattr(settings, "rate_limit_writes_per_minute", 0)
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session, "material-ratelimit-off-subject", "material-ratelimit-off@example.com"
    )
    course = await _create_course(db_session, instructor)
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        url = f"/v1/courses/{course.id}/materials/upload-url"
        for _ in range(5):
            response = await client.post(url, json=_upload_url_payload(), headers=headers)
            assert response.status_code == 200

    await db_session.delete(instructor)
    await db_session.commit()
