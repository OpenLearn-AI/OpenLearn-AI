from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.profile import ProfileResponse, ProfileUpdate
from app.services.profile_service import get_profile_by_user_id, replace_profile

router = APIRouter(prefix="/v1/users", tags=["users"])

# 422 is documented by FastAPI automatically (validation error schema); these
# document the auth/resolution failures raised manually inside the dependencies.
_PROFILE_ERROR_RESPONSES = {
    401: {"description": "Not authenticated (missing or invalid bearer token)"},
    404: {"description": "No local user for the authenticated identity, or no profile exists"},
}


@router.get(
    "/me",
    response_model=ProfileResponse,
    responses=_PROFILE_ERROR_RESPONSES,
)
async def read_my_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    profile = await get_profile_by_user_id(db, user.id)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return ProfileResponse.model_validate(profile)


@router.put(
    "/me",
    response_model=ProfileResponse,
    responses=_PROFILE_ERROR_RESPONSES,
)
async def replace_my_profile(
    payload: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    # The profile owner always comes from the authenticated identity; the
    # request body cannot influence it.
    profile = await replace_profile(db, user.id, payload)

    return ProfileResponse.model_validate(profile)
