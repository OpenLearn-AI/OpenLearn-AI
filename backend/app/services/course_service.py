"""Week 6 course persistence helpers.

Plain SQLAlchemy accessors matching the style of ``profile_service``: small,
explicit functions over an async session with straightforward commit/refresh.
"""

import asyncio
import uuid

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.material import Material
from app.pal.providers.vector_db.postgres_provider import PostgresVectorDBProvider
from app.schemas.course import CourseCreate, CourseUpdate
from app.services import storage

logger = structlog.get_logger(__name__)


async def list_courses(db: AsyncSession, owner_id: uuid.UUID) -> list[Course]:
    """List the courses owned by the given local user.

    Ownership scoping is part of the query itself against the indexed
    ``courses.owner_id`` column, so the database only ever returns the
    requesting user's rows; no post-fetch filtering and no caller-side
    decision can observe another user's courses.
    """
    result = await db.execute(
        select(Course)
        .where(Course.owner_id == owner_id)
        .order_by(Course.created_at.desc(), Course.id)
    )
    return list(result.scalars().all())


async def get_course_by_id(db: AsyncSession, course_id: uuid.UUID) -> Course | None:
    result = await db.execute(
        select(Course).where(Course.id == course_id)
    )
    return result.scalar_one_or_none()


async def create_course(
    db: AsyncSession,
    owner_id: uuid.UUID,
    payload: CourseCreate,
) -> Course:
    course = Course(
        owner_id=owner_id,
        title=payload.title,
        description=payload.description,
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


async def replace_course(
    db: AsyncSession,
    course: Course,
    payload: CourseUpdate,
) -> Course:
    """Full-replacement update: every editable column comes from the payload.

    Ownership (``owner_id``) is never assigned here; callers enforce it.
    """
    course.title = payload.title
    course.description = payload.description
    await db.commit()
    await db.refresh(course)
    return course


async def delete_course(db: AsyncSession, course: Course) -> None:
    """Delete a course with its materials, stored files and vectors.

    The rows cascade in the database, and the materials' vector records (no
    foreign key to materials) are deleted in the same transaction. The stored
    files are deleted from object storage after the commit; a storage failure
    is logged and never fails the request (the course is already gone).
    """
    result = await db.execute(
        select(Material.id, Material.s3_key).where(Material.course_id == course.id)
    )
    materials = result.all()

    vectors = PostgresVectorDBProvider(db)
    for material_id, _ in materials:
        await vectors.delete(filters={"material_id": str(material_id)})

    await db.delete(course)
    await db.commit()

    s3_keys = [s3_key for _, s3_key in materials]
    if not s3_keys:
        return
    try:
        failed = await asyncio.to_thread(storage.delete_material_objects, s3_keys)
    except Exception:
        logger.exception("course_objects_delete_failed", object_count=len(s3_keys))
        return
    if failed:
        logger.warning("course_objects_delete_incomplete", failed_keys=failed)