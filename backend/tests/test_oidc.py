from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import uuid

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from httpx2 import ASGITransport, AsyncClient
from sqlalchemy import select

from app.config import settings
from app.db.session import get_db
from app.main import app
from app.models.user import User
from app.services.auth import oidc

from app.api.deps import require_admin, require_instructor, require_student, get_current_oidc_claims
from fastapi import HTTPException, Depends

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

    monkeypatch.setattr(oidc, "_JWK_CLIENT", FakeJwksClient())

    return FakeJwksClient


def _build_token(
    private_key: str,
    *,
    sub: str | None = "123e4567-e89b-12d3-a456-426614174000",
    iss: str = ISSUER,
    aud: str = AUDIENCE,
    expires_in_minutes: int = 15,
    extra: dict | None = None,
    algorithm: str = "RS256",
    missing_claims: list[str] | None = None,
) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": sub,
        "iss": iss,
        "aud": aud,
        "iat": now,
        "exp": now + timedelta(minutes=expires_in_minutes),
        "preferred_username": "student1",
        "email": "student1@openlearn.dev",
        "realm_access": {"roles": ["student"]},
    }

    if sub is None:
        payload.pop("sub")

    if missing_claims:
        for claim in missing_claims:
            payload.pop(claim, None)

    if extra:
        payload.update(extra)

    return jwt.encode(
        payload,
        private_key,
        algorithm=algorithm,
    )


def test_valid_token_returns_claims(fake_jwks, rsa_keypair) -> None:
    private_key, _ = rsa_keypair

    claims = oidc.decode_access_token(
        _build_token(private_key)
    )

    assert claims["sub"] == "123e4567-e89b-12d3-a456-426614174000"
    assert claims["iss"] == ISSUER
    assert claims["aud"] == AUDIENCE
    assert oidc.extract_roles(claims) == ["student"]


def test_rejects_wrong_issuer(fake_jwks, rsa_keypair) -> None:
    private_key, _ = rsa_keypair

    with pytest.raises(ValueError, match="Invalid access token"):
        oidc.decode_access_token(
            _build_token(
                private_key,
                iss="https://evil.example/realms/openlearn",
            )
        )


def test_rejects_wrong_audience(fake_jwks, rsa_keypair) -> None:
    private_key, _ = rsa_keypair

    with pytest.raises(ValueError, match="Invalid access token"):
        oidc.decode_access_token(
            _build_token(
                private_key,
                aud="some-other-client",
            )
        )


def test_rejects_expired_token(fake_jwks, rsa_keypair) -> None:
    private_key, _ = rsa_keypair

    with pytest.raises(ValueError, match="Invalid access token"):
        oidc.decode_access_token(
            _build_token(
                private_key,
                expires_in_minutes=-5,
            )
        )


def test_rejects_missing_subject(fake_jwks, rsa_keypair) -> None:
    private_key, _ = rsa_keypair

    with pytest.raises(ValueError, match="Invalid access token"):
        oidc.decode_access_token(
            _build_token(
                private_key,
                sub=None,
            )
        )


@pytest.mark.parametrize(
    "missing_claim",
    ["exp", "iat", "iss", "aud"],
)
def test_rejects_missing_required_claims(
    fake_jwks,
    rsa_keypair,
    missing_claim: str,
) -> None:
    private_key, _ = rsa_keypair

    with pytest.raises(ValueError, match="Invalid access token"):
        oidc.decode_access_token(
            _build_token(
                private_key,
                missing_claims=[missing_claim],
            )
        )


def test_rejects_unverifiable_signature(
    fake_jwks,
    rsa_keypair,
    monkeypatch,
) -> None:
    private_key, _ = rsa_keypair

    class FailingJwksClient:
        def get_signing_key_from_jwt(self, token):
            raise jwt.PyJWKClientError("no key found")

    monkeypatch.setattr(
        oidc,
        "_JWK_CLIENT",
        FailingJwksClient(),
    )

    with pytest.raises(
        ValueError,
        match="Could not resolve the token signing key",
    ):
        oidc.decode_access_token(
            _build_token(private_key)
        )


def _second_private_key_pem() -> str:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")


def test_rejects_token_signed_with_different_key(fake_jwks) -> None:
    with pytest.raises(ValueError, match="Invalid access token"):
        oidc.decode_access_token(
            _build_token(_second_private_key_pem())
        )


def test_rejects_unsupported_algorithm(fake_jwks) -> None:
    with pytest.raises(ValueError, match="Invalid access token"):
        oidc.decode_access_token(
            _build_token(
                "s" * 32,
                algorithm="HS256",
            )
        )


def test_extract_roles_returns_empty_when_absent() -> None:
    assert oidc.extract_roles({}) == []
    assert oidc.extract_roles({"realm_access": {}}) == []


def test_extract_roles_returns_empty_for_malformed_realm_access() -> None:
    assert oidc.extract_roles({"realm_access": "nonsense"}) == []
    assert oidc.extract_roles({"realm_access": {"roles": "student"}}) == []


def test_extract_roles_filters_non_string_roles() -> None:
    roles = oidc.extract_roles(
        {
            "realm_access": {
                "roles": ["student", 42, None, "admin", ""],
            },
        }
    )

    assert roles == ["student", "admin"]


@pytest.mark.asyncio
async def test_me_endpoint_with_valid_token(
    fake_jwks,
    rsa_keypair,
    db_session,
) -> None:
    private_key, _ = rsa_keypair

    subject = "123e4567-e89b-12d3-a456-426614174000"

    user = User(
        keycloak_issuer=ISSUER,
        keycloak_subject=subject,
        email="student1@openlearn.dev",
        preferred_lang="en",
        settings={"theme": "dark"},
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

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
                "/auth/me",
                headers={
                    "Authorization": f"Bearer {_build_token(private_key)}"
                },
            )

        assert response.status_code == 200

        payload = response.json()

        assert payload["id"] == str(user.id)
        assert payload["email"] == "student1@openlearn.dev"
        assert payload["preferred_lang"] == "en"
        assert payload["settings"] == {"theme": "dark"}
        assert payload["roles"] == ["student"]

        assert payload["keycloak"]["issuer"] == ISSUER
        assert payload["keycloak"]["subject"] == subject

        assert "password" not in payload
        assert "token" not in payload
        assert "password_hash" not in payload

    finally:
        app.dependency_overrides.clear()

        await db_session.delete(user)
        await db_session.commit()


@pytest.mark.asyncio
async def test_me_endpoint_jit_creates_new_user(
    fake_jwks,
    rsa_keypair,
    db_session,
) -> None:
    private_key, _ = rsa_keypair

    subject = "e2e-jit-0f8ad9c6-4f2a-4f3b-9d1e-2c1b3a4d5e6f"

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
                "/auth/me",
                headers={
                    "Authorization": f"Bearer {_build_token(private_key, sub=subject)}"
                },
            )

        assert response.status_code == 200

        payload = response.json()

        assert payload["email"] == "student1@openlearn.dev"
        assert payload["preferred_lang"] == "en"
        assert payload["settings"] == {}
        assert payload["roles"] == ["student"]
        assert payload["keycloak"]["issuer"] == ISSUER
        assert payload["keycloak"]["subject"] == subject

        result = await db_session.execute(
            select(User).where(User.keycloak_subject == subject)
        )
        saved_user = result.scalar_one()

        assert saved_user is not None
        assert saved_user.id == uuid.UUID(payload["id"])
        assert saved_user.email == "student1@openlearn.dev"

        await db_session.delete(saved_user)
        await db_session.commit()
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_student_role_is_authorized(
    fake_jwks,
    rsa_keypair,
) -> None:
    private_key, _ = rsa_keypair

    claims = oidc.decode_access_token(
        _build_token(
            private_key,
            extra={
                "realm_access": {
                    "roles": ["student"],
                },
            },
        )
    )

    result = require_student(claims)

    assert result["sub"] == "123e4567-e89b-12d3-a456-426614174000"


@pytest.mark.asyncio
async def test_student_role_is_forbidden_from_instructor(
    fake_jwks,
    rsa_keypair,
) -> None:
    private_key, _ = rsa_keypair

    claims = oidc.decode_access_token(
        _build_token(
            private_key,
            extra={
                "realm_access": {
                    "roles": ["student"],
                },
            },
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        require_instructor(claims)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_instructor_role_is_authorized(
    fake_jwks,
    rsa_keypair,
) -> None:
    private_key, _ = rsa_keypair

    claims = oidc.decode_access_token(
        _build_token(
            private_key,
            extra={
                "realm_access": {
                    "roles": ["instructor"],
                },
            },
        )
    )

    result = require_instructor(claims)

    assert result["sub"] == "123e4567-e89b-12d3-a456-426614174000"


@pytest.mark.asyncio
async def test_admin_role_is_authorized(
    fake_jwks,
    rsa_keypair,
) -> None:
    private_key, _ = rsa_keypair

    claims = oidc.decode_access_token(
        _build_token(
            private_key,
            extra={
                "realm_access": {
                    "roles": ["admin"],
                },
            },
        )
    )

    result = require_admin(claims)

    assert result["sub"] == "123e4567-e89b-12d3-a456-426614174000"


@pytest.mark.asyncio
async def test_missing_role_is_forbidden(
    fake_jwks,
    rsa_keypair,
) -> None:
    private_key, _ = rsa_keypair

    claims = oidc.decode_access_token(
        _build_token(
            private_key,
            extra={
                "realm_access": {
                    "roles": [],
                },
            },
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        require_student(claims)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_rbac_http_boundary(
    fake_jwks,
    rsa_keypair,
) -> None:
    private_key, _ = rsa_keypair

    from fastapi import FastAPI

    test_app = FastAPI()

    @test_app.get("/student")
    async def student_endpoint(
        claims: dict = Depends(get_current_oidc_claims),
    ):
        return {"sub": claims["sub"]}

    @test_app.get("/instructor")
    async def instructor_endpoint(
        claims: dict = Depends(require_instructor),
    ):
        return {"sub": claims["sub"]}

    @test_app.get("/admin")
    async def admin_endpoint(
        claims: dict = Depends(require_admin),
    ):
        return {"sub": claims["sub"]}

    transport = ASGITransport(app=test_app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get("/student")
        assert response.status_code == 401

        student_token = _build_token(
            private_key,
            extra={
                "realm_access": {
                    "roles": ["student"],
                },
            },
        )

        response = await client.get(
            "/instructor",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert response.status_code == 403

        instructor_token = _build_token(
            private_key,
            extra={
                "realm_access": {
                    "roles": ["instructor"],
                },
            },
        )

        response = await client.get(
            "/instructor",
            headers={"Authorization": f"Bearer {instructor_token}"},
        )
        assert response.status_code == 200

        admin_token = _build_token(
            private_key,
            extra={
                "realm_access": {
                    "roles": ["admin"],
                },
            },
        )

        response = await client.get(
            "/admin",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_malformed_bearer_credentials_return_401(
    fake_jwks,
    rsa_keypair,
) -> None:
    from fastapi import FastAPI

    test_app = FastAPI()

    @test_app.get("/ping")
    async def ping_endpoint(
        claims: dict = Depends(get_current_oidc_claims),
    ):
        return {"sub": claims["sub"]}

    transport = ASGITransport(app=test_app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        malformed_headers = [
            {"Authorization": "Bearer not-a-jwt"},
            {"Authorization": "Basic dXNlcjpwYXNz"},
            {"Authorization": "Bearer"},
        ]

        for headers in malformed_headers:
            response = await client.get("/ping", headers=headers)
            assert response.status_code == 401
            assert response.headers.get("www-authenticate") == "Bearer"
            assert response.json()["detail"] == "Not authenticated"