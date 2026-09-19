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
from sqlalchemy import select

from app.config import settings
from app.db.session import get_db
from app.main import app
from app.models.course import Course
from app.models.material import Material
from app.models.user import User
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
async def test_register_material_creates_pending_row(
    db_session,
    rsa_keypair,
    fake_jwks,
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

    assert response.status_code == 201

    body = response.json()

    uuid.UUID(body["id"])
    assert body["course_id"] == str(course.id)
    assert body["title"] == "Slides"
    assert body["s3_key"] == s3_key
    assert body["status"] == "pending"
    assert body["uploaded_by"] == str(instructor.id)

    result = await db_session.execute(
        select(Material).where(Material.id == body["id"])
    )
    stored = result.scalar_one()
    assert stored.course_id == course.id
    assert stored.uploaded_by == instructor.id
    assert stored.status == "pending"

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

    assert first.status_code == 201
    assert second.status_code == 409

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


def test_openapi_documents_material_endpoints():
    client = TestClient(app)
    spec = client.get("/openapi.json").json()

    paths = spec["paths"]

    upload_url_path = "/v1/courses/{course_id}/materials/upload-url"
    register_path = "/v1/courses/{course_id}/materials"

    assert upload_url_path in paths
    assert register_path in paths

    upload_responses = paths[upload_url_path]["post"]["responses"]
    assert "200" in upload_responses
    assert "401" in upload_responses
    assert "403" in upload_responses
    assert "404" in upload_responses
    assert "422" in upload_responses

    register_responses = paths[register_path]["post"]["responses"]
    assert "201" in register_responses
    assert "401" in register_responses
    assert "403" in register_responses
    assert "404" in register_responses
    assert "409" in register_responses
    assert "422" in register_responses