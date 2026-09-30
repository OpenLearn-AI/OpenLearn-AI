"""Week 6 material persistence and S3 key helpers.

A material lives inside a single course's S3 namespace:
``courses/{course_id}/materials/{uuid}-{safe_filename}``. Keys are generated
server-side; the client never chooses an arbitrary object key.
"""

import os
import re
import uuid

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.material import (
    FAILED_STATUS,
    PENDING_STATUS,
    PROCESSING_STATUS,
    READY_STATUS,
    Material,
)

_ALLOWED_TRANSITIONS = {
    PENDING_STATUS: {PROCESSING_STATUS},
    PROCESSING_STATUS: {READY_STATUS, FAILED_STATUS},
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
) -> Material:
    # TODO(future phase): real virus/content scanning. Week 6 registers the
    # object as ``pending`` only; scan/processing is a later phase.
    material = Material(
        course_id=course_id,
        title=title,
        s3_key=s3_key,
        status=PENDING_STATUS,
        uploaded_by=uploaded_by,
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
