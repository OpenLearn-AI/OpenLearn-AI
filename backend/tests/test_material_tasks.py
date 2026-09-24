"""Week 7 Celery worker task tests.

``app.workers.tasks.material_tasks`` imports ``app.workers.celery_app``, which
raises at import time unless ``REDIS_PASSWORD`` is set, so the environment
variable is configured *before* the module import below. Importing the module
only registers the task; no Redis broker is contacted. ``_handle_material`` is
exercised directly to avoid ``asyncio.run`` (which cannot nest) and any broker
dispatch.

The worker owns no module-level session machinery. Each ``process_material``
invocation builds a task-local async engine and session factory inside its own
event loop (``asyncio.run``) and disposes the engine before that loop closes, so
pooled asyncpg connections never survive from one task's loop into the next.
The lifecycle behavior tests exercise ``_handle_material`` directly with an
explicit per-test factory bound to a fresh engine created inside that test's
loop; the sequential regression test drives the real ``process_material.run()``
entrypoint twice in the same process to prove the task-local engine isolation.

Phase 1C: the DB-failure regression tests exercise real statement and flush
failures through ``_handle_material`` and require the original error to
propagate (after the material is recorded ``failed``) instead of a secondary
transaction/PendingRollback error that leaves the material ``processing``.

Phase 1D locked contract: re-processing a material that is already
``processing``, ``ready``, or ``failed`` is a no-op that returns the current
status string (never calls the content seam, never changes the persisted
status); a missing material returns ``None``. A separate delivery-
configuration tripwire guards the intended Celery settings.
"""

import asyncio
import os
import uuid

os.environ.setdefault("REDIS_PASSWORD", "test-redis-password")

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
import sqlalchemy  # noqa: E402
from sqlalchemy import select, text  # noqa: E402
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
from app.services.material_service import claim_pending_material  # noqa: E402
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


async def _read_material_status(material_id: uuid.UUID) -> str:
    """Read a material's persisted status through an independent engine.

    Phase 1C: persisted-state assertions must never reuse the session that
    failed mid-transaction; a fresh engine gives a connection-independent read.
    """
    engine = create_async_engine(settings.database_url)
    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    try:
        async with factory() as db:
            result = await db.execute(
                select(Material).where(Material.id == material_id)
            )
            material = result.scalar_one_or_none()
            return material.status if material else "missing"
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_process_material_drives_pending_to_ready_and_commits(
    db_session, worker_session_factory, monkeypatch
):

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
        session_factory=worker_session_factory,
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
            session_factory=worker_session_factory,
        )

    await db_session.refresh(material)
    assert material.status == FAILED_STATUS

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_process_material_aborts_when_material_missing(
    db_session, worker_session_factory, monkeypatch
):

    calls = []

    async def recording_process_content(*args, **kwargs):
        calls.append(args)

    monkeypatch.setattr(material_tasks, "_process_material_content", recording_process_content)

    status = await material_tasks._handle_material(
        str(uuid.uuid4()),
        "courses/x/materials/none.pdf",
        str(uuid.uuid4()),
        str(uuid.uuid4()),
        session_factory=worker_session_factory,
    )

    assert status is None
    assert calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "initial_status", [READY_STATUS, PROCESSING_STATUS, FAILED_STATUS]
)
async def test_process_material_skips_already_finalized_material_and_leaves_status_unchanged(
    db_session, worker_session_factory, monkeypatch, initial_status
):
    """Phase 1D locked contract: re-processing a material that is already
    ``ready``, ``processing``, or ``failed`` is a no-op -
    ``_handle_material`` returns the current status string, the content-
    processing seam is never called, and the persisted status stays unchanged.
    """
    owner = await _create_user(
        db_session, "material-task-rerun-owner", "material-task-rerun@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner, status=initial_status)
    s3_key = material.s3_key

    calls = []

    async def recording_process_content(*args, **kwargs):
        calls.append(True)

    monkeypatch.setattr(material_tasks, "_process_material_content", recording_process_content)

    status = await material_tasks._handle_material(
        str(material.id),
        s3_key,
        str(course.id),
        str(owner.id),
        session_factory=worker_session_factory,
    )

    assert status == initial_status

    await db_session.refresh(material)
    assert material.status == initial_status
    assert calls == []

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_process_material_second_delivery_after_claim_is_noop(
    db_session, worker_session_factory, monkeypatch
):
    """W8: once a worker atomically claims a pending material as ``processing``,
    a concurrent/second delivery of the same material is a no-op: the content
    seam is never called and the persisted status stays ``processing``.
    """
    owner = await _create_user(
        db_session, "material-task-claimnoop-owner", "material-task-claimnoop@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    s3_key = material.s3_key

    claimed = await claim_pending_material(db_session, material.id)
    assert claimed is not None
    assert claimed.status == PROCESSING_STATUS

    calls = []

    async def recording_process_content(*args, **kwargs):
        calls.append(True)

    monkeypatch.setattr(material_tasks, "_process_material_content", recording_process_content)

    status = await material_tasks._handle_material(
        str(material.id),
        s3_key,
        str(course.id),
        str(owner.id),
        session_factory=worker_session_factory,
    )

    assert status == PROCESSING_STATUS

    await db_session.refresh(material)
    assert material.status == PROCESSING_STATUS
    assert calls == []

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_process_material_concurrent_double_delivery_claims_seam_exactly_once(
    db_session, worker_session_factory, monkeypatch
):
    """Phase 1D W8 acceptance: two deliveries of the same pending material run
    genuinely concurrently under ``asyncio.gather`` against the same material id.

    Exactly one execution wins the atomic ``pending -> processing`` claim and
    reaches the content seam; the loser takes the safe re-entry/no-op path
    (returns the current status, never reaches the seam). The winner's final
    transition is committed, so the persisted status is the winner's outcome.
    """
    owner = await _create_user(
        db_session,
        "material-task-concurrent-owner",
        "material-task-concurrent@example.com",
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    s3_key = material.s3_key

    seam_calls = []
    winner_claimed = asyncio.Event()
    release_winner = asyncio.Event()

    async def barrier_content(inner_material, inner_s3_key, course_id, owner_id):
        seam_calls.append((inner_material.id, inner_s3_key))
        winner_claimed.set()
        await release_winner.wait()

    monkeypatch.setattr(material_tasks, "_process_material_content", barrier_content)

    async def _deliver_as_winner():
        return await material_tasks._handle_material(
            str(material.id),
            s3_key,
            str(course.id),
            str(owner.id),
            session_factory=worker_session_factory,
        )

    async def _deliver_as_loser():
        await winner_claimed.wait()
        try:
            return await material_tasks._handle_material(
                str(material.id),
                s3_key,
                str(course.id),
                str(owner.id),
                session_factory=worker_session_factory,
            )
        finally:
            release_winner.set()

    winner_result, loser_result = await asyncio.gather(
        _deliver_as_winner(), _deliver_as_loser()
    )

    assert winner_result == READY_STATUS
    assert loser_result == PROCESSING_STATUS
    assert len(seam_calls) == 1
    assert seam_calls[0][0] == material.id

    await db_session.refresh(material)
    assert material.status == READY_STATUS

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_process_material_statement_failure_preserves_original_error_and_records_failed(
    db_session, worker_session_factory, monkeypatch
):
    """Phase 1C regression: a real DB statement failure inside content
    processing must propagate the ORIGINAL error after recording the material
    as ``failed``, not a secondary transaction-aborted error that leaves the
    material stuck in ``processing``.
    """
    owner = await _create_user(
        db_session, "material-task-stmt-owner", "material-task-stmt@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    s3_key = material.s3_key

    captured_sessions: list[AsyncSession] = []
    original_errors: dict[str, sqlalchemy.exc.SQLAlchemyError] = {}

    def capturing_factory():
        session = worker_session_factory()
        captured_sessions.append(session)
        return session

    async def failing_statement_content(*args, **kwargs):
        session = captured_sessions[-1]
        try:
            await session.execute(text("SELECT * FROM phase_1c_missing_table"))
        except sqlalchemy.exc.SQLAlchemyError as error:
            original_errors["error"] = error
            raise

    monkeypatch.setattr(
        material_tasks, "_process_material_content", failing_statement_content
    )

    with pytest.raises(sqlalchemy.exc.SQLAlchemyError) as exc_info:
        await material_tasks._handle_material(
            str(material.id),
            s3_key,
            str(course.id),
            str(owner.id),
            session_factory=capturing_factory,
        )

    assert exc_info.value is original_errors["error"]
    assert not isinstance(exc_info.value, sqlalchemy.exc.PendingRollbackError)

    assert await _read_material_status(material.id) == FAILED_STATUS

    async def noop_content(*args, **kwargs):
        return None

    monkeypatch.setattr(material_tasks, "_process_material_content", noop_content)

    second = await _create_material(db_session, course, owner)
    second_status = await material_tasks._handle_material(
        str(second.id),
        second.s3_key,
        str(course.id),
        str(owner.id),
        session_factory=worker_session_factory,
    )
    assert second_status == READY_STATUS
    assert await _read_material_status(second.id) == READY_STATUS

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_process_material_flush_failure_preserves_original_error_and_records_failed(
    db_session, worker_session_factory, monkeypatch
):
    """Phase 1C regression: a real ORM flush/integrity failure inside content
    processing must propagate the ORIGINAL integrity error (after recording the
    material as ``failed``), not a PendingRollbackError raised by a subsequent
    FAILED transition on the poisoned session.
    """
    owner = await _create_user(
        db_session, "material-task-flush-owner", "material-task-flush@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    s3_key = material.s3_key

    captured_sessions: list[AsyncSession] = []
    original_errors: dict[str, sqlalchemy.exc.SQLAlchemyError] = {}

    def capturing_factory():
        session = worker_session_factory()
        captured_sessions.append(session)
        return session

    async def failing_flush_content(*args, **kwargs):
        session = captured_sessions[-1]
        args[0].title = None
        try:
            await session.flush()
        except sqlalchemy.exc.SQLAlchemyError as error:
            original_errors["error"] = error
            raise

    monkeypatch.setattr(
        material_tasks, "_process_material_content", failing_flush_content
    )

    with pytest.raises(sqlalchemy.exc.SQLAlchemyError) as exc_info:
        await material_tasks._handle_material(
            str(material.id),
            s3_key,
            str(course.id),
            str(owner.id),
            session_factory=capturing_factory,
        )

    assert exc_info.value is original_errors["error"]
    assert not isinstance(exc_info.value, sqlalchemy.exc.PendingRollbackError)

    assert await _read_material_status(material.id) == FAILED_STATUS

    await db_session.delete(owner)
    await db_session.commit()


def test_process_material_registered_under_publishing_task_name():
    assert material_tasks.process_material.name == publishing.MATERIAL_PROCESSING_TASK_NAME
    assert material_tasks.process_material.name == (
        "app.workers.tasks.material_tasks.process_material"
    )
    assert publishing.MATERIAL_PROCESSING_TASK_NAME in material_tasks.celery_app.tasks


def test_process_material_delivery_configuration_tripwire():
    """Phase 1D delivery-contract tripwire.

    The processing task is intentionally delivered with ``acks_late`` disabled,
    ``reject_on_worker_lost`` not enabled, no automatic retry delay, and publish
    retry enabled. F10 adds a 10-minute soft / 11-minute hard task time limit.
    These settings are defaults today (plus the explicit F10 limits); the
    assertions guard against accidental future changes to the delivery
    configuration.
    """
    conf = material_tasks.celery_app.conf

    assert conf.get("task_acks_late") is False
    assert not conf.get("task_reject_on_worker_lost")
    assert conf.get("task_default_retry_delay") is None
    assert conf.get("task_publish_retry") is True

    assert conf.get("task_soft_time_limit") == 600
    assert conf.get("task_time_limit") == 660


def test_process_material_sequential_tasks_use_distinct_loops_in_same_process(
    monkeypatch,
):
    """Phase 1B regression: two sequential ``process_material.run(...)`` calls in
    the same Python process must each succeed.

    ``process_material`` is a synchronous Celery task that calls
    ``asyncio.run(...)`` per invocation, so every task gets a brand-new event
    loop. Phase 1B gives each invocation its own task-local engine and session
    factory and disposes the engine before its loop closes, so a pooled asyncpg
    connection created by the first task's event loop must never leak into the
    second task's loop. This test drives the real production entrypoint twice
    against two distinct pending materials and requires both to reach ``ready``.
    """

    async def _noop_content(*args, **kwargs):
        return None

    monkeypatch.setattr(material_tasks, "_process_material_content", _noop_content)

    async def _seed() -> dict[str, str]:
        engine = create_async_engine(settings.database_url)
        factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        try:
            async with factory() as db:
                owner = await _create_user(
                    db, "material-seq-owner", "material-seq@example.com"
                )
                course = await _create_course(db, owner)
                first = await _create_material(db, course, owner)
                second = await _create_material(db, course, owner)
                return {
                    "owner_id": str(owner.id),
                    "course_id": str(course.id),
                    "first_id": str(first.id),
                    "first_s3_key": first.s3_key,
                    "second_id": str(second.id),
                    "second_s3_key": second.s3_key,
                }
        finally:
            await engine.dispose()

    async def _read_statuses(material_ids: list[str]) -> dict[str, str]:
        engine = create_async_engine(settings.database_url)
        factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        try:
            async with factory() as db:
                statuses: dict[str, str] = {}
                for material_id in material_ids:
                    result = await db.execute(
                        select(Material).where(Material.id == uuid.UUID(material_id))
                    )
                    material = result.scalar_one_or_none()
                    statuses[material_id] = material.status if material else "missing"
                return statuses
        finally:
            await engine.dispose()

    async def _cleanup_by_subject(subject: str) -> None:
        engine = create_async_engine(settings.database_url)
        factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        try:
            async with factory() as db:
                await _delete_user_by_subject(db, subject)
        finally:
            await engine.dispose()

    seeded = asyncio.run(_seed())

    try:
        first_status = material_tasks.process_material.run(
            seeded["first_id"],
            seeded["first_s3_key"],
            seeded["course_id"],
            seeded["owner_id"],
        )
        second_status = material_tasks.process_material.run(
            seeded["second_id"],
            seeded["second_s3_key"],
            seeded["course_id"],
            seeded["owner_id"],
        )

        assert first_status == READY_STATUS
        assert second_status == READY_STATUS

        statuses = asyncio.run(
            _read_statuses([seeded["first_id"], seeded["second_id"]])
        )
        assert statuses[seeded["first_id"]] == READY_STATUS
        assert statuses[seeded["second_id"]] == READY_STATUS
    finally:
        asyncio.run(_cleanup_by_subject("material-seq-owner"))