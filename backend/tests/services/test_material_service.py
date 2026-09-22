"""Week 7 Material service tests.

Database-backed service tests for ``transition_material_status`` and
``get_material_by_id`` following the repository pattern: the shared ``db_session``
fixture from ``tests/conftest.py`` and real ORM rows with cascade-based cleanup
(see ``tests/test_database.py``).

``transition_material_status`` flushes but intentionally does not commit, so
these tests assert status mutation and the occurrence of ``db.flush`` only.
"""

import uuid

import pytest
from sqlalchemy import select

from app.models.course import Course
from app.models.material import (
    FAILED_STATUS,
    PENDING_STATUS,
    PROCESSING_STATUS,
    READY_STATUS,
    Material,
)
from app.models.user import User
from app.services.material_service import (
    get_material_by_id,
    transition_material_status,
)

ISSUER = "http://localhost:8080/realms/openlearn"


async def _delete_user_by_subject(db, subject: str) -> None:
    result = await db.execute(
        select(User).where(User.keycloak_subject == subject)
    )
    for user in result.scalars():
        await db.delete(user)
    await db.commit()


async def _create_user(db, subject: str, email: str) -> User:
    await _delete_user_by_subject(db, subject)

    user = User(
        keycloak_issuer=ISSUER,
        keycloak_subject=subject,
        email=email,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def _create_course(db, owner: User) -> Course:
    course = Course(
        owner_id=owner.id,
        title="Test Course",
        description="Slides",
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


async def _create_material(
    db,
    course: Course,
    owner: User,
    *,
    status: str = PENDING_STATUS,
) -> Material:
    material = Material(
        course_id=course.id,
        title="Lecture Slides",
        s3_key=f"courses/{course.id}/materials/{uuid.uuid4()}-slides.pdf",
        uploaded_by=owner.id,
        status=status,
    )
    db.add(material)
    await db.commit()
    await db.refresh(material)
    return material


def _spy_on_flush(db):
    """Record ``db.flush`` invocations while still performing the real flush."""
    calls = []
    real_flush = db.flush

    async def recording_flush(*args, **kwargs):
        calls.append(True)
        return await real_flush(*args, **kwargs)

    db.flush = recording_flush
    return calls


@pytest.mark.asyncio
async def test_pending_to_processing_succeeds(db_session):
    owner = await _create_user(
        db_session, "material-transition-pp-owner", "material-transition-pp@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    flush_calls = _spy_on_flush(db_session)

    result = await transition_material_status(db_session, material, PROCESSING_STATUS)

    assert result is material
    assert material.status == PROCESSING_STATUS
    assert flush_calls == [True]

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_processing_to_ready_succeeds(db_session):
    owner = await _create_user(
        db_session, "material-transition-pr-owner", "material-transition-pr@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(
        db_session, course, owner, status=PROCESSING_STATUS
    )
    flush_calls = _spy_on_flush(db_session)

    result = await transition_material_status(db_session, material, READY_STATUS)

    assert result is material
    assert material.status == READY_STATUS
    assert flush_calls == [True]

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_processing_to_failed_succeeds(db_session):
    owner = await _create_user(
        db_session, "material-transition-pf-owner", "material-transition-pf@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(
        db_session, course, owner, status=PROCESSING_STATUS
    )
    flush_calls = _spy_on_flush(db_session)

    result = await transition_material_status(db_session, material, FAILED_STATUS)

    assert result is material
    assert material.status == FAILED_STATUS
    assert flush_calls == [True]

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("initial_status", "invalid_target"),
    [
        (PENDING_STATUS, READY_STATUS),
        (PENDING_STATUS, FAILED_STATUS),
        (READY_STATUS, PROCESSING_STATUS),
        (FAILED_STATUS, PROCESSING_STATUS),
    ],
)
async def test_invalid_transitions_raise_value_error_and_leave_status_unchanged(
    db_session, initial_status, invalid_target
):
    owner = await _create_user(
        db_session, "material-transition-invalid-owner", "material-transition-invalid@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(
        db_session, course, owner, status=initial_status
    )
    flush_calls = _spy_on_flush(db_session)

    with pytest.raises(ValueError, match="Invalid material status transition"):
        await transition_material_status(db_session, material, invalid_target)

    assert material.status == initial_status
    assert flush_calls == []

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_get_material_by_id_returns_existing_material(db_session):
    owner = await _create_user(
        db_session, "material-lookup-owner", "material-lookup@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)

    result = await get_material_by_id(db_session, material.id)

    assert result is material
    assert result.id == material.id
    assert result.status == PENDING_STATUS

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_get_material_by_id_returns_none_for_unknown_id(db_session):
    result = await get_material_by_id(db_session, uuid.uuid4())

    assert result is None
