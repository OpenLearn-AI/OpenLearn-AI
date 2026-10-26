from typing import Any

import asyncio
import structlog
import uuid

from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status as http_status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_instructor, require_owned_course
from app.api.rate_limit import limit_writes
from app.config import settings
from app.db.session import get_db
from app.models.material import (
    MATERIAL_RETRY_LIMIT,
    PENDING_STATUS,
    PROCESSING_STATUS,
)
from app.models.user import User
from app.schemas.material import (
    MaterialAcceptedResponse,
    MaterialCreate,
    MaterialPageResponse,
    MaterialPagesResponse,
    MaterialResponse,
    MaterialStatusResponse,
    UploadUrlCreate,
    UploadUrlResponse,
)
from app.services import storage
from app.services.storage import MaterialObjectChangedError
from app.services.material_service import (
    build_material_s3_key,
    claim_material_retry,
    create_material,
    find_material_by_content_hash,
    get_material_by_id,
    get_material_page,
    is_material_s3_key_for_course,
    is_s3_key_referenced,
    list_material_pages,
    list_materials_by_course,
    restore_material_after_publish_failure,
)
from app.workers.publishing import (
    MATERIAL_PROCESSING_TASK_NAME,
    enqueue_material_processing,
)

logger = structlog.get_logger(__name__)

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

#: botocore error codes for a missing stored object (Week 9 hashing).
_OBJECT_MISSING_ERROR_CODES = {"NoSuchKey", "NotFound", "404"}


def _stored_object_missing(exc: ClientError) -> bool:
    error = exc.response.get("Error", {}) or {}
    code = str(error.get("Code", ""))
    if code in _OBJECT_MISSING_ERROR_CODES:
        return True
    http_code = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    return http_code == 404


def _missing_object_error() -> HTTPException:
    return HTTPException(
        status_code=http_status.HTTP_404_NOT_FOUND,
        detail=(
            "No object is stored for the provided s3_key; upload it "
            "through the presigned URL before registering"
        ),
    )


async def _delete_verified_duplicate_object(
    db: AsyncSession,
    course_id: uuid.UUID,
    duplicate_s3_key: str,
    canonical_s3_key: str,
) -> None:
    """Delete a just-uploaded duplicate object (Week 9 dedup).

    Skipped when it is the canonical key, outside the course namespace, or
    referenced by any material row. Deletion failures are only logged.
    """
    if duplicate_s3_key == canonical_s3_key:
        return
    if not is_material_s3_key_for_course(course_id, duplicate_s3_key):
        return
    if await is_s3_key_referenced(db, duplicate_s3_key):
        return
    try:
        await asyncio.to_thread(storage.delete_material_object, duplicate_s3_key)
    except Exception:
        logger.warning(
            "duplicate_material_object_delete_failed",
            course_id=str(course_id),
            s3_key=duplicate_s3_key,
        )


async def _reuse_existing_material(
    db: AsyncSession,
    course_id: uuid.UUID,
    uploaded_s3_key: str,
    canonical,
) -> MaterialAcceptedResponse:
    await _delete_verified_duplicate_object(
        db, course_id, uploaded_s3_key, canonical.s3_key
    )
    return MaterialAcceptedResponse(
        material_id=canonical.id,
        job_id=None,
        status=canonical.status,
    )


status_router = APIRouter(
    prefix="/v1/materials",
    tags=["materials"],
)

# The status read requires course ownership (through the shared
# ``require_owned_course`` helper); no instructor role dependency is added.
_MATERIAL_STATUS_ERROR_RESPONSES = {
    401: {"description": "Not authenticated (missing or invalid bearer token)"},
    403: {"description": "Insufficient permissions (course ownership required)"},
    404: {"description": "Material does not exist"},
}

_MATERIAL_PROCESS_ERROR_RESPONSES = {
    401: {"description": "Not authenticated (missing or invalid bearer token)"},
    403: {"description": "Insufficient permissions (instructor role and course ownership required)"},
    404: {"description": "Material does not exist"},
    409: {
        "description": (
            "Material is already queued or processing, or the manual retry "
            f"budget is exhausted ({MATERIAL_RETRY_LIMIT} manual retries "
            "consumed); nothing was enqueued"
        )
    },
    429: {"description": "Too many requests (per-user write rate limit)"},
}


@router.post(
    "/upload-url",
    response_model=UploadUrlResponse,
    responses={
        **_MATERIAL_ERROR_RESPONSES,
        429: {"description": "Too many requests (per-user write rate limit)"},
    },
    dependencies=[Depends(limit_writes)],
)
async def create_upload_url_handler(
    course_id: uuid.UUID,
    payload: UploadUrlCreate,
    user: User = Depends(get_current_user),
    _: dict[str, Any] = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
) -> UploadUrlResponse:
    course = await require_owned_course(db, course_id, user)

    # The object key is generated server-side inside the course's namespace;
    # the client only supplies the display filename.
    s3_key = build_material_s3_key(course.id, payload.filename)
    upload = storage.generate_upload_post(s3_key)

    return UploadUrlResponse(
        course_id=course.id,
        title=payload.title,
        s3_key=s3_key,
        upload_url=upload["url"],
        upload_fields=upload["fields"],
        max_size_bytes=settings.max_upload_size_bytes,
        expires_in=settings.s3_url_expiration_seconds,
    )


@router.post(
    "",
    response_model=MaterialAcceptedResponse,
    status_code=http_status.HTTP_202_ACCEPTED,
    responses={
        **_MATERIAL_ERROR_RESPONSES,
        409: {
            "description": (
                "Material already registered, or the stored object changed "
                "while it was being registered"
            )
        },
        413: {"description": "Stored object exceeds the maximum upload size"},
        429: {"description": "Too many requests (per-user write rate limit)"},
    },
    dependencies=[Depends(limit_writes)],
)
async def register_material_handler(
    course_id: uuid.UUID,
    payload: MaterialCreate,
    user: User = Depends(get_current_user),
    _: dict[str, Any] = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
) -> MaterialAcceptedResponse:
    """Register an uploaded object for processing.

    Week 9: a file whose content already exists in this course returns the
    existing material (``job_id=None``, current status) and enqueues nothing,
    whatever that material's status is.
    """
    course = await require_owned_course(db, course_id, user)

    if not is_material_s3_key_for_course(course.id, payload.s3_key):
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="s3_key does not belong to this course's materials namespace",
        )

    # Week 9 dedup: hash the stored object server-side (never client-supplied).
    # HEAD first: it gives the size (cap checked before any bytes are read)
    # and the ETag. The hash is then read with If-Match on that ETag, so it
    # describes exactly that object version; the ETag is stored and the worker
    # reads with the same If-Match (an object replaced later is not processed).
    try:
        stored = await asyncio.to_thread(
            storage.get_material_object_info, payload.s3_key
        )
    except ClientError as exc:
        if _stored_object_missing(exc):
            raise _missing_object_error() from None
        raise

    if stored.size > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=http_status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                "Stored object exceeds the maximum upload size of "
                f"{settings.max_upload_size_bytes} bytes"
            ),
        )

    try:
        content_sha256 = await asyncio.to_thread(
            storage.compute_material_sha256, payload.s3_key, stored.etag
        )
    except MaterialObjectChangedError:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="The stored object changed while it was being registered; retry",
        ) from None
    except ClientError as exc:
        if _stored_object_missing(exc):
            raise _missing_object_error() from None
        raise

    canonical = await find_material_by_content_hash(db, course.id, content_sha256)
    if canonical is not None:
        return await _reuse_existing_material(db, course.id, payload.s3_key, canonical)

    try:
        material = await create_material(
            db,
            course_id=course.id,
            title=payload.title,
            s3_key=payload.s3_key,
            uploaded_by=user.id,
            sha256=content_sha256,
            s3_etag=stored.etag,
        )
    except IntegrityError:
        # A concurrent registration of the same content won the
        # (course_id, sha256) race: return that material instead of 409.
        # (course_id, not course.id: the rollback expired the ORM instance.)
        canonical = await find_material_by_content_hash(db, course_id, content_sha256)
        if canonical is not None:
            return await _reuse_existing_material(
                db, course_id, payload.s3_key, canonical
            )
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="A material with this s3_key is already registered",
        ) from None

    # Commit-before-publish contract (F8): the material is committed ``pending``
    # by ``create_material`` before Celery publish is attempted. A publish
    # failure leaves that committed ``pending`` row in place and the request
    # returns 500 without a job id. Broker acceptance followed by an error
    # remains a possible at-least-once tail: the worker may still process it.
    try:
        job_id = await enqueue_material_processing(
            material.id,
            material.s3_key,
            material.course_id,
            material.uploaded_by,
        )
    except Exception:
        logger.exception(
            "material_processing_enqueue_failed",
            material_id=str(material.id),
            course_id=str(material.course_id),
            task_name=MATERIAL_PROCESSING_TASK_NAME,
        )
        raise
    return MaterialAcceptedResponse(
        material_id=material.id,
        job_id=job_id,
        status=material.status,
    )


@router.get(
    "",
    response_model=list[MaterialResponse],
    responses=_MATERIAL_ERROR_RESPONSES,
)
async def list_materials_handler(
    course_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_owned_course(db, course_id, user)
    materials = await list_materials_by_course(db, course_id)
    return materials


@status_router.get(
    "/{material_id}/status",
    response_model=MaterialStatusResponse,
    responses=_MATERIAL_STATUS_ERROR_RESPONSES,
)
async def get_material_status_handler(
    material_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MaterialStatusResponse:
    material = await get_material_by_id(db, material_id)
    if material is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Material not found",
        )
    await require_owned_course(db, material.course_id, user)
    return MaterialStatusResponse(
        material_id=material.id,
        status=material.status,
    )


@status_router.get(
    "/{material_id}/pages",
    response_model=MaterialPagesResponse,
    responses=_MATERIAL_STATUS_ERROR_RESPONSES,
)
async def get_material_pages_handler(
    material_id: uuid.UUID,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MaterialPagesResponse:
    """List a material's stored pages, ascending (Week 9). Empty until processed.

    Paginated: at most ``limit`` pages (default 100, max 500) starting after
    ``offset`` pages; a shorter page than ``limit`` means the last page.
    """
    material = await get_material_by_id(db, material_id)
    if material is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Material not found",
        )
    await require_owned_course(db, material.course_id, user)

    pages = await list_material_pages(db, material.id, limit=limit, offset=offset)
    return MaterialPagesResponse(
        material_id=material.id,
        pages=[
            MaterialPageResponse(page_number=page.page_number, text=page.text)
            for page in pages
        ],
    )


@status_router.get(
    "/{material_id}/pages/{page_number}",
    response_model=MaterialPageResponse,
    responses={
        **_MATERIAL_STATUS_ERROR_RESPONSES,
        404: {"description": "Material or page does not exist"},
    },
)
async def get_material_page_handler(
    material_id: uuid.UUID,
    page_number: int = Path(ge=1),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MaterialPageResponse:
    """Read one stored page of a material (Week 9)."""
    material = await get_material_by_id(db, material_id)
    if material is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Material not found",
        )
    await require_owned_course(db, material.course_id, user)

    page = await get_material_page(db, material.id, page_number)
    if page is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )
    return MaterialPageResponse(page_number=page.page_number, text=page.text)


@status_router.post(
    "/{material_id}/process",
    response_model=MaterialAcceptedResponse,
    status_code=http_status.HTTP_202_ACCEPTED,
    responses=_MATERIAL_PROCESS_ERROR_RESPONSES,
    dependencies=[Depends(limit_writes)],
)
async def process_material_handler(
    material_id: uuid.UUID,
    user: User = Depends(get_current_user),
    _: dict[str, Any] = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
) -> MaterialAcceptedResponse:
    """Manually retry processing of a ``ready``/``failed`` material (Week 9).

    Course owner only; at most ``MATERIAL_RETRY_LIMIT`` manual retries. 409
    while already pending/processing and 409 when the budget is exhausted.
    """
    material = await get_material_by_id(db, material_id)
    if material is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Material not found",
        )
    await require_owned_course(db, material.course_id, user)

    previous_status = material.status
    claimed = await claim_material_retry(db, material.id)
    if claimed is None:
        # Nothing claimed: report why (deleted, in flight, or out of budget).
        current = await get_material_by_id(db, material_id)
        if current is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Material not found",
            )
        if current.status in (PENDING_STATUS, PROCESSING_STATUS):
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail=(
                    "Material is already queued or processing "
                    f"(current status: {current.status})"
                ),
            )
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail=(
                "Manual retry budget exhausted "
                f"({current.retry_count} of {MATERIAL_RETRY_LIMIT} "
                "manual retries consumed)"
            ),
        )

    # Commit-before-publish (F8): a publish failure undoes the claim.
    try:
        job_id = await enqueue_material_processing(
            claimed.id,
            claimed.s3_key,
            claimed.course_id,
            claimed.uploaded_by,
        )
    except Exception:
        logger.exception(
            "material_process_enqueue_failed",
            material_id=str(claimed.id),
            course_id=str(claimed.course_id),
            task_name=MATERIAL_PROCESSING_TASK_NAME,
        )
        await restore_material_after_publish_failure(
            db,
            claimed.id,
            previous_status=previous_status,
            claimed_retry_count=claimed.retry_count,
        )
        raise
    return MaterialAcceptedResponse(
        material_id=claimed.id,
        job_id=job_id,
        status=claimed.status,
    )