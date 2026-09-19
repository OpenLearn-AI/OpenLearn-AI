"""Week 6 course persistence helpers.

Plain SQLAlchemy accessors matching the style of ``profile_service``: small,
explicit functions over an async session with straightforward commit/refresh.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate


async def list_courses(db: AsyncSession) -> list[Course]:
    result = await db.execute(
        select(Course).order_by(Course.created_at.desc(), Course.id)
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
    await db.delete(course)
    await db.commit()