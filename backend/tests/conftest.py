import uuid
from types import SimpleNamespace

import pytest
import pytest_asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.models.course import Course
from app.models.material import PENDING_STATUS, Material
from app.models.user import User
from app.services.auth import oidc as oidc_module

# Celery-app importability for the whole suite (Redis settings contract).
#
# ``app.workers.celery_app`` resolves its Redis URL through
# ``app.config.Settings.redis_connection_url`` and raises at import time when
# neither ``REDIS_URL`` nor ``REDIS_PASSWORD`` can be resolved from the
# process environment, backend/.env, or the repository-root .env.local. Tests
# must never depend on developer-local env files, so give the shared settings
# instance a deterministic dummy password before any test module imports the
# Celery app (this conftest is imported first, and the guard below also makes
# single-file runs like ``pytest tests/test_material_tasks.py`` work in a
# clean checkout). Individual tests override these fields with
# ``monkeypatch.setattr(settings, ...)``, which monkeypatch restores.
if not settings.redis_url and not settings.redis_password:
    settings.redis_password = "test-redis-password"


# PAL provider selection is likewise developer-configurable: backend/.env
# legitimately points the real pipeline at bge-m3 / postgres (and could point
# OCR/reasoning at gemini/litellm). Tests that assert the factory's
# "defaults to settings" selection or that drive the wired pipeline with the
# mock store must not depend on that local choice. Requesting this fixture
# selects the mock providers explicitly through the SAME settings contract the
# factory reads (monkeypatch restores the original values afterwards), so the
# production defaults and application behavior are untouched.
_MOCK_AI_PROVIDER_FIELDS = (
    "ai_ocr_provider",
    "ai_embedding_provider",
    "ai_reasoning_provider",
    "ai_vector_db_provider",
)


@pytest.fixture
def mock_ai_providers(monkeypatch: pytest.MonkeyPatch) -> None:
    for field in _MOCK_AI_PROVIDER_FIELDS:
        monkeypatch.setattr(settings, field, "mock")


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
    )
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session

    await engine.dispose()


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


async def _delete_user_by_subject(db, subject: str) -> None:
    """Defensively remove a user by Keycloak subject to keep tests repeatable."""
    result = await db.execute(
        select(User).where(User.keycloak_subject == subject)
    )
    for user in result.scalars():
        await db.delete(user)
    await db.commit()


async def _create_user(db, subject: str, email: str) -> User:
    await _delete_user_by_subject(db, subject)

    user = User(
        keycloak_issuer=settings.keycloak_issuer,
        keycloak_subject=subject,
        email=email,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def _create_material(
    db,
    course: Course,
    owner: User,
    *,
    status: str = PENDING_STATUS,
    sha256: str | None = None,
    s3_etag: str | None = None,
) -> Material:
    material = Material(
        course_id=course.id,
        title="Lecture Slides",
        s3_key=f"courses/{course.id}/materials/{uuid.uuid4()}-slides.pdf",
        uploaded_by=owner.id,
        status=status,
        sha256=sha256,
        s3_etag=s3_etag,
    )
    db.add(material)
    await db.commit()
    await db.refresh(material)
    return material

@pytest.fixture(autouse=True)
def _reset_write_rate_limits():
    """The per-user write rate limiter is process-global state."""
    from app.api.rate_limit import reset_rate_limits

    reset_rate_limits()
    yield
    reset_rate_limits()
