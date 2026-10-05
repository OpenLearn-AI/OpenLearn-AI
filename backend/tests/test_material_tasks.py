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

B5: the content seam is wired (fetch → Stage 1 → Stage 2). The pinned
lifecycle stubs now accept the keyword-only ``session`` argument the task
passes to the seam (decisions.md §6); the wired-path tests exercise the real
seam body end-to-end — storage fetch fake, Docling conversion faked at the
production import site (same isolation strategy as
``tests/services/test_document_pipeline_stage1.py``), PAL providers built
through the real factory — against the real database, including the atomic
vector/``ready`` commit and the rollback-discards-vectors failure path.
"""

import asyncio
import os
import uuid
from pathlib import Path, PurePosixPath
from unittest.mock import MagicMock

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
    PROCESSING_STATUS,
    READY_STATUS,
    Material,
)
from app.models.user import User  # noqa: E402
from app.services.material_service import claim_pending_material  # noqa: E402
from app.workers import publishing  # noqa: E402
from app.workers.tasks import material_tasks  # noqa: E402
from conftest import (  # noqa: E402
    _create_material,
    _create_user,
    _delete_user_by_subject,
)
from docling.datamodel.base_models import ConversionStatus  # noqa: E402
from docling.datamodel.document import ConversionResult  # noqa: E402
from docling_core.types.doc.document import (  # noqa: E402
    DoclingDocument,
    PageItem,
    ProvenanceItem,
    Size,
    TextItem,
)
from docling_core.types.doc.labels import DocItemLabel  # noqa: E402

from app.documents.exceptions import UnsupportedDocumentTypeError  # noqa: E402
from app.pal.providers.vector_db.mock_provider import (  # noqa: E402
    MockVectorDBProvider,
)
from app.pal.providers.vector_db.postgres_provider import (  # noqa: E402
    PostgresVectorDBProvider,
)

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
    seam_sessions = []

    async def fake_process_content(
        inner_material, inner_s3_key, course_id, owner_id, *, session
    ):
        calls.append((inner_material.id, inner_s3_key, course_id, owner_id))
        seam_sessions.append(session)

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
    # B5: the seam receives the task's live session (decisions.md §2.4/§6).
    assert len(seam_sessions) == 1
    assert isinstance(seam_sessions[0], AsyncSession)

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

    async def barrier_content(
        inner_material, inner_s3_key, course_id, owner_id, *, session
    ):
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


# ---------------------------------------------------------------------------
# B5 — wired content-processing path (fetch → Stage 1 → Stage 2)
#
# The tests below exercise the REAL ``_process_material_content`` body:
# the storage fetch is replaced with a deterministic fake honoring the
# helper's contract, Docling conversion is faked at the production import
# site (same isolation strategy as tests/services/test_document_pipeline_
# stage1.py), and the PAL providers are built through the REAL factory from
# settings. Everything else — claim, session/transaction lifecycle, the
# document pipeline stages, the chunker, status transitions — runs for real
# against the database.
# ---------------------------------------------------------------------------


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def _build_single_page_pdf(page_text: str) -> bytes:
    """A valid deterministic one-page PDF (same fixture strategy as the
    Stage-1 suite: hand-written raw bytes, base-14 font, no conversion)."""
    objects: dict[int, bytes] = {}
    objects[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objects[2] = b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"
    objects[3] = (
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
    )
    stream = f"BT /F1 24 Tf 72 700 Td ({_escape_pdf_text(page_text)}) Tj ET".encode()
    objects[4] = b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"
    objects[5] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"

    out = bytearray(b"%PDF-1.4\n")
    offsets: dict[int, int] = {}
    for obj_num in sorted(objects):
        offsets[obj_num] = len(out)
        out += f"{obj_num} 0 obj\n".encode() + objects[obj_num] + b"\nendobj\n"

    xref_offset = len(out)
    out += b"xref\n" + f"0 {len(objects) + 1}\n".encode() + b"0000000000 65535 f \n"
    for obj_num in sorted(objects):
        out += f"{offsets[obj_num]:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode()
    out += f"startxref\n{xref_offset}\n%%EOF\n".encode()
    return bytes(out)


def _text_item(ref: str, text: str, page_no: int) -> TextItem:
    return TextItem(
        self_ref=ref,
        label=DocItemLabel.TEXT,
        orig=text,
        text=text,
        prov=[
            ProvenanceItem(
                page_no=page_no,
                bbox={
                    "l": 0.0,
                    "t": 0.0,
                    "r": 100.0,
                    "b": 100.0,
                    "coord_origin": "TOPLEFT",
                },
                charspan=(0, len(text)),
            )
        ],
    )


def _conversion_result(page_texts: list[str]) -> ConversionResult:
    """A real ConversionResult envelope with a one-page DoclingDocument."""
    document = DoclingDocument(
        name="mocked-doc",
        pages={i + 1: PageItem(page_no=i + 1, size=Size(width=612.0, height=792.0)) for i in range(len(page_texts))},
        texts=[
            _text_item(f"#/texts/{i}", page_text, i + 1)
            for i, page_text in enumerate(page_texts)
        ],
    )
    return ConversionResult.model_construct(
        status=ConversionStatus.SUCCESS,
        document=document,
        errors=[],
    )


def _install_fake_converter(monkeypatch, page_texts: list[str]) -> MagicMock:
    """Patch DocumentConverter in the production module's namespace."""
    cls_mock = MagicMock(name="DocumentConverter")
    cls_mock.return_value.convert.return_value = _conversion_result(page_texts)
    monkeypatch.setattr("app.services.ingestion.DocumentConverter", cls_mock)
    return cls_mock


class _FakeStorageFetch:
    """Deterministic stand-in for the Backend storage fetch helper.

    Records every ``(s3_key, destination_dir)`` call and writes real bytes
    into the caller-owned directory per the helper's contract; when ``error``
    is set it raises after recording, to exercise the failure path's cleanup.
    """

    def __init__(self, content: bytes, error: Exception | None = None) -> None:
        self.content = content
        self.error = error
        self.calls: list[tuple[str, str]] = []

    def __call__(self, s3_key: str, destination_dir: str) -> Path:
        self.calls.append((s3_key, destination_dir))
        if self.error is not None:
            raise self.error
        destination = Path(destination_dir) / PurePosixPath(s3_key).name
        destination.write_bytes(self.content)
        return destination


def _spy_on_seam_vector_provider(monkeypatch, post_upsert_error=None) -> dict:
    """Wrap the REAL factory getter to capture what the seam builds.

    The provider instance is still created by ``get_vector_db_provider`` from
    settings (the production selection mechanism); the spy only records the
    instance, the session the seam handed it, and the records upserted.
    With ``post_upsert_error`` set, the wrapped upsert raises AFTER the real
    provider executed — injecting a failure inside content processing with
    the vector statements already on the session.
    """
    captured: dict = {"records": [], "session": None, "provider": None}
    real_get = material_tasks.get_vector_db_provider

    def spy(provider=None, session=None):
        instance = real_get(provider=provider, session=session)
        original_upsert = instance.upsert

        async def recording_upsert(records):
            captured["records"].extend(records)
            result = await original_upsert(records)
            if post_upsert_error is not None:
                raise post_upsert_error
            return result

        instance.upsert = recording_upsert
        captured["provider"] = instance
        captured["session"] = session
        return instance

    monkeypatch.setattr(material_tasks, "get_vector_db_provider", spy)
    return captured


async def _count_vector_records(material_id: str) -> int:
    """Count committed vector rows for a material via an independent engine
    (same connection-independence rule as ``_read_material_status``)."""
    engine = create_async_engine(settings.database_url)
    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    try:
        async with factory() as db:
            result = await db.execute(
                text(
                    "SELECT COUNT(*) FROM vector_records "
                    "WHERE metadata->>'material_id' = :mid"
                ),
                {"mid": material_id},
            )
            return int(result.scalar_one())
    finally:
        await engine.dispose()


_PAGE_TEXT = (
    "Wired pipeline fixture page: this single-page PDF carries well over the "
    "fifty-character OCR threshold, so the targeted-OCR path never fires and "
    "the mock OCR provider is never invoked."
)


@pytest.mark.asyncio
async def test_wired_pipeline_fetch_ingest_persist_marks_ready_and_cleans_temp(
    db_session, worker_session_factory, monkeypatch
):
    """B5 wired happy path: fetch → Stage 1 → Stage 2 → ``ready``.

    Uses the real seam, real factory (settings default to the mock vector
    store), real chunker, and the real lifecycle; only the storage fetch and
    Docling conversion are faked. Asserts argument propagation into the
    fetch, material-scoped vector identities, the live session passed to the
    provider, and deterministic temp-directory cleanup after success.
    """
    owner = await _create_user(
        db_session, "b5-wired-ready-owner", "b5-wired-ready@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    s3_key = material.s3_key

    _install_fake_converter(monkeypatch, [_PAGE_TEXT])
    fetch = _FakeStorageFetch(_build_single_page_pdf(_PAGE_TEXT))
    monkeypatch.setattr(material_tasks, "download_material_to_temp", fetch)
    captured = _spy_on_seam_vector_provider(monkeypatch)

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

    # Task arguments propagate into the storage fetch.
    assert [call[0] for call in fetch.calls] == [s3_key]
    assert len(fetch.calls) == 1

    # The seam built the factory's provider and handed it the live session.
    assert isinstance(captured["provider"], MockVectorDBProvider)
    assert isinstance(captured["session"], AsyncSession)

    # Stage-2 records are material-scoped with the full provenance payload.
    records = captured["records"]
    assert len(records) >= 1
    for record in records:
        assert record.id.startswith(f"{material.id}:")
        assert record.metadata["material_id"] == str(material.id)
        assert record.metadata["document_id"] == PurePosixPath(s3_key).stem
        assert record.content
        assert len(record.vector) == settings.ai_embedding_dimension

    # Deterministic cleanup: the per-task temp directory is gone.
    assert not Path(fetch.calls[0][1]).exists()

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_wired_pipeline_persists_vectors_atomically_with_ready_transition(
    db_session, worker_session_factory, monkeypatch
):
    """B5 atomicity (success): with the session-backed postgres vector store
    configured, the upsert executes on the task's live session and the rows
    become visible from an independent connection exactly when the material
    is ``ready`` — one commit covers vectors and status together.
    """
    owner = await _create_user(
        db_session, "b5-wired-atomic-owner", "b5-wired-atomic@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    s3_key = material.s3_key

    monkeypatch.setattr(settings, "ai_vector_db_provider", "postgres")
    _install_fake_converter(monkeypatch, [_PAGE_TEXT])
    fetch = _FakeStorageFetch(_build_single_page_pdf(_PAGE_TEXT))
    monkeypatch.setattr(material_tasks, "download_material_to_temp", fetch)
    captured = _spy_on_seam_vector_provider(monkeypatch)

    status = await material_tasks._handle_material(
        str(material.id),
        s3_key,
        str(course.id),
        str(owner.id),
        session_factory=worker_session_factory,
    )

    assert status == READY_STATUS
    assert isinstance(captured["provider"], PostgresVectorDBProvider)
    assert isinstance(captured["session"], AsyncSession)

    assert await _read_material_status(material.id) == READY_STATUS
    # Committed atomically with the ready transition: every record handed to
    # the provider is durable on an independent connection.
    assert (
        await _count_vector_records(str(material.id))
        == len(captured["records"])
    )
    assert len(captured["records"]) >= 1

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_wired_pipeline_rollback_discards_vectors_and_marks_failed(
    db_session, worker_session_factory, monkeypatch
):
    """B5 atomicity (failure): an exception inside content processing AFTER
    the vector upsert executed on the shared session (decisions.md §2.4) —
    triggered by a stage-2 error injected post-upsert — follows the pinned
    failure path: rollback discards the uncommitted vector rows, the
    material lands in ``failed``, and no partial vector state survives.
    """
    owner = await _create_user(
        db_session, "b5-wired-rollback-owner", "b5-wired-rollback@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    s3_key = material.s3_key

    monkeypatch.setattr(settings, "ai_vector_db_provider", "postgres")
    _install_fake_converter(monkeypatch, [_PAGE_TEXT])
    fetch = _FakeStorageFetch(_build_single_page_pdf(_PAGE_TEXT))
    monkeypatch.setattr(material_tasks, "download_material_to_temp", fetch)
    captured = _spy_on_seam_vector_provider(
        monkeypatch,
        post_upsert_error=RuntimeError("forced post-upsert failure"),
    )

    with pytest.raises(RuntimeError, match="forced post-upsert failure"):
        await material_tasks._handle_material(
            str(material.id),
            s3_key,
            str(course.id),
            str(owner.id),
            session_factory=worker_session_factory,
        )

    # The upsert really executed on the session before the failure...
    assert len(captured["records"]) >= 1
    # ...and the pinned failure path's rollback discarded every uncommitted
    # row while the material itself was recorded ``failed``.
    assert await _count_vector_records(str(material.id)) == 0
    assert await _read_material_status(material.id) == FAILED_STATUS
    assert not Path(fetch.calls[0][1]).exists()

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_wired_pipeline_fetch_failure_marks_failed_and_cleans_temp(
    db_session, worker_session_factory, monkeypatch
):
    """B5 failure path (storage): a fetch error propagates unchanged, the
    material is recorded ``failed`` through the pinned lifecycle, and the
    per-task temp directory is cleaned up.
    """
    owner = await _create_user(
        db_session, "b5-wired-fetchfail-owner", "b5-wired-fetchfail@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    s3_key = material.s3_key

    fetch = _FakeStorageFetch(b"", error=RuntimeError("storage download boom"))
    monkeypatch.setattr(material_tasks, "download_material_to_temp", fetch)

    with pytest.raises(RuntimeError, match="storage download boom"):
        await material_tasks._handle_material(
            str(material.id),
            s3_key,
            str(course.id),
            str(owner.id),
            session_factory=worker_session_factory,
        )

    assert await _read_material_status(material.id) == FAILED_STATUS
    assert len(fetch.calls) == 1
    assert not Path(fetch.calls[0][1]).exists()
    assert await _count_vector_records(str(material.id)) == 0

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_wired_pipeline_stage_failure_marks_failed_and_cleans_temp(
    db_session, worker_session_factory, monkeypatch
):
    """B5 failure path (processing stage): an unsupported document extension
    fails Stage 1 with its real typed error before any conversion runs; the
    material is recorded ``failed`` and the temp directory is cleaned up.
    """
    owner = await _create_user(
        db_session, "b5-wired-stagefail-owner", "b5-wired-stagefail@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    # The task consumes the s3_key argument as-is; a key outside the seeded
    # material's own value exercises the ingestion error path (.xyz is not a
    # supported ingestion format).
    s3_key = f"courses/{course.id}/materials/{uuid.uuid4()}-notes.xyz"

    fetch = _FakeStorageFetch(b"not a real document")
    monkeypatch.setattr(material_tasks, "download_material_to_temp", fetch)

    with pytest.raises(UnsupportedDocumentTypeError):
        await material_tasks._handle_material(
            str(material.id),
            s3_key,
            str(course.id),
            str(owner.id),
            session_factory=worker_session_factory,
        )

    assert await _read_material_status(material.id) == FAILED_STATUS
    assert [call[0] for call in fetch.calls] == [s3_key]
    assert not Path(fetch.calls[0][1]).exists()
    assert await _count_vector_records(str(material.id)) == 0

    await db_session.delete(owner)
    await db_session.commit()
