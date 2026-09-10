import pytest
import asyncio

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.models.user import User
from app.services.auth.user_service import (
    get_or_create_user_from_keycloak,
    get_user_by_keycloak_identity,
)
from app.config import settings


async def _delete_user_by_identity(db, subject: str) -> None:
    """Defensively remove a user by Keycloak subject to keep tests repeatable."""
    await db.execute(
        delete(User).where(User.keycloak_subject == subject)
    )
    await db.commit()



@pytest.mark.asyncio
async def test_get_user_by_keycloak_identity_returns_existing_user(db_session):
    user = User(
        keycloak_issuer="http://localhost:8080/realms/openlearn",
        keycloak_subject="lookup-test-subject",
        email="lookup-test@example.com",
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    claims = {
        "iss": "http://localhost:8080/realms/openlearn",
        "sub": "lookup-test-subject",
    }

    result = await get_user_by_keycloak_identity(db_session, claims)

    assert result is not None
    assert result.id == user.id

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_get_user_by_keycloak_identity_returns_none_for_unknown_user(db_session):
    claims = {
        "iss": "http://localhost:8080/realms/openlearn",
        "sub": "unknown-subject",
    }

    result = await get_user_by_keycloak_identity(db_session, claims)

    assert result is None


@pytest.mark.asyncio
async def test_get_user_by_keycloak_identity_rejects_missing_issuer(db_session):
    claims = {
        "sub": "lookup-test-subject",
    }

    with pytest.raises(ValueError, match="Keycloak issuer is missing"):
        await get_user_by_keycloak_identity(db_session, claims)


@pytest.mark.asyncio
async def test_get_user_by_keycloak_identity_rejects_missing_subject(db_session):
    claims = {
        "iss": "http://localhost:8080/realms/openlearn",
    }

    with pytest.raises(ValueError, match="Keycloak subject is missing"):
        await get_user_by_keycloak_identity(db_session, claims)


@pytest.mark.asyncio
async def test_get_or_create_user_returns_existing_user(db_session):
    user = User(
        keycloak_issuer="http://localhost:8080/realms/openlearn",
        keycloak_subject="existing-jit-subject",
        email="existing-jit@example.com",
        email_verified=True,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    claims = {
        "iss": "http://localhost:8080/realms/openlearn",
        "sub": "existing-jit-subject",
        "email": "existing-jit@example.com",
        "email_verified": True,
    }

    result = await get_or_create_user_from_keycloak(
        db_session,
        claims,
    )

    assert result.id == user.id
    assert result.email == "existing-jit@example.com"

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_get_or_create_user_creates_new_user(db_session):
    claims = {
        "iss": "http://localhost:8080/realms/openlearn",
        "sub": "new-jit-subject",
        "email": "new-jit@example.com",
        "email_verified": True,
    }

    result = await get_or_create_user_from_keycloak(
        db_session,
        claims,
    )

    assert result.id is not None
    assert result.keycloak_issuer == (
        "http://localhost:8080/realms/openlearn"
    )
    assert result.keycloak_subject == "new-jit-subject"
    assert result.email == "new-jit@example.com"
    assert result.email_verified is True
    assert result.preferred_lang == "en"
    assert result.settings == {}

    await db_session.delete(result)
    await db_session.commit()


@pytest.mark.asyncio
async def test_get_or_create_user_rejects_email_collision(db_session):
    existing_user = User(
        keycloak_issuer="http://localhost:8080/realms/openlearn",
        keycloak_subject="email-collision-existing-subject",
        email="email-collision@example.com",
    )

    db_session.add(existing_user)
    await db_session.commit()

    claims = {
        "iss": "http://localhost:8080/realms/openlearn",
        "sub": "email-collision-new-subject",
        "email": "email-collision@example.com",
        "email_verified": True,
    }

    with pytest.raises(
        ValueError,
        match="A different OpenLearn user already uses this email address",
    ):
        await get_or_create_user_from_keycloak(
            db_session,
            claims,
        )

    await db_session.delete(existing_user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_get_or_create_user_rejects_missing_email(db_session):
    claims = {
        "iss": "http://localhost:8080/realms/openlearn",
        "sub": "missing-email-subject",
    }

    with pytest.raises(ValueError, match="Keycloak email is missing"):
        await get_or_create_user_from_keycloak(
            db_session,
            claims,
        )


@pytest.mark.asyncio
async def test_get_or_create_user_syncs_email_verified_false_to_true(db_session):
    subject = "verify-upgrade-subject"
    email = "verify-upgrade@example.com"

    await _delete_user_by_identity(db_session, subject)

    user = User(
        keycloak_issuer="http://localhost:8080/realms/openlearn",
        keycloak_subject=subject,
        email=email,
        email_verified=False,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    claims = {
        "iss": "http://localhost:8080/realms/openlearn",
        "sub": subject,
        "email": email,
        "email_verified": True,
    }

    try:
        result = await get_or_create_user_from_keycloak(
            db_session,
            claims,
        )

        assert result.id == user.id
        assert result.email_verified is True
    finally:
        await _delete_user_by_identity(db_session, subject)


@pytest.mark.asyncio
async def test_get_or_create_user_syncs_email_verified_true_to_false(db_session):
    subject = "verify-downgrade-subject"
    email = "verify-downgrade@example.com"

    await _delete_user_by_identity(db_session, subject)

    user = User(
        keycloak_issuer="http://localhost:8080/realms/openlearn",
        keycloak_subject=subject,
        email=email,
        email_verified=True,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    claims = {
        "iss": "http://localhost:8080/realms/openlearn",
        "sub": subject,
        "email": email,
        "email_verified": False,
    }

    try:
        result = await get_or_create_user_from_keycloak(
            db_session,
            claims,
        )

        assert result.id == user.id
        assert result.email_verified is False
    finally:
        await _delete_user_by_identity(db_session, subject)


@pytest.mark.asyncio
async def test_email_verified_unchanged_does_not_write(db_session, monkeypatch):
    subject = "verify-unchanged-subject"
    email = "verify-unchanged@example.com"

    await _delete_user_by_identity(db_session, subject)

    user = User(
        keycloak_issuer="http://localhost:8080/realms/openlearn",
        keycloak_subject=subject,
        email=email,
        email_verified=True,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    claims = {
        "iss": "http://localhost:8080/realms/openlearn",
        "sub": subject,
        "email": email,
        "email_verified": True,
    }

    async def fail_on_write(*args, **kwargs):
        raise AssertionError("An unexpected DB write occurred.")

    try:
        monkeypatch.setattr(db_session, "commit", fail_on_write)

        result = await get_or_create_user_from_keycloak(
            db_session,
            claims,
        )

        assert result.id == user.id
        assert result.email_verified is True
    finally:
        monkeypatch.undo()
        await _delete_user_by_identity(db_session, subject)


@pytest.mark.asyncio
async def test_get_or_create_user_recovers_after_losing_race(db_session, monkeypatch):
    claims = {
        "iss": "http://localhost:8080/realms/openlearn",
        "sub": "race-recovery-subject",
        "email": "race-recovery@example.com",
        "email_verified": True,
    }

    winner = User(
        keycloak_issuer=claims["iss"],
        keycloak_subject=claims["sub"],
        email=claims["email"],
        email_verified=True,
    )

    lookups = {"count": 0}

    async def fake_lookup(session, c):
        lookups["count"] += 1
        return None if lookups["count"] == 1 else winner

    async def losing_commit(*args, **kwargs):
        raise IntegrityError(
            "INSERT INTO users",
            {},
            Exception(
                "duplicate key value violates unique constraint"
                "uq_users_keycloak_identity"
            ),
        )

    monkeypatch.setattr(
        "app.services.auth.user_service.get_user_by_keycloak_identity",
        fake_lookup,
    )
    monkeypatch.setattr(db_session, "commit", losing_commit)

    result = await get_or_create_user_from_keycloak(db_session, claims)

    assert result.id == winner.id
    assert result.keycloak_subject == claims["sub"]
    assert lookups["count"] == 2


@pytest.mark.asyncio
async def test_concurrent_jit_provisioning_returns_same_user():
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
    )
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    claims = {
        "iss": "http://localhost:8080/realms/openlearn",
        "sub": "concurrent-jit-subject",
        "email": "concurrent-jit@example.com",
        "email_verified": True,
    }

    async def provision_user():
        async with session_factory() as session:
            return await get_or_create_user_from_keycloak(
                session,
                claims,
            )

    try:
        async with session_factory() as session:
            await session.execute(
                delete(User).where(
                    User.keycloak_issuer == claims["iss"],
                    User.keycloak_subject == claims["sub"],
                )
            )
            await session.commit()

        user_a, user_b = await asyncio.gather(
            provision_user(),
            provision_user(),
        )

        assert user_a.id == user_b.id
        assert user_a.keycloak_issuer == claims["iss"]
        assert user_a.keycloak_subject == claims["sub"]

        async with session_factory() as session:
            count_result = await session.execute(
                select(func.count())
                .select_from(User)
                .where(
                    User.keycloak_issuer == claims["iss"],
                    User.keycloak_subject == claims["sub"],
                )
            )

            assert count_result.scalar_one() == 1

            user = await get_user_by_keycloak_identity(
                session,
                claims,
            )

            assert user is not None
    finally:
        async with session_factory() as session:
            await session.execute(
                delete(User).where(
                    User.keycloak_issuer == claims["iss"],
                    User.keycloak_subject == claims["sub"],
                )
            )
            await session.commit()
        await engine.dispose()