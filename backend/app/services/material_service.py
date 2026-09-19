"""Week 6 material persistence and S3 key helpers.

A material lives inside a single course's S3 namespace:
``courses/{course_id}/materials/{uuid}-{safe_filename}``. Keys are generated
server-side; the client never chooses an arbitrary object key.
"""

import os
import re
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.material import Material, PENDING_STATUS

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