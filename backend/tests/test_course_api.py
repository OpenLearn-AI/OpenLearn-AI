"""Phase 5 tests for the Course CRUD API (/v1/courses).

Mirrors the authenticated-endpoint test setup in test_oidc.py / test_profile_api.py
(fake JWKS + dependency-overridden database session).
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
from app.models.user import User
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


def _course_payload(**overrides) -> dict:
    payload = {
        "title": "Intro to AI",
        "description": "A first course in artificial intelligence.",
    }
    payload.update(overrides)
    return payload


@pytest.mark.asyncio
async def test_instructor_can_create_course(db_session, rsa_keypair, fake_jwks):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "course-instructor-subject",
        "course-instructor@example.com",
    )
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.post(
            "/v1/courses",
            json=_course_payload(),
            headers=headers,
        )

    assert response.status_code == 201

    body = response.json()

    assert body["owner_id"] == str(instructor.id)
    assert body["title"] == "Intro to AI"
    assert body["description"] == "A first course in artificial intelligence."
    uuid.UUID(body["id"])
    assert body["created_at"] is not None

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_student_cannot_create_course(db_session, rsa_keypair, fake_jwks):
    private_key, _ = rsa_keypair
    student = await _create_user(
        db_session,
        "course-student-subject",
        "course-student@example.com",
    )
    token = _build_token(private_key, sub=student.keycloak_subject, roles=["student"])

    async with _api(db_session, token) as (client, headers):
        response = await client.post(
            "/v1/courses",
            json=_course_payload(),
            headers=headers,
        )

    assert response.status_code == 403

    await db_session.delete(student)
    await db_session.commit()


@pytest.mark.asyncio
async def test_create_course_unauthenticated(db_session, rsa_keypair, fake_jwks):
    async with _api(db_session) as (client, _headers):
        response = await client.post(
            "/v1/courses",
            json=_course_payload(),
        )

    assert response.status_code == 401


@pytest.mark.parametrize("spoofed_field", ["owner_id", "user_id", "created_at"])
@pytest.mark.asyncio
async def test_create_course_rejects_client_identity_fields(
    db_session,
    rsa_keypair,
    fake_jwks,
    spoofed_field,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        f"course-spoof-{spoofed_field}-subject",
        f"course-spoof-{spoofed_field}@example.com",
    )
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.post(
            "/v1/courses",
            json=_course_payload(**{spoofed_field: str(uuid.uuid4())}),
            headers=headers,
        )

    assert response.status_code == 422

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_list_courses_available_to_authenticated_user(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "course-list-instructor-subject",
        "course-list-instructor@example.com",
    )
    student = await _create_user(
        db_session,
        "course-list-student-subject",
        "course-list-student@example.com",
    )

    first = await _create_course(db_session, instructor, title="First")
    second = await _create_course(db_session, instructor, title="Second")

    token = _build_token(private_key, sub=student.keycloak_subject, roles=["student"])

    async with _api(db_session, token) as (client, headers):
        response = await client.get("/v1/courses", headers=headers)

    assert response.status_code == 200

    ids = {course["id"] for course in response.json()}
    assert str(first.id) in ids
    assert str(second.id) in ids

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_get_course_works_for_authenticated_user(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "course-get-subject",
        "course-get@example.com",
    )
    course = await _create_course(db_session, instructor, title="Visible")

    student = await _create_user(
        db_session,
        "course-get-student-subject",
        "course-get-student@example.com",
    )
    token = _build_token(private_key, sub=student.keycloak_subject, roles=["student"])

    async with _api(db_session, token) as (client, headers):
        response = await client.get(f"/v1/courses/{course.id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["title"] == "Visible"
    assert response.json()["owner_id"] == str(instructor.id)

    await db_session.delete(instructor)
    await db_session.delete(student)
    await db_session.commit()


@pytest.mark.asyncio
async def test_get_course_nonexistent_returns_404(db_session, rsa_keypair, fake_jwks):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "course-get-missing-subject",
        "course-get-missing@example.com",
    )
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.get(
            f"/v1/courses/{uuid.uuid4()}",
            headers=headers,
        )

    assert response.status_code == 404

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_get_course_invalid_uuid_returns_422(db_session, rsa_keypair, fake_jwks):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "course-get-baduuid-subject",
        "course-get-baduuid@example.com",
    )
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.get("/v1/courses/not-a-uuid", headers=headers)

    assert response.status_code == 422

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_owner_can_update_course(db_session, rsa_keypair, fake_jwks):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "course-update-owner-subject",
        "course-update-owner@example.com",
    )
    course = await _create_course(db_session, instructor, title="Old")
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.put(
            f"/v1/courses/{course.id}",
            json=_course_payload(title="New", description="Updated"),
            headers=headers,
        )

    assert response.status_code == 200

    body = response.json()
    assert body["title"] == "New"
    assert body["description"] == "Updated"
    assert body["owner_id"] == str(instructor.id)

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_non_owner_cannot_update_course(db_session, rsa_keypair, fake_jwks):
    private_key, _ = rsa_keypair
    owner = await _create_user(
        db_session,
        "course-update-owner2-subject",
        "course-update-owner2@example.com",
    )
    intruder = await _create_user(
        db_session,
        "course-update-intruder-subject",
        "course-update-intruder@example.com",
    )
    course = await _create_course(db_session, owner, title="Owned")

    token = _build_token(private_key, sub=intruder.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.put(
            f"/v1/courses/{course.id}",
            json=_course_payload(title="Hijacked"),
            headers=headers,
        )

    assert response.status_code == 403

    result = await db_session.execute(
        select(Course).where(Course.id == course.id)
    )
    stored = result.scalar_one()
    assert stored.title == "Owned"

    await db_session.delete(owner)
    await db_session.delete(intruder)
    await db_session.commit()


@pytest.mark.asyncio
async def test_update_nonexistent_course_returns_404(db_session, rsa_keypair, fake_jwks):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "course-update-missing-subject",
        "course-update-missing@example.com",
    )
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.put(
            f"/v1/courses/{uuid.uuid4()}",
            json=_course_payload(),
            headers=headers,
        )

    assert response.status_code == 404

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_owner_can_delete_course(db_session, rsa_keypair, fake_jwks):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "course-delete-owner-subject",
        "course-delete-owner@example.com",
    )
    course = await _create_course(db_session, instructor, title="To delete")
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.delete(f"/v1/courses/{course.id}", headers=headers)

    assert response.status_code == 204

    result = await db_session.execute(
        select(Course).where(Course.id == course.id)
    )
    assert result.scalar_one_or_none() is None

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_non_owner_cannot_delete_course(db_session, rsa_keypair, fake_jwks):
    private_key, _ = rsa_keypair
    owner = await _create_user(
        db_session,
        "course-delete-owner2-subject",
        "course-delete-owner2@example.com",
    )
    intruder = await _create_user(
        db_session,
        "course-delete-intruder-subject",
        "course-delete-intruder@example.com",
    )
    course = await _create_course(db_session, owner, title="Protected")

    token = _build_token(private_key, sub=intruder.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.delete(f"/v1/courses/{course.id}", headers=headers)

    assert response.status_code == 403

    result = await db_session.execute(
        select(Course).where(Course.id == course.id)
    )
    assert result.scalar_one_or_none() is not None

    await db_session.delete(owner)
    await db_session.delete(intruder)
    await db_session.commit()


@pytest.mark.asyncio
async def test_protected_operations_require_authentication(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    async with _api(db_session) as (client, _headers):
        list_response = await client.get("/v1/courses")
        update_response = await client.put(
            f"/v1/courses/{uuid.uuid4()}",
            json=_course_payload(),
        )
        delete_response = await client.delete(f"/v1/courses/{uuid.uuid4()}")
        get_response = await client.get(f"/v1/courses/{uuid.uuid4()}")

    assert list_response.status_code == 401
    assert update_response.status_code == 401
    assert delete_response.status_code == 401
    assert get_response.status_code == 401


@pytest.mark.parametrize(
    "payload",
    [
        _course_payload(title=""),  # type: ignore[misc]
        {"description": "missing title"},
        {"title": "x" * 256},
    ],
)
@pytest.mark.asyncio
async def test_create_course_invalid_payload_returns_422(
    db_session,
    rsa_keypair,
    fake_jwks,
    payload,
):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "course-invalid-subject",
        "course-invalid@example.com",
    )
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.post("/v1/courses", json=payload, headers=headers)

    assert response.status_code == 422

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_create_course_rejects_unknown_fields(db_session, rsa_keypair, fake_jwks):
    private_key, _ = rsa_keypair
    instructor = await _create_user(
        db_session,
        "course-extra-subject",
        "course-extra@example.com",
    )
    token = _build_token(private_key, sub=instructor.keycloak_subject, roles=["instructor"])

    async with _api(db_session, token) as (client, headers):
        response = await client.post(
            "/v1/courses",
            json=_course_payload(unexpected_field="nope"),
            headers=headers,
        )

    assert response.status_code == 422

    await db_session.delete(instructor)
    await db_session.commit()


@pytest.mark.asyncio
async def test_admin_without_instructor_role_cannot_create_course(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    """Documents Phase 5 admin behavior: Keycloak roles are discrete authority;
    ``admin`` alone does not grant instructor privileges (no invented override)."""
    private_key, _ = rsa_keypair
    admin = await _create_user(
        db_session,
        "course-admin-subject",
        "course-admin@example.com",
    )
    token = _build_token(private_key, sub=admin.keycloak_subject, roles=["admin"])

    async with _api(db_session, token) as (client, headers):
        response = await client.post(
            "/v1/courses",
            json=_course_payload(),
            headers=headers,
        )

    assert response.status_code == 403

    await db_session.delete(admin)
    await db_session.commit()


@pytest.mark.asyncio
async def test_admin_has_no_ownership_override_for_update(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    """Admin does not automatically own another user's course; owner-only
    modification remains owner-only."""
    private_key, _ = rsa_keypair
    owner = await _create_user(
        db_session,
        "course-admin-override-owner-subject",
        "course-admin-override-owner@example.com",
    )
    admin = await _create_user(
        db_session,
        "course-admin-override-admin-subject",
        "course-admin-override-admin@example.com",
    )
    course = await _create_course(db_session, owner, title="Not admin's")

    token = _build_token(private_key, sub=admin.keycloak_subject, roles=["admin"])

    async with _api(db_session, token) as (client, headers):
        response = await client.put(
            f"/v1/courses/{course.id}",
            json=_course_payload(title="Seized"),
            headers=headers,
        )

    assert response.status_code == 403

    await db_session.delete(owner)
    await db_session.delete(admin)
    await db_session.commit()


@pytest.mark.asyncio
async def test_admin_has_no_ownership_override_for_delete(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair
    owner = await _create_user(
        db_session,
        "course-admin-del-owner-subject",
        "course-admin-del-owner@example.com",
    )
    admin = await _create_user(
        db_session,
        "course-admin-del-admin-subject",
        "course-admin-del-admin@example.com",
    )
    course = await _create_course(db_session, owner, title="Keep me")

    token = _build_token(private_key, sub=admin.keycloak_subject, roles=["admin"])

    async with _api(db_session, token) as (client, headers):
        response = await client.delete(f"/v1/courses/{course.id}", headers=headers)

    assert response.status_code == 403

    await db_session.delete(owner)
    await db_session.delete(admin)
    await db_session.commit()


def test_openapi_documents_course_endpoints():
    client = TestClient(app)
    spec = client.get("/openapi.json").json()

    paths = spec["paths"]
    assert "/v1/courses" in paths
    assert "/v1/courses/{course_id}" in paths

    post_responses = paths["/v1/courses"]["post"]["responses"]
    assert "201" in post_responses
    assert "401" in post_responses
    assert "403" in post_responses
    assert "422" in post_responses

    get_responses = paths["/v1/courses"]["get"]["responses"]
    assert "200" in get_responses
    assert "401" in get_responses

    put_responses = paths["/v1/courses/{course_id}"]["put"]["responses"]
    assert "200" in put_responses
    assert "401" in put_responses
    assert "403" in put_responses
    assert "404" in put_responses

    delete_responses = paths["/v1/courses/{course_id}"]["delete"]["responses"]
    assert "204" in delete_responses
    assert "401" in delete_responses
    assert "403" in delete_responses
    assert "404" in delete_responses