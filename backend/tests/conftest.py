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