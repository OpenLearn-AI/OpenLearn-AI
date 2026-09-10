import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.user import User


@pytest.mark.asyncio
async def test_create_and_read_user(db_session):
    user = User(
        keycloak_issuer="http://localhost:8080/realms/openlearn",
        keycloak_subject="db-test-subject",
        email="db-test@example.com",
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert isinstance(user.id, uuid.UUID)
    assert user.keycloak_issuer == "http://localhost:8080/realms/openlearn"
    assert user.keycloak_subject == "db-test-subject"
    assert user.email == "db-test@example.com"
    assert user.preferred_lang == "en"
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
        keycloak_issuer="http://localhost:8080/realms/openlearn",
        keycloak_subject="unique-test-subject-1",
        email="unique-test@example.com",
    )
    second_user = User(
        keycloak_issuer="http://localhost:8080/realms/openlearn",
        keycloak_subject="unique-test-subject-2",
        email="unique-test@example.com",
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
async def test_keycloak_identity_must_be_unique(db_session):
    first_user = User(
        keycloak_issuer="http://localhost:8080/realms/openlearn",
        keycloak_subject="same-subject",
        email="identity-test-1@example.com",
    )
    second_user = User(
        keycloak_issuer="http://localhost:8080/realms/openlearn",
        keycloak_subject="same-subject",
        email="identity-test-2@example.com",
    )

    db_session.add(first_user)
    await db_session.commit()

    db_session.add(second_user)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()

    await db_session.delete(first_user)
    await db_session.commit()
