import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_instructor
from app.db.session import get_db
from app.models.user import User
from app.schemas.course import CourseCreate, CourseResponse, CourseUpdate
from app.services.course_service import (
    create_course,
    delete_course,
    get_course_by_id,
    list_courses,
    replace_course,
)

router = APIRouter(prefix="/v1/courses", tags=["courses"])

# 422 is documented by FastAPI automatically (validation error schema); these
# document the auth/rbac/resolution failures raised manually.
_COURSE_ERROR_RESPONSES = {
    401: {"description": "Not authenticated (missing or invalid bearer token)"},
    403: {"description": "Insufficient permissions (instructor role or course ownership required)"},
    404: {"description": "No local user for the authenticated identity, or course does not exist"},
}


@router.post(
    "",
    response_model=CourseResponse,
    status_code=http_status.HTTP_201_CREATED,
    responses=_COURSE_ERROR_RESPONSES,
)
async def create_course_handler(
    payload: CourseCreate,
    user: User = Depends(get_current_user),
    _: dict = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
) -> CourseResponse:
    # owner_id always comes from the authenticated local user; the request
    # body cannot influence it (CourseCreate rejects extra fields).
    course = await create_course(db, owner_id=user.id, payload=payload)
    return CourseResponse.model_validate(course)


@router.get(
    "",
    response_model=list[CourseResponse],
    responses=_COURSE_ERROR_RESPONSES,
)
async def list_courses_handler(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CourseResponse]:
    courses = await list_courses(db)
    return [CourseResponse.model_validate(course) for course in courses]


@router.get(
    "/{course_id}",
    response_model=CourseResponse,
    responses=_COURSE_ERROR_RESPONSES,
)
async def get_course_handler(
    course_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CourseResponse:
    course = await get_course_by_id(db, course_id)
    if course is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    return CourseResponse.model_validate(course)


@router.put(
    "/{course_id}",
    response_model=CourseResponse,
    responses=_COURSE_ERROR_RESPONSES,
)
async def update_course_handler(
    course_id: uuid.UUID,
    payload: CourseUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CourseResponse:
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
    course = await replace_course(db, course, payload)
    return CourseResponse.model_validate(course)


@router.delete(
    "/{course_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
    responses=_COURSE_ERROR_RESPONSES,
)
async def delete_course_handler(
    course_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
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
    await delete_course(db, course)
    return Response(status_code=http_status.HTTP_204_NO_CONTENT)