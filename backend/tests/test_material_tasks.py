"""Week 7 Celery worker task tests.

``app.workers.tasks.material_tasks`` imports ``app.workers.celery_app``, which
raises at import time unless ``REDIS_PASSWORD`` is set, so the environment
variable is configured *before* the module import below. Importing the module
only registers the task; no Redis broker is contacted. ``_handle_material`` is
exercised directly to avoid ``asyncio.run`` (which cannot nest) and any broker
dispatch.

The worker owns its database session through the module-level
``AsyncSessionLocal``, whose engine is shared at import time. pytest-asyncio
creates a fresh event loop per test, and asyncpg connections are loop-bound, so
reusing that shared engine across tests breaks. Each test therefore
monkeypatches ``material_tasks.AsyncSessionLocal`` to a per-test factory bound
to a fresh engine created inside that test's loop.
"""

import os
import uuid

os.environ.setdefault("REDIS_PASSWORD", "test-redis-password")

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings  # noqa: E402
from app.models.course import Course  # noqa: E402
from app.models.material import (  # noqa: E402
    FAILED_STATUS,
    PENDING_STATUS,
    PROCESSING_STATUS,
    READY_STATUS,
    Material,
)
from app.models.user import User  # noqa: E402
from app.workers import publishing  # noqa: E402
from app.workers.tasks import material_tasks  # noqa: E402

ISSUER = "http://localhost:8080/realms/openlearn"


@pytest_asyncio.fixture
async def worker_session_factory():
    engine = create_async_engine(settings.database_url)
    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    try:
        yield factory
    finally:
        await engine.dispose()


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


@pytest.mark.asyncio
async def test_process_material_drives_pending_to_ready_and_commits(
    db_session, worker_session_factory, monkeypatch
):
    monkeypatch.setattr(
        material_tasks, "AsyncSessionLocal", worker_session_factory
    )

    owner = await _create_user(
        db_session, "material-task-ready-owner", "material-task-ready@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    s3_key = material.s3_key

    calls = []

    async def fake_process_content(inner_material, inner_s3_key, course_id, owner_id):
        calls.append((inner_material.id, inner_s3_key, course_id, owner_id))

    monkeypatch.setattr(material_tasks, "_process_material_content", fake_process_content)

    status = await material_tasks._handle_material(
        str(material.id),
        s3_key,
        str(course.id),
        str(owner.id),
    )

    assert status == READY_STATUS

    await db_session.refresh(material)
    assert material.status == READY_STATUS

    assert calls == [(material.id, s3_key, str(course.id), str(owner.id))]

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_process_material_failure_marks_failed_and_propagates(
    db_session, worker_session_factory, monkeypatch
):
    monkeypatch.setattr(
        material_tasks, "AsyncSessionLocal", worker_session_factory
    )

    owner = await _create_user(
        db_session, "material-task-fail-owner", "material-task-fail@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    s3_key = material.s3_key

    async def failing_process_content(*args, **kwargs):
        raise RuntimeError("content pipeline boom")

    monkeypatch.setattr(material_tasks, "_process_material_content", failing_process_content)

    with pytest.raises(RuntimeError, match="content pipeline boom"):
        await material_tasks._handle_material(
            str(material.id),
            s3_key,
            str(course.id),
            str(owner.id),
        )

    await db_session.refresh(material)
    assert material.status == FAILED_STATUS

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_process_material_aborts_when_material_missing(
    db_session, worker_session_factory, monkeypatch
):
    monkeypatch.setattr(
        material_tasks, "AsyncSessionLocal", worker_session_factory
    )

    calls = []

    async def recording_process_content(*args, **kwargs):
        calls.append(args)

    monkeypatch.setattr(material_tasks, "_process_material_content", recording_process_content)

    status = await material_tasks._handle_material(
        str(uuid.uuid4()),
        "courses/x/materials/none.pdf",
        str(uuid.uuid4()),
        str(uuid.uuid4()),
    )

    assert status is None
    assert calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("initial_status", [READY_STATUS, PROCESSING_STATUS])
async def test_process_material_rejects_invalid_transition_and_leaves_status_unchanged(
    db_session, worker_session_factory, monkeypatch, initial_status
):
    monkeypatch.setattr(
        material_tasks, "AsyncSessionLocal", worker_session_factory
    )

    owner = await _create_user(
        db_session, "material-task-guard-owner", "material-task-guard@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner, status=initial_status)
    s3_key = material.s3_key

    calls = []

    async def recording_process_content(*args, **kwargs):
        calls.append(True)

    monkeypatch.setattr(material_tasks, "_process_material_content", recording_process_content)

    with pytest.raises(ValueError, match="Invalid material status transition"):
        await material_tasks._handle_material(
            str(material.id),
            s3_key,
            str(course.id),
            str(owner.id),
        )

    await db_session.refresh(material)
    assert material.status == initial_status
    assert calls == []

    await db_session.delete(owner)
    await db_session.commit()


def test_process_material_registered_under_publishing_task_name():
    assert material_tasks.process_material.name == publishing.MATERIAL_PROCESSING_TASK_NAME
    assert material_tasks.process_material.name == (
        "app.workers.tasks.material_tasks.process_material"
    )
    assert publishing.MATERIAL_PROCESSING_TASK_NAME in material_tasks.celery_app.tasks