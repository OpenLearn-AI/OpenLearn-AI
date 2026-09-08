import uuid

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.models.user import User


@pytest_asyncio.fixture
async def db_session():
    # Create an engine per test to avoid reusing asyncpg connections
    # across pytest event loops on Windows.
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


@pytest.mark.asyncio
async def test_create_and_read_user(db_session):
    user = User(
        email="db-test@example.com",
        password_hash="test-password-hash",
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert isinstance(user.id, uuid.UUID)
    assert user.email == "db-test@example.com"
    assert user.password_hash == "test-password-hash"
    assert user.preferred_lang == "en"
    assert user.role == "student"
    assert user.settings == {}

    result = await db_session.execute(
        select(User).where(User.email == "db-test@example.com")
    )
    saved_user = result.scalar_one()

    assert saved_user.id == user.id

    await db_session.delete(saved_user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_email_must_be_unique(db_session):
    first_user = User(
        email="unique-test@example.com",
        password_hash="hash-1",
    )
    second_user = User(
        email="unique-test@example.com",
        password_hash="hash-2",
    )

    db_session.add(first_user)
    await db_session.commit()

    db_session.add(second_user)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()

    await db_session.delete(first_user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_password_hash_cannot_be_null(db_session):
    user = User(
        email="null-password-test@example.com",
        password_hash=None,
    )

    db_session.add(user)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()
