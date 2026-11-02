"""Retrieval search endpoint (Week 10 foundation).

Owner-only semantic search across one course's processed materials:

    POST /v1/courses/{course_id}/materials/search

Conventions follow ``app/api/materials.py``: bearer authentication via
``get_current_user``, course authorization via ``require_owned_course``
(missing course → 404 before ownership; non-owner → 403), and authorization
runs **before** any embedding or vector-store access.

Retrieval has its own per-user rate budget (``limit_retrieval``, independent
counters from the write limiter). It is a read endpoint, but each request
triggers embedding inference plus one vector query per material, so it is
metered. Provider failures propagate unchanged — they never become
fabricated empty results.
"""

import uuid

from fastapi import APIRouter, Depends, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_owned_course
from app.api.rate_limit import limit_retrieval
from app.db.session import get_db
from app.models.user import User
from app.schemas.retrieval import (
    RetrievalSearchRequest,
    RetrievalSearchResponse,
)
from app.services.retrieval_service import search_course_materials

router = APIRouter(
    prefix="/v1/courses/{course_id}/materials",
    tags=["retrieval"],
)

# 422 is documented by FastAPI automatically (validation error schema); these
# document the auth/authorization/rate-limit failures raised manually.
_RETRIEVAL_ERROR_RESPONSES = {
    401: {"description": "Not authenticated (missing or invalid bearer token)"},
    403: {"description": "Insufficient permissions (course ownership required)"},
    404: {"description": "Course does not exist"},
    429: {"description": "Too many requests (per-user retrieval rate limit)"},
}


@router.post(
    "/search",
    response_model=RetrievalSearchResponse,
    responses=_RETRIEVAL_ERROR_RESPONSES,
    dependencies=[Depends(limit_retrieval)],
)
async def search_materials_handler(
    course_id: uuid.UUID,
    payload: RetrievalSearchRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RetrievalSearchResponse:
    """Search one course's materials by semantic similarity.

    Course ownership is enforced (404/403, ``app.api.deps.require_owned_course``)
    before embedding or vector access. Results may come from any material of
    the course whose vectors exist; no matching content yields a successful
    200 with an empty ``results`` array.
    """
    course = await require_owned_course(db, course_id, user)
    results = await search_course_materials(
        db,
        course_id=course.id,
        query=payload.query,
        top_k=payload.top_k,
    )
    return RetrievalSearchResponse(course_id=course.id, results=results)
