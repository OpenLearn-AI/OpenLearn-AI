import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Profile
from app.schemas.profile import ProfileUpdate


async def get_profile_by_user_id(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> Profile | None:
    result = await db.execute(
        select(Profile).where(Profile.user_id == user_id)
    )

    return result.scalar_one_or_none()


async def replace_profile(
    db: AsyncSession,
    user_id: uuid.UUID,
    payload: ProfileUpdate,
) -> Profile:
    """Create or fully replace the profile owned by ``user_id``.

    Every column is assigned from the payload, so omitted optional fields are
    cleared (full replacement, not PATCH). The unique constraint on
    ``profiles.user_id`` guarantees one profile per user; on a concurrent
    creation race the loser re-fetches the winner's row and re-applies the
    replacement, mirroring the retry pattern in the auth user service.
    """
    profile = await get_profile_by_user_id(db, user_id)

    if profile is None:
        profile = Profile(user_id=user_id)
        db.add(profile)

    _apply_payload(profile, payload)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()

        profile = await get_profile_by_user_id(db, user_id)

        if profile is None:
            raise

        _apply_payload(profile, payload)
        await db.commit()

    await db.refresh(profile)

    return profile


def _apply_payload(profile: Profile, payload: ProfileUpdate) -> None:
    profile.education_level = payload.education_level
    profile.major = payload.major
    profile.preferred_language = payload.preferred_language
    profile.university = payload.university
    profile.learning_style_vark = payload.learning_style_vark
    profile.daily_available_minutes = payload.daily_available_minutes
