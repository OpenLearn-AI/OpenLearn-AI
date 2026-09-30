from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models.user import User


class KeycloakIdentityError(ValueError):
    """A token could not be resolved to an OpenLearn user.

    These are defensive failures for identities that are already
    signature/issuer/audience validated, so they are caller-caused and must
    surface as 4xx rather than 500. They subclass ``ValueError`` so the
    service contract (and its existing callers) is unchanged.
    """


class MissingIdentityError(KeycloakIdentityError):
    """The token carries no issuer or subject to resolve a user by."""


class MissingEmailError(KeycloakIdentityError):
    """The token carries no email, so no user row can be created."""


class DuplicateEmailError(KeycloakIdentityError):
    """Another OpenLearn user already owns the email in the token."""


async def get_user_by_keycloak_identity(
    db: AsyncSession,
    claims: dict[str, Any],
) -> User | None:
    issuer = claims.get("iss")
    subject = claims.get("sub")

    if not issuer:
        raise MissingIdentityError("Keycloak issuer is missing.")

    if not subject:
        raise MissingIdentityError("Keycloak subject is missing.")

    result = await db.execute(
        select(User).where(
            User.keycloak_issuer == issuer,
            User.keycloak_subject == subject,
        )
    )

    return result.scalar_one_or_none()


async def get_or_create_user_from_keycloak(
    db: AsyncSession,
    claims: dict[str, Any],
) -> User:
    issuer = claims.get("iss")
    subject = claims.get("sub")
    email = claims.get("email")

    if not issuer:
        raise MissingIdentityError("Keycloak issuer is missing.")

    if not subject:
        raise MissingIdentityError("Keycloak subject is missing.")

    if not email:
        raise MissingEmailError("Keycloak email is missing.")

    user = await get_user_by_keycloak_identity(
        db,
        claims,
    )

    if user is not None:
        email_verified = bool(claims.get("email_verified", False))

        if user.email_verified != email_verified:
            user.email_verified = email_verified
            await db.commit()
            await db.refresh(user)

        return user

    existing_email_result = await db.execute(
        select(User).where(User.email == email)
    )
    existing_email_user = existing_email_result.scalar_one_or_none()

    if existing_email_user is not None:
        raise DuplicateEmailError(
            "A different OpenLearn user already uses this email address."
        )

    email_verified = bool(claims.get("email_verified", False))

    user = User(
        keycloak_issuer=issuer,
        keycloak_subject=subject,
        email=email,
        email_verified=email_verified,
    )

    db.add(user)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()

        user = await get_user_by_keycloak_identity(
            db,
            claims,
        )

        if user is not None:
            return user

        raise

    await db.refresh(user)

    return user