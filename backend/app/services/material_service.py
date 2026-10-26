"""Week 6 material persistence and S3 key helpers.

A material lives inside a single course's S3 namespace:
``courses/{course_id}/materials/{uuid}-{safe_filename}``. Keys are generated
server-side; the client never chooses an arbitrary object key.

Week 9 adds course-scoped content deduplication (``sha256``), the manual
retry budget (``retry_count``), and per-page output (``material_pages``).
"""

import os
import re
import uuid
from collections.abc import Iterable, Sequence
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.material import (
    FAILED_STATUS,
    MATERIAL_RETRY_LIMIT,
    PENDING_STATUS,
    PROCESSING_STATUS,
    READY_STATUS,
    Material,
)
from app.models.material_page import MaterialPage

_ALLOWED_TRANSITIONS = {
    PENDING_STATUS: {PROCESSING_STATUS},
    # Week 9: processing -> pending is the automatic-retry hand-back.
    PROCESSING_STATUS: {READY_STATUS, FAILED_STATUS, PENDING_STATUS},
}

_KEY_PREFIX_TEMPLATE = "courses/{course_id}/materials/"
_SAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")


def _safe_filename(filename: str) -> str:
    """Reduce a client filename to a single safe basename for S3 key use."""
    name = os.path.basename(filename or "").strip()
    name = _SAFE_CHARS.sub("_", name)
    name = name.strip("._")
    return name[:60] or "upload"


def material_key_prefix(course_id: uuid.UUID) -> str:
    return _KEY_PREFIX_TEMPLATE.format(course_id=course_id)


def build_material_s3_key(course_id: uuid.UUID, filename: str) -> str:
    return f"{material_key_prefix(course_id)}{uuid.uuid4()}-{_safe_filename(filename)}"


def is_material_s3_key_for_course(course_id: uuid.UUID, s3_key: str) -> bool:
    """A key is only acceptable for registration if it lives in this course's
    server-owned namespace. A client cannot point at another course's objects
    or an arbitrary path."""
    prefix = material_key_prefix(course_id)
    return s3_key.startswith(prefix) and len(s3_key) > len(prefix)


async def create_material(
    db: AsyncSession,
    *,
    course_id: uuid.UUID,
    title: str,
    s3_key: str,
    uploaded_by: uuid.UUID,
    sha256: str | None = None,
    s3_etag: str | None = None,
) -> Material:
    # TODO(future phase): real virus/content scanning. Week 6 registers the
    # object as ``pending`` only; scan/processing is a later phase.
    material = Material(
        course_id=course_id,
        title=title,
        s3_key=s3_key,
        status=PENDING_STATUS,
        uploaded_by=uploaded_by,
        sha256=sha256,
        s3_etag=s3_etag,
    )
    db.add(material)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    await db.refresh(material)
    return material


async def get_material_by_id(
    db: AsyncSession,
    material_id: uuid.UUID,
) -> Material | None:
    result = await db.execute(
        select(Material).where(Material.id == material_id)
    )
    return result.scalar_one_or_none()


async def claim_pending_material(
    db: AsyncSession,
    material_id: uuid.UUID,
) -> Material | None:
    """Atomically claim a pending material for processing (W8).

    The claim is a single conditional UPDATE that makes the ``pending`` ->
    ``processing`` transition and only matches rows still ``pending`` at
    execution time, so concurrent workers can never claim the same material
    twice. The claim is committed before returning; the returned material is
    already persisted as ``processing``. Returns ``None`` when there is no
    pending material to claim (including when another worker already claimed
    it).
    """
    result = await db.execute(
        update(Material)
        .where(Material.id == material_id, Material.status == PENDING_STATUS)
        .values(status=PROCESSING_STATUS)
        .returning(Material.id)
        .execution_options(synchronize_session=False)
    )
    if result.scalar_one_or_none() is None:
        return None
    await db.commit()
    material = await get_material_by_id(db, material_id)
    await db.refresh(material)
    return material


async def list_materials_by_course(
    db: AsyncSession,
    course_id: uuid.UUID,
) -> list[Material]:
    """Return all materials for a course, newest first (id as tiebreak)."""
    result = await db.execute(
        select(Material)
        .where(Material.course_id == course_id)
        .order_by(Material.created_at.desc(), Material.id)
    )
    return list(result.scalars().all())


async def transition_material_status(
    db: AsyncSession,
    material: Material,
    new_status: str,
) -> Material:
    allowed_statuses = _ALLOWED_TRANSITIONS.get(material.status, set())

    if new_status not in allowed_statuses:
        raise ValueError(
            f"Invalid material status transition: "
            f"{material.status!r} -> {new_status!r}"
        )

    material.status = new_status
    await db.flush()
    return material


async def find_material_by_content_hash(
    db: AsyncSession,
    course_id: uuid.UUID,
    sha256: str,
) -> Material | None:
    """Return the material holding ``sha256`` in ``course_id`` (Week 9 dedup)."""
    result = await db.execute(
        select(Material).where(
            Material.course_id == course_id,
            Material.sha256 == sha256,
        )
    )
    return result.scalar_one_or_none()


async def is_s3_key_referenced(
    db: AsyncSession,
    s3_key: str,
) -> bool:
    """True when a material row references ``s3_key`` (guards duplicate-object deletion)."""
    result = await db.execute(
        select(Material.id).where(Material.s3_key == s3_key).limit(1)
    )
    return result.first() is not None


async def claim_material_retry(
    db: AsyncSession,
    material_id: uuid.UUID,
) -> Material | None:
    """Atomically claim one manual retry (Week 9).

    Single conditional UPDATE: only ``ready``/``failed`` rows below the
    retry limit move to ``pending`` with ``retry_count + 1``, so concurrent
    claims cannot both succeed. Committed before returning (F8). Returns
    None when the material is missing, ineligible, or out of budget.
    """
    result = await db.execute(
        update(Material)
        .where(
            Material.id == material_id,
            Material.status.in_([READY_STATUS, FAILED_STATUS]),
            Material.retry_count < MATERIAL_RETRY_LIMIT,
        )
        .values(
            status=PENDING_STATUS,
            retry_count=Material.retry_count + 1,
        )
        .returning(Material.retry_count)
        .execution_options(synchronize_session=False)
    )
    claimed_retry_count = result.scalar_one_or_none()
    if claimed_retry_count is None:
        return None
    await db.commit()
    material = await get_material_by_id(db, material_id)
    await db.refresh(material)
    return material


async def restore_material_after_publish_failure(
    db: AsyncSession,
    material_id: uuid.UUID,
    *,
    previous_status: str,
    claimed_retry_count: int,
) -> bool:
    """Undo a retry claim whose queue publication failed.

    Applied only while the row is still ``pending`` with the claimed count,
    so a job the worker already picked up is never reverted.
    """
    result = await db.execute(
        update(Material)
        .where(
            Material.id == material_id,
            Material.status == PENDING_STATUS,
            Material.retry_count == claimed_retry_count,
        )
        .values(
            status=previous_status,
            retry_count=claimed_retry_count - 1,
        )
        .returning(Material.id)
        .execution_options(synchronize_session=False)
    )
    restored = result.scalar_one_or_none() is not None
    if restored:
        await db.commit()
    else:
        await db.rollback()
    return restored


async def count_nonempty_material_pages(
    db: AsyncSession,
    material_id: uuid.UUID,
) -> int:
    """Number of stored pages with non-whitespace text (Week 9 keep-more rule)."""
    result = await db.execute(
        select(func.count())
        .select_from(MaterialPage)
        .where(
            MaterialPage.material_id == material_id,
            MaterialPage.text.regexp_match(r"\S"),
        )
    )
    return int(result.scalar_one())


async def replace_material_pages(
    db: AsyncSession,
    material_id: uuid.UUID,
    pages: Iterable[tuple[int, str]],
) -> int:
    """Replace a material's stored pages, empty pages included (Week 9).

    Flush only, never commit: the pages commit with the caller's ``ready``
    transition and are discarded by its rollback on failure.
    Returns the number of page rows written.
    """
    await db.execute(
        delete(MaterialPage).where(MaterialPage.material_id == material_id)
    )

    stored = 0
    for page_number, text in sorted(pages):
        db.add(
            MaterialPage(
                material_id=material_id,
                page_number=page_number,
                text=text or "",
            )
        )
        stored += 1
    await db.flush()
    return stored


async def list_material_pages(
    db: AsyncSession,
    material_id: uuid.UUID,
    limit: int | None = None,
    offset: int = 0,
) -> Sequence[MaterialPage]:
    """Return a material's stored pages in ascending page order.

    ``limit``/``offset`` page through large documents (``limit=None`` returns
    everything from ``offset``).
    """
    stmt = (
        select(MaterialPage)
        .where(MaterialPage.material_id == material_id)
        .order_by(MaterialPage.page_number.asc())
        .offset(offset)
    )
    if limit is not None:
        stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_material_page(
    db: AsyncSession,
    material_id: uuid.UUID,
    page_number: int,
) -> MaterialPage | None:
    result = await db.execute(
        select(MaterialPage).where(
            MaterialPage.material_id == material_id,
            MaterialPage.page_number == page_number,
        )
    )
    return result.scalar_one_or_none()


async def fail_stuck_materials(
    db: AsyncSession,
    older_than: timedelta,
) -> list[uuid.UUID]:
    """Mark materials stuck in ``pending``/``processing`` as ``failed``.

    A row is stuck when it has not changed for ``older_than`` (a lost enqueue
    or a worker killed past the Celery time limits). One conditional UPDATE,
    committed; the owner can then use the manual retry. Returns the ids moved.
    """
    cutoff = datetime.now(UTC) - older_than
    result = await db.execute(
        update(Material)
        .where(
            Material.status.in_([PENDING_STATUS, PROCESSING_STATUS]),
            Material.updated_at < cutoff,
        )
        .values(status=FAILED_STATUS)
        .returning(Material.id)
        .execution_options(synchronize_session=False)
    )
    stuck_ids = list(result.scalars().all())
    await db.commit()
    return stuck_ids
