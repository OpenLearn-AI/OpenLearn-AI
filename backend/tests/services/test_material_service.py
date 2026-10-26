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
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.models.course import Course
from app.models.material import (
    FAILED_STATUS,
    MATERIAL_RETRY_LIMIT,
    PENDING_STATUS,
    PROCESSING_STATUS,
    READY_STATUS,
    Material,
)
from app.models.material_page import MaterialPage
from app.models.user import User
from app.services.material_service import (
    count_nonempty_material_pages,
    claim_material_retry,
    claim_pending_material,
    find_material_by_content_hash,
    get_material_by_id,
    list_material_pages,
    replace_material_pages,
    restore_material_after_publish_failure,
    transition_material_status,
)
from conftest import _create_material, _create_user


async def _create_course(db, owner: User, title: str = "Test Course") -> Course:
    course = Course(
        owner_id=owner.id,
        title=title,
        description="Slides",
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course



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
async def test_claim_pending_material_sets_processing_and_commits(db_session):
    owner = await _create_user(
        db_session, "material-claim-owner", "material-claim@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)

    claimed = await claim_pending_material(db_session, material.id)

    assert claimed is not None
    assert claimed.id == material.id
    assert claimed.status == PROCESSING_STATUS

    result = await db_session.execute(
        select(Material).where(Material.id == material.id)
    )
    persisted = result.scalar_one()
    assert persisted.status == PROCESSING_STATUS

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_claim_pending_material_returns_none_for_missing_id(db_session):
    claimed = await claim_pending_material(db_session, uuid.uuid4())

    assert claimed is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "initial_status", [PROCESSING_STATUS, READY_STATUS, FAILED_STATUS]
)
async def test_claim_pending_material_returns_none_for_non_pending(
    db_session, initial_status
):
    owner = await _create_user(
        db_session,
        f"material-claim-{initial_status}-owner",
        f"material-claim-{initial_status}@example.com",
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(
        db_session, course, owner, status=initial_status
    )

    claimed = await claim_pending_material(db_session, material.id)

    assert claimed is None
    await db_session.refresh(material)
    assert material.status == initial_status

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_claim_pending_material_excludes_concurrent_claim_from_another_session(
    db_session,
):
    """W8: the claim is a single conditional UPDATE. Once one session claims a
    pending material as ``processing``, a second session (a concurrent worker)
    claiming the same material must receive ``None`` and leave the persisted
    status at ``processing``."""
    owner = await _create_user(
        db_session, "material-claim-excl-owner", "material-claim-excl@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)

    claimed = await claim_pending_material(db_session, material.id)
    assert claimed is not None
    assert claimed.status == PROCESSING_STATUS

    engine = create_async_engine(settings.database_url)
    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    try:
        async with factory() as other_session:
            second_claim = await claim_pending_material(other_session, material.id)
            assert second_claim is None

            result = await other_session.execute(
                select(Material).where(Material.id == material.id)
            )
            persisted = result.scalar_one()
            assert persisted.status == PROCESSING_STATUS
    finally:
        await engine.dispose()

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


# ---------------------------------------------------------------------------
# Week 9 — content-hash lookup, retry budget, publish-failure compensation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_find_material_by_content_hash_scoped_to_course(db_session):
    owner = await _create_user(
        db_session, "material-hash-lookup-owner", "material-hash-lookup@example.com"
    )
    course_a = await _create_course(db_session, owner, title="A")
    course_b = await _create_course(db_session, owner, title="B")
    digest = uuid.uuid4().hex
    await _create_material(db_session, course_a, owner, status=READY_STATUS, sha256=digest)

    found = await find_material_by_content_hash(db_session, course_a.id, digest)
    assert found is not None
    assert found.course_id == course_a.id
    assert found.sha256 == digest

    # Same content in another course is not a duplicate (course-scoped).
    assert await find_material_by_content_hash(db_session, course_b.id, digest) is None
    # Unknown hashes never match.
    assert await find_material_by_content_hash(db_session, course_a.id, uuid.uuid4().hex) is None

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_claim_material_retry_sets_pending_and_increments_counter(db_session):
    owner = await _create_user(
        db_session, "material-retry-claim-owner", "material-retry-claim@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner, status=FAILED_STATUS)

    claimed = await claim_material_retry(db_session, material.id)

    assert claimed is not None
    assert claimed.status == PENDING_STATUS
    assert claimed.retry_count == 1

    result = await db_session.execute(
        select(Material).where(Material.id == material.id)
    )
    persisted = result.scalar_one()
    assert persisted.status == PENDING_STATUS
    assert persisted.retry_count == 1

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize("initial_status", [PENDING_STATUS, PROCESSING_STATUS])
async def test_claim_material_retry_returns_none_for_ineligible_status(
    db_session, initial_status
):
    owner = await _create_user(
        db_session,
        f"material-retry-ineligible-{initial_status}-owner",
        f"material-retry-ineligible-{initial_status}@example.com",
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner, status=initial_status)

    claimed = await claim_material_retry(db_session, material.id)

    assert claimed is None
    await db_session.refresh(material)
    assert material.status == initial_status
    assert material.retry_count == 0

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_claim_material_retry_stops_at_retry_limit(db_session):
    owner = await _create_user(
        db_session, "material-retry-limit-owner", "material-retry-limit@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner, status=FAILED_STATUS)
    material.retry_count = MATERIAL_RETRY_LIMIT
    await db_session.commit()

    claimed = await claim_material_retry(db_session, material.id)

    assert claimed is None
    await db_session.refresh(material)
    assert material.status == FAILED_STATUS
    assert material.retry_count == MATERIAL_RETRY_LIMIT

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_claim_material_retry_ready_material_is_allowed(db_session):
    """The Week 9 budget covers manual retries of ``ready`` and ``failed``
    materials; a claim on a ready material re-enters processing as pending."""
    owner = await _create_user(
        db_session, "material-retry-ready-owner", "material-retry-ready@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner, status=READY_STATUS)

    claimed = await claim_material_retry(db_session, material.id)

    assert claimed is not None
    assert claimed.status == PENDING_STATUS
    assert claimed.retry_count == 1

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_claim_material_retry_excludes_concurrent_claim_from_another_session(
    db_session,
):
    """Week 9: the retry claim is a single conditional UPDATE, so exactly one
    concurrent claim can succeed; the second session sees ``None`` while the
    row stays pending with a single consumed retry."""
    owner = await _create_user(
        db_session, "material-retry-excl-owner", "material-retry-excl@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner, status=FAILED_STATUS)

    claimed = await claim_material_retry(db_session, material.id)
    assert claimed is not None
    assert claimed.retry_count == 1

    engine = create_async_engine(settings.database_url)
    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    try:
        async with factory() as other_session:
            second_claim = await claim_material_retry(other_session, material.id)
            assert second_claim is None

            result = await other_session.execute(
                select(Material).where(Material.id == material.id)
            )
            persisted = result.scalar_one()
            assert persisted.status == PENDING_STATUS
            assert persisted.retry_count == 1
    finally:
        await engine.dispose()

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_restore_after_publish_failure_restores_status_and_decrements(db_session):
    owner = await _create_user(
        db_session, "material-restore-owner", "material-restore@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner, status=FAILED_STATUS)

    claimed = await claim_material_retry(db_session, material.id)
    assert claimed is not None
    claimed_retry_count = claimed.retry_count

    restored = await restore_material_after_publish_failure(
        db_session,
        material.id,
        previous_status=FAILED_STATUS,
        claimed_retry_count=claimed_retry_count,
    )

    assert restored is True
    await db_session.refresh(material)
    assert material.status == FAILED_STATUS
    assert material.retry_count == 0

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_restore_after_publish_failure_never_reverts_worker_claimed_job(db_session):
    """Week 9: compensation only applies while the retry is still pending with
    the claimed retry count. A material already claimed by the worker
    (``processing``) — or finished after that — is never reverted."""
    owner = await _create_user(
        db_session, "material-restore-claimed-owner", "material-restore-claimed@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner, status=FAILED_STATUS)

    claimed = await claim_material_retry(db_session, material.id)
    assert claimed is not None
    claimed_retry_count = claimed.retry_count

    # The worker claims the material before the compensation attempt.
    worker_claimed = await claim_pending_material(db_session, material.id)
    assert worker_claimed is not None
    assert worker_claimed.status == PROCESSING_STATUS

    restored = await restore_material_after_publish_failure(
        db_session,
        material.id,
        previous_status=FAILED_STATUS,
        claimed_retry_count=claimed_retry_count,
    )

    assert restored is False
    await db_session.refresh(material)
    assert material.status == PROCESSING_STATUS
    assert material.retry_count == 1

    await db_session.delete(owner)
    await db_session.commit()


# ---------------------------------------------------------------------------
# Week 9 output consistency — replace_material_pages
# ---------------------------------------------------------------------------


async def _seed_pages(
    db: AsyncSession, material: Material, rows: list[tuple[int, str]]
) -> None:
    for page_number, text in rows:
        db.add(
            MaterialPage(
                material_id=material.id, page_number=page_number, text=text
            )
        )
    await db.commit()


async def _read_pages(
    db: AsyncSession, material_id: uuid.UUID
) -> list[tuple[int, str]]:
    result = await db.execute(
        select(MaterialPage.page_number, MaterialPage.text)
        .where(MaterialPage.material_id == material_id)
        .order_by(MaterialPage.page_number)
    )
    return [(row[0], row[1]) for row in result.all()]


@pytest.mark.asyncio
async def test_replace_material_pages_persists_numbered_nonempty_pages(db_session):
    """Week 9: a successful attempt's pages are persisted 1-based, in
    ascending page-number order, and the persisted count is returned."""
    owner = await _create_user(
        db_session, "material-pages-insert-owner", "material-pages-insert@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)

    stored = await replace_material_pages(
        db_session,
        material.id,
        pages=[(2, "second page"), (1, "first page")],
    )
    await db_session.commit()

    assert stored == 2
    assert await _read_pages(db_session, material.id) == [
        (1, "first page"),
        (2, "second page"),
    ]

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_replace_material_pages_replaces_previous_output(db_session):
    """Week 9 output consistency: a success replaces the previous attempt's
    page rows — stale pages never survive next to the new output."""
    owner = await _create_user(
        db_session, "material-pages-replace-owner", "material-pages-replace@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    await _seed_pages(db_session, material, [(1, "old one"), (5, "old five")])

    stored = await replace_material_pages(
        db_session,
        material.id,
        pages=[(1, "new one"), (2, "new two")],
    )
    await db_session.commit()

    assert stored == 2
    assert await _read_pages(db_session, material.id) == [
        (1, "new one"),
        (2, "new two"),
    ]

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_replace_material_pages_stores_empty_pages(db_session):
    """Week 9 decision: empty and whitespace-only pages are stored too, but
    only non-empty pages count toward the keep-more-pages rule."""
    owner = await _create_user(
        db_session, "material-pages-blank-owner", "material-pages-blank@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)

    stored = await replace_material_pages(
        db_session,
        material.id,
        pages=[(1, "real text"), (2, ""), (3, "   \n\t "), (4, "more text")],
    )
    await db_session.commit()

    assert stored == 4
    assert await _read_pages(db_session, material.id) == [
        (1, "real text"),
        (2, ""),
        (3, "   \n\t "),
        (4, "more text"),
    ]
    assert await count_nonempty_material_pages(
        db_session, material.id
    ) == 2

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_replace_material_pages_empty_input_clears_previous_output(db_session):
    """A successful run that produced no storable pages clears the previous
    output entirely; the material never keeps a mix of old and new rows."""
    owner = await _create_user(
        db_session, "material-pages-clear-owner", "material-pages-clear@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    await _seed_pages(db_session, material, [(1, "old one"), (2, "old two")])

    stored = await replace_material_pages(db_session, material.id, pages=[])

    assert stored == 0
    assert await _read_pages(db_session, material.id) == []

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_replace_material_pages_flushes_without_committing(db_session):
    """Transaction contract: the function only flushes, it never commits —
    the writes stay invisible to an independent connection until the caller
    commits, and a caller rollback discards them entirely (this is what
    makes the worker's failed-attempt rollback discard page output)."""
    owner = await _create_user(
        db_session, "material-pages-txn-owner", "material-pages-txn@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    await _seed_pages(db_session, material, [(1, "committed old page")])
    material_id = material.id  # rollback expires ORM instances below

    stored = await replace_material_pages(
        db_session, material_id, pages=[(1, "uncommitted new page")]
    )
    assert stored == 1

    # Not committed: an independent connection still sees the old output.
    engine = create_async_engine(settings.database_url)
    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    try:
        async with factory() as independent:
            result = await independent.execute(
                select(MaterialPage.text)
                .where(MaterialPage.material_id == material.id)
                .order_by(MaterialPage.page_number)
            )
            assert [row[0] for row in result.all()] == ["committed old page"]
    finally:
        await engine.dispose()

    # A caller rollback discards the flush entirely.
    await db_session.rollback()
    assert await _read_pages(db_session, material_id) == [(1, "committed old page")]

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_list_material_pages_returns_ascending_and_scoped(db_session):
    """Week 9 read API: pages come back in ascending page-number order and
    only the requested material's rows are returned."""
    owner = await _create_user(
        db_session, "material-pages-read-owner", "material-pages-read@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)
    other_material = await _create_material(db_session, course, owner)

    # Seeded raw (descending) so the read's ORDER BY is what's under test,
    # not the write path's insertion order.
    db_session.add_all(
        [
            MaterialPage(
                material_id=material.id, page_number=3, text="third page"
            ),
            MaterialPage(
                material_id=material.id, page_number=1, text="first page"
            ),
            MaterialPage(
                material_id=other_material.id, page_number=2, text="other material"
            ),
        ]
    )
    await db_session.commit()

    pages = await list_material_pages(db_session, material.id)

    assert [(page.page_number, page.text) for page in pages] == [
        (1, "first page"),
        (3, "third page"),
    ]

    await db_session.delete(owner)
    await db_session.commit()


@pytest.mark.asyncio
async def test_list_material_pages_empty_when_no_output(db_session):
    """Week 9 read API: a material with no persisted output — not yet
    processed, processing, or failed — reads back as an empty sequence."""
    owner = await _create_user(
        db_session, "material-pages-empty-owner", "material-pages-empty@example.com"
    )
    course = await _create_course(db_session, owner)
    material = await _create_material(db_session, course, owner)

    assert await list_material_pages(db_session, material.id) == []

    await db_session.delete(owner)
    await db_session.commit()
