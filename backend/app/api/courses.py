import uuid

from fastapi import APIRouter, Depends, Response, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_owned_course
from app.api.rate_limit import limit_writes
from app.db.session import get_db
from app.models.user import User
from app.schemas.course import CourseCreate, CourseResponse, CourseUpdate
from app.services.course_service import (
    create_course,
    delete_course,
    list_courses,
    replace_course,
)

router = APIRouter(prefix="/v1/courses", tags=["courses"])

# 422 is documented by FastAPI automatically (validation error schema); these
# document the auth/rbac/resolution failures raised manually. The mapping is
# shared by every course route, but 403 is only reachable on the
# ownership-protected by-id routes (GET/PUT/DELETE /v1/courses/{course_id}):
# listing is scoped to the authenticated owner inside the query, and POST
# /v1/courses is open to any authenticated user and takes no ownership check.
_COURSE_ERROR_RESPONSES = {
    401: {"description": "Not authenticated (missing or invalid bearer token)"},
    403: {"description": "Insufficient permissions (owner-only GET/PUT/DELETE by course id; POST /v1/courses never rejects on role or ownership)"},
    404: {"description": "No local user for the authenticated identity, or course does not exist"},
}


@router.post(
    "",
    response_model=CourseResponse,
    status_code=http_status.HTTP_201_CREATED,
    responses={
        **_COURSE_ERROR_RESPONSES,
        429: {"description": "Too many requests (per-user write rate limit)"},
    },
    dependencies=[Depends(limit_writes)],
)
async def create_course_handler(
    payload: CourseCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # owner_id always comes from the authenticated local user; the request
    # body cannot influence it (CourseCreate rejects extra fields).
    # The ORM object is returned directly: ``response_model`` serializes it.
    course = await create_course(db, owner_id=user.id, payload=payload)
    return course


@router.get(
    "",
    response_model=list[CourseResponse],
    responses=_COURSE_ERROR_RESPONSES,
)
async def list_courses_handler(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Owner-scoped listing: only the authenticated user's own courses are
    # selected, in the database query itself. The local ``user.id`` (not the
    # Keycloak ``sub``) is the ownership reference.
    courses = await list_courses(db, owner_id=user.id)
    return courses


@router.get(
    "/{course_id}",
    response_model=CourseResponse,
    responses=_COURSE_ERROR_RESPONSES,
)
async def get_course_handler(
    course_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Same owner-only check as PUT/DELETE: a missing course is a 404, a
    # course owned by someone else is a 403, and no other user's course
    # data (title, description, owner_id) is ever serialized.
    course = await require_owned_course(db, course_id, user)
    return course


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
):
    course = await require_owned_course(db, course_id, user)
    course = await replace_course(db, course, payload)
    return course


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
    course = await require_owned_course(db, course_id, user)
    await delete_course(db, course)
    return Response(status_code=http_status.HTTP_204_NO_CONTENT)
