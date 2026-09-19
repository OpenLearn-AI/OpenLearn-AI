"""Phase 2 tests for the Profile API (GET/PUT /v1/users/me).

Mirrors the authenticated-endpoint test setup in test_oidc.py (fake JWKS +
dependency-overridden database session).
"""
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select

from app.config import settings
from app.db.session import get_db
from app.main import app
from app.models.profile import Profile
from app.models.user import User
from app.services.auth import oidc as oidc_module
from app.services.profile_service import get_profile_by_user_id

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


def _build_token(
    private_key: str,
    *,
    sub: str = "123e4567-e89b-12d3-a456-426614174000",
    iss: str = ISSUER,
    aud: str = AUDIENCE,
    email: str = "student1@openlearn.dev",
    extra: dict | None = None,
    missing_claims: list[str] | None = None,
) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": sub,
        "iss": iss,
        "aud": aud,
        "iat": now,
        "exp": now + timedelta(minutes=15),
        "email": email,
        "realm_access": {"roles": ["student"]},
    }

    if missing_claims:
        for claim in missing_claims:
            payload.pop(claim, None)

    if extra:
        payload.update(extra)

    return jwt.encode(payload, private_key, algorithm="RS256")


def _profile_payload(**overrides) -> dict:
    payload = {
        "education_level": "Bachelor",
        "major": "AI",
        "preferred_language": "en",
        "university": None,
        "learning_style_vark": None,
        "daily_available_minutes": 60,
    }
    payload.update(overrides)
    return payload


async def _create_user(db, subject: str, email: str) -> User:
    await _delete_user_by_subject(db, subject)

    user = User(
        keycloak_issuer=ISSUER,
        keycloak_subject=subject,
        email=email,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def _delete_user_by_subject(db, subject: str) -> None:
    result = await db.execute(
        select(User).where(User.keycloak_subject == subject)
    )
    for user in result.scalars():
        await db.delete(user)
    await db.commit()


async def _count_profiles_for(db, user_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count()).select_from(Profile).where(
            Profile.user_id == user_id
        )
    )
    return result.scalar_one()


@pytest.mark.asyncio
async def test_get_me_requires_authentication(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.get("/v1/users/me")

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_put_me_requires_authentication(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.put(
                "/v1/users/me",
                json=_profile_payload(),
            )

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_me_rejects_invalid_token(db_session, rsa_keypair, fake_jwks):
    # Signed by a different key than the one the fake JWKS publishes.
    other_private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    ).private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    token = _build_token(other_private_key)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.get(
                "/v1/users/me",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_me_returns_404_without_local_user(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair
    subject = "profile-api-unknown-subject"

    token = _build_token(private_key, sub=subject)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.get(
                "/v1/users/me",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404

        # No local user may be created as a side effect.
        result = await db_session.execute(
            select(User).where(User.keycloak_subject == subject)
        )
        assert result.scalar_one_or_none() is None
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_put_me_returns_404_without_local_user(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair
    subject = "profile-api-put-unknown-subject"

    token = _build_token(private_key, sub=subject)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.put(
                "/v1/users/me",
                json=_profile_payload(),
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404

        result = await db_session.execute(
            select(User).where(User.keycloak_subject == subject)
        )
        assert result.scalar_one_or_none() is None
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_identity_resolved_by_keycloak_identity_not_email(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair

    user = await _create_user(
        db_session,
        "profile-api-email-mismatch-subject",
        "local-user@example.com",
    )
    profile = Profile(
        user_id=user.id,
        education_level="Bachelor",
        major="AI",
        preferred_language="ar",
        daily_available_minutes=45,
    )
    db_session.add(profile)
    await db_session.commit()

    # Token email does not match the local user's email; identity must be
    # resolved by (issuer, subject) alone.
    token = _build_token(
        private_key,
        sub=user.keycloak_subject,
        email="someone-else@example.com",
    )

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.get(
                "/v1/users/me",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        assert response.json()["user_id"] == str(user.id)
    finally:
        app.dependency_overrides.clear()

        await db_session.delete(user)
        await db_session.commit()


@pytest.mark.asyncio
async def test_get_me_returns_existing_profile(db_session, rsa_keypair, fake_jwks):
    private_key, _ = rsa_keypair

    user = await _create_user(
        db_session,
        "profile-api-get-subject",
        "profile-get@example.com",
    )
    profile = Profile(
        user_id=user.id,
        education_level="Master",
        major="Data Science",
        university="Cairo University",
        preferred_language="ar",
        learning_style_vark="visual",
        daily_available_minutes=45,
    )
    db_session.add(profile)
    await db_session.commit()

    token = _build_token(private_key, sub=user.keycloak_subject)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.get(
                "/v1/users/me",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200

        body = response.json()

        assert body["id"] == str(profile.id)
        assert body["user_id"] == str(user.id)
        assert body["education_level"] == "Master"
        assert body["major"] == "Data Science"
        assert body["university"] == "Cairo University"
        assert body["preferred_language"] == "ar"
        assert body["learning_style_vark"] == "visual"
        assert body["daily_available_minutes"] == 45
    finally:
        app.dependency_overrides.clear()

        await db_session.delete(user)
        await db_session.commit()


@pytest.mark.asyncio
async def test_get_me_returns_404_when_profile_missing(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair

    user = await _create_user(
        db_session,
        "profile-api-get-missing-subject",
        "profile-get-missing@example.com",
    )

    token = _build_token(private_key, sub=user.keycloak_subject)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.get(
                "/v1/users/me",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()

        await db_session.delete(user)
        await db_session.commit()


@pytest.mark.asyncio
async def test_put_me_creates_profile(db_session, rsa_keypair, fake_jwks):
    private_key, _ = rsa_keypair

    user = await _create_user(
        db_session,
        "profile-api-put-create-subject",
        "profile-put-create@example.com",
    )

    token = _build_token(private_key, sub=user.keycloak_subject)
    payload = _profile_payload(
        education_level="Bachelor",
        major="AI",
        preferred_language="ar",
        daily_available_minutes=120,
    )

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.put(
                "/v1/users/me",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200

        body = response.json()

        assert body["user_id"] == str(user.id)
        assert body["education_level"] == "Bachelor"
        assert body["major"] == "AI"
        assert body["preferred_language"] == "ar"
        assert body["university"] is None
        assert body["learning_style_vark"] is None
        assert body["daily_available_minutes"] == 120

        assert await _count_profiles_for(db_session, user.id) == 1

        stored = await get_profile_by_user_id(db_session, user.id)
        assert stored is not None
        assert stored.major == "AI"
        assert stored.daily_available_minutes == 120
    finally:
        app.dependency_overrides.clear()

        await db_session.delete(user)
        await db_session.commit()


@pytest.mark.asyncio
async def test_put_me_rejects_client_user_id(db_session, rsa_keypair, fake_jwks):
    private_key, _ = rsa_keypair

    user = await _create_user(
        db_session,
        "profile-api-identity-subject",
        "profile-identity@example.com",
    )
    other_user = await _create_user(
        db_session,
        "profile-api-identity-other-subject",
        "profile-identity-other@example.com",
    )

    token = _build_token(private_key, sub=user.keycloak_subject)
    payload = _profile_payload(user_id=str(other_user.id))

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.put(
                "/v1/users/me",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )

        # Identity comes exclusively from the token; a client-supplied
        # user_id is not a profile field and must be rejected outright.
        assert response.status_code == 422

        assert await _count_profiles_for(db_session, user.id) == 0
        assert await _count_profiles_for(db_session, other_user.id) == 0
    finally:
        app.dependency_overrides.clear()

        await db_session.delete(user)
        await db_session.delete(other_user)
        await db_session.commit()


@pytest.mark.asyncio
async def test_put_me_replaces_profile_completely(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair

    user = await _create_user(
        db_session,
        "profile-api-replace-subject",
        "profile-replace@example.com",
    )
    db_session.add(
        Profile(
            user_id=user.id,
            education_level="Bachelor",
            major="AI",
            university="ABC",
            preferred_language="en",
            learning_style_vark="visual",
            daily_available_minutes=120,
        )
    )
    await db_session.commit()

    token = _build_token(private_key, sub=user.keycloak_subject)
    payload = _profile_payload(
        major="Data Science",
        preferred_language="ar",
        university=None,
        learning_style_vark=None,
        daily_available_minutes=60,
    )

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.put(
                "/v1/users/me",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200

        body = response.json()

        assert body["user_id"] == str(user.id)
        assert body["education_level"] == "Bachelor"
        assert body["major"] == "Data Science"
        assert body["preferred_language"] == "ar"
        assert body["university"] is None
        assert body["learning_style_vark"] is None
        assert body["daily_available_minutes"] == 60

        assert await _count_profiles_for(db_session, user.id) == 1

        stored = await get_profile_by_user_id(db_session, user.id)
        assert stored is not None
        assert stored.university is None
        assert stored.learning_style_vark is None
        assert stored.major == "Data Science"
    finally:
        app.dependency_overrides.clear()

        await db_session.delete(user)
        await db_session.commit()


@pytest.mark.parametrize(
    "missing_field",
    [
        "education_level",
        "major",
        "preferred_language",
        "daily_available_minutes",
    ],
)
@pytest.mark.asyncio
async def test_put_me_rejects_missing_required_fields(
    db_session,
    rsa_keypair,
    fake_jwks,
    missing_field,
):
    private_key, _ = rsa_keypair

    user = await _create_user(
        db_session,
        "profile-api-validation-subject",
        "profile-validation@example.com",
    )

    token = _build_token(private_key, sub=user.keycloak_subject)
    payload = _profile_payload()
    del payload[missing_field]

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.put(
                "/v1/users/me",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 422
        assert await _count_profiles_for(db_session, user.id) == 0
    finally:
        app.dependency_overrides.clear()

        await db_session.delete(user)
        await db_session.commit()


@pytest.mark.parametrize("language", ["fr", "EN", ""])
@pytest.mark.asyncio
async def test_put_me_rejects_unsupported_language(
    db_session,
    rsa_keypair,
    fake_jwks,
    language,
):
    private_key, _ = rsa_keypair

    user = await _create_user(
        db_session,
        "profile-api-language-subject",
        "profile-language@example.com",
    )

    token = _build_token(private_key, sub=user.keycloak_subject)
    payload = _profile_payload(preferred_language=language)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.put(
                "/v1/users/me",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 422
        assert await _count_profiles_for(db_session, user.id) == 0
    finally:
        app.dependency_overrides.clear()

        await db_session.delete(user)
        await db_session.commit()


@pytest.mark.parametrize("minutes", [0, -1, 1441])
@pytest.mark.asyncio
async def test_put_me_rejects_out_of_range_daily_minutes(
    db_session,
    rsa_keypair,
    fake_jwks,
    minutes,
):
    private_key, _ = rsa_keypair

    user = await _create_user(
        db_session,
        "profile-api-minutes-subject",
        "profile-minutes@example.com",
    )

    token = _build_token(private_key, sub=user.keycloak_subject)
    payload = _profile_payload(daily_available_minutes=minutes)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.put(
                "/v1/users/me",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 422
        assert await _count_profiles_for(db_session, user.id) == 0
    finally:
        app.dependency_overrides.clear()

        await db_session.delete(user)
        await db_session.commit()


@pytest.mark.parametrize(
    "field,value",
    [
        ("daily_available_minutes", "abc"),
        ("education_level", 123),
    ],
)
@pytest.mark.asyncio
async def test_put_me_rejects_wrong_types(
    db_session,
    rsa_keypair,
    fake_jwks,
    field,
    value,
):
    private_key, _ = rsa_keypair

    user = await _create_user(
        db_session,
        "profile-api-types-subject",
        "profile-types@example.com",
    )

    token = _build_token(private_key, sub=user.keycloak_subject)
    payload = _profile_payload(**{field: value})

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.put(
                "/v1/users/me",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 422
        assert await _count_profiles_for(db_session, user.id) == 0
    finally:
        app.dependency_overrides.clear()

        await db_session.delete(user)
        await db_session.commit()


@pytest.mark.asyncio
async def test_put_me_rejects_boolean_daily_minutes(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    """Pydantic lax mode would coerce true -> 1; the strict field must not."""
    private_key, _ = rsa_keypair

    user = await _create_user(
        db_session,
        "profile-api-bool-minutes-subject",
        "profile-bool-minutes@example.com",
    )

    token = _build_token(private_key, sub=user.keycloak_subject)
    payload = _profile_payload(daily_available_minutes=True)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.put(
                "/v1/users/me",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 422
        assert await _count_profiles_for(db_session, user.id) == 0
    finally:
        app.dependency_overrides.clear()

        await db_session.delete(user)
        await db_session.commit()


@pytest.mark.asyncio
async def test_put_me_rejects_unknown_extra_field(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    private_key, _ = rsa_keypair

    user = await _create_user(
        db_session,
        "profile-api-extra-field-subject",
        "profile-extra-field@example.com",
    )

    token = _build_token(private_key, sub=user.keycloak_subject)
    payload = _profile_payload(unexpected_field="not part of the contract")

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.put(
                "/v1/users/me",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 422
        assert await _count_profiles_for(db_session, user.id) == 0
    finally:
        app.dependency_overrides.clear()

        await db_session.delete(user)
        await db_session.commit()


@pytest.mark.parametrize("minutes", [1, 1440])
@pytest.mark.asyncio
async def test_put_me_accepts_boundary_daily_minutes(
    db_session,
    rsa_keypair,
    fake_jwks,
    minutes,
):
    private_key, _ = rsa_keypair

    user = await _create_user(
        db_session,
        f"profile-api-boundary-{minutes}-subject",
        f"profile-boundary-{minutes}@example.com",
    )

    token = _build_token(private_key, sub=user.keycloak_subject)
    payload = _profile_payload(daily_available_minutes=minutes)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.put(
                "/v1/users/me",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        assert response.json()["daily_available_minutes"] == minutes
    finally:
        app.dependency_overrides.clear()

        await db_session.delete(user)
        await db_session.commit()


def test_openapi_documents_get_me_error_responses():
    client = TestClient(app)
    spec = client.get("/openapi.json").json()

    responses = spec["paths"]["/v1/users/me"]["get"]["responses"]

    assert "200" in responses
    assert "401" in responses
    assert "404" in responses


def test_openapi_documents_put_me_error_responses():
    client = TestClient(app)
    spec = client.get("/openapi.json").json()

    responses = spec["paths"]["/v1/users/me"]["put"]["responses"]

    assert "200" in responses
    assert "401" in responses
    assert "404" in responses
    assert "422" in responses


@pytest.mark.asyncio
async def test_profile_endpoints_do_not_require_any_role(
    db_session,
    rsa_keypair,
    fake_jwks,
):
    """Self-service endpoints: a token with no role claim at all still manages
    its own profile. RBAC guards exist for role-restricted resources, not here."""
    private_key, _ = rsa_keypair

    user = await _create_user(
        db_session,
        "profile-api-no-role-subject",
        "profile-no-role@example.com",
    )

    token = _build_token(
        private_key,
        sub=user.keycloak_subject,
        missing_claims=["realm_access"],
    )

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            put_response = await client.put(
                "/v1/users/me",
                json=_profile_payload(),
                headers={"Authorization": f"Bearer {token}"},
            )

            assert put_response.status_code == 200
            assert put_response.json()["user_id"] == str(user.id)

            get_response = await client.get(
                "/v1/users/me",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert get_response.status_code == 200
            assert get_response.json()["user_id"] == str(user.id)
    finally:
        app.dependency_overrides.clear()

        await db_session.delete(user)
        await db_session.commit()
