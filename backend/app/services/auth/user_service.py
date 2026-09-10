from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models.user import User


async def get_user_by_keycloak_identity(
    db: AsyncSession,
    claims: dict[str, Any],
) -> User | None:
    issuer = claims.get("iss")
    subject = claims.get("sub")

    if not issuer:
        raise ValueError("Keycloak issuer is missing.")

    if not subject:
        raise ValueError("Keycloak subject is missing.")

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
        raise ValueError("Keycloak issuer is missing.")

    if not subject:
        raise ValueError("Keycloak subject is missing.")

    if not email:
        raise ValueError("Keycloak email is missing.")

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
        raise ValueError(
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