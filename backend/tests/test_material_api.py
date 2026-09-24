"""Phase 6 tests for the material upload pipeline (/v1/courses/{id}/materials/*).

Uses the established authenticated-endpoint harness (fake JWKS + overridden DB
session) and a fake boto3 so no real MinIO/S3 instance is required. Tests
verify behavior, not storage internals.
"""
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
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
from app.services.auth import oidc as oidc_module

ISSUER = settings.keycloak_issuer
AUDIENCE = settings.keycloak_audience


@pytest.fixture
def rsa_keypair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    return private_pem, public_pem


@pytest.fixture
def fake_jwks(rsa_keypair, monkeypatch):
    _, public_pem = rsa_keypair

    class FakeJwksClient:
        def get_signing_key_from_jwt(self, token):
            return SimpleNamespace(key=public_pem)

    monkeypatch.setattr(oidc_module, "_JWK_CLIENT", FakeJwksClient())

    return FakeJwksClient


class FakeS3Client:
    def __init__(self):
        self.calls = []

    def generate_presigned_url(self, ClientMethod, Params, ExpiresIn):
        self.calls.append((ClientMethod, dict(Params), ExpiresIn))
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


async def _create_user(db, subject: str, email: str) -> User:
    result = await db.execute(
        select(User).where(User.keycloak_subject == subject)
    )
    for user in result.scalars():
        await db.delete(user)
    await db.commit()

    user = User(
        keycloak_issuer=ISSUER,
        keycloak_subject=subject,
        email=email,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


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


async def _create_material(
    db,
    course: Course,
    owner: User,
    *,
    status: str = PENDING_STATUS,
) -> Material:
    material = Material(
        course_id=course.id,
        title="Lecture Slides",
        s3_key=f"courses/{course.id}/materials/{uuid.uuid4()}-slides.pdf",
        uploaded_by=owner.id,
        status=status,
    )
    db.add(material)
    await db.commit()
    await db.refresh(material)
    return material


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
    assert body["upload_url"] == "https://storage.example/presigned-upload-url"
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

    assert fake_boto3.client_kwargs == {
        "endpoint_url": settings.s3_endpoint_url,
        "aws_access_key_id": settings.s3_access_key_id,
        "aws_secret_access_key": settings.s3_secret_access_key,
        "region_name": settings.s3_region_name,
    }

    method, params, expires_in = fake_boto3.s3_client.calls[0]
    assert method == "put_object"
    assert params["Bucket"] == settings.s3_bucket_name
    assert params["Key"] == response.json()["s3_key"]
    assert expires_in == settings.s3_url_expiration_seconds

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
async def test_register_material_duplicate_key_conflicts(
    db_session,
    rsa_keypair,
    fake_jwks,
    fake_publisher,
):
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
    assert second.status_code == 409
    assert len(fake_publisher) == 1

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