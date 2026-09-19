from typing import Any

import uuid

from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_instructor
from app.config import settings
from app.db.session import get_db
from app.models.course import Course
from app.models.user import User
from app.schemas.material import (
    MaterialCreate,
    MaterialResponse,
    UploadUrlCreate,
    UploadUrlResponse,
)
from app.services import storage
from app.services.course_service import get_course_by_id
from app.services.material_service import (
    build_material_s3_key,
    create_material,
    is_material_s3_key_for_course,
)

router = APIRouter(
    prefix="/v1/courses/{course_id}/materials",
    tags=["materials"],
)

# 422 is documented by FastAPI automatically (validation error schema); these
# document the auth/rbac/resolution failures raised manually.
_MATERIAL_ERROR_RESPONSES = {
    401: {"description": "Not authenticated (missing or invalid bearer token)"},
    403: {"description": "Insufficient permissions (instructor role and course ownership required)"},
    404: {"description": "No local user for the authenticated identity, or course does not exist"},
}


async def _require_owned_course(
    db: AsyncSession,
    course_id: uuid.UUID,
    user: User,
) -> Course:
    course = await get_course_by_id(db, course_id)
    if course is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    if course.owner_id != user.id:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return course


@router.post(
    "/upload-url",
    response_model=UploadUrlResponse,
    responses=_MATERIAL_ERROR_RESPONSES,
)
async def create_upload_url_handler(
    course_id: uuid.UUID,
    payload: UploadUrlCreate,
    user: User = Depends(get_current_user),
    _: dict[str, Any] = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
) -> UploadUrlResponse:
    course = await _require_owned_course(db, course_id, user)

    # The object key is generated server-side inside the course's namespace;
    # the client only supplies the display filename.
    s3_key = build_material_s3_key(course.id, payload.filename)
    upload_url = storage.generate_upload_url(s3_key)

    return UploadUrlResponse(
        course_id=course.id,
        title=payload.title,
        s3_key=s3_key,
        upload_url=upload_url,
        expires_in=settings.s3_url_expiration_seconds,
    )


@router.post(
    "",
    response_model=MaterialResponse,
    status_code=http_status.HTTP_201_CREATED,
    responses={**_MATERIAL_ERROR_RESPONSES, 409: {"description": "Material already registered"}},
)
async def register_material_handler(
    course_id: uuid.UUID,
    payload: MaterialCreate,
    user: User = Depends(get_current_user),
    _: dict[str, Any] = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
) -> MaterialResponse:
    course = await _require_owned_course(db, course_id, user)

    if not is_material_s3_key_for_course(course.id, payload.s3_key):
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="s3_key does not belong to this course's materials namespace",
        )

    try:
        material = await create_material(
            db,
            course_id=course.id,
            title=payload.title,
            s3_key=payload.s3_key,
            uploaded_by=user.id,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="A material with this s3_key is already registered",
        ) from None

    return MaterialResponse.model_validate(material)