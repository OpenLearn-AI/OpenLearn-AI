"""P9-B integration tests against real PostgreSQL + pgvector (opt-in).

Isolated from the normal suite: skipped unless OPENLEARN_PG_TESTS=1 is set.
Requires the vector_records table (alembic head f3a1b7c9d4e2) on a
pgvector-enabled database. Cleanup is scoped to rows with the
'p9b-test:' id prefix created by these tests — nothing else is touched.
"""

from __future__ import annotations

import os
import uuid

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.vector_record import EMBEDDING_DIMENSION, VectorRecordModel
from app.pal.models.types import VectorRecord
from app.pal.providers.vector_db.postgres_provider import PostgresVectorDBProvider

pytestmark = pytest.mark.skipif(
    os.environ.get("OPENLEARN_PG_TESTS") != "1",
    reason="Real-PostgreSQL tests are opt-in: set OPENLEARN_PG_TESTS=1",
)

TEST_ID_PREFIX = "p9b-test:"
DSN = os.environ.get("OPENLEARN_TEST_DATABASE_URL", settings.database_url)


def _unit(axis: int) -> list[float]:
    vec = [0.0] * EMBEDDING_DIMENSION
    vec[axis] = 1.0
    return vec


def _opposite() -> list[float]:
    return [-1.0] + [0.0] * (EMBEDDING_DIMENSION - 1)


def _test_id() -> str:
    return f"{TEST_ID_PREFIX}{uuid.uuid4().hex}"


@pytest_asyncio.fixture()
async def env():
    engine = create_async_engine(DSN, pool_pre_ping=True)
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield PostgresVectorDBProvider(session), session
        # Scoped cleanup: only rows created by these tests.
        await session.execute(
            VectorRecordModel.__table__.delete().where(
                VectorRecordModel.id.like(TEST_ID_PREFIX + "%")
            )
        )
        await session.commit()
    await engine.dispose()


@pytest.mark.asyncio
async def test_upsert_get_search_update_delete_roundtrip(env) -> None:
    pg, session = env
    records = [
        VectorRecord(
            id=_test_id(),
            vector=_unit(0),
            content="same",
            metadata={"document_id": "p9b-doc", "page": 1},
        ),
        VectorRecord(
            id=_test_id(),
            vector=_unit(1),
            content="orthogonal",
            metadata={"document_id": "p9b-doc", "page": 2},
        ),
        VectorRecord(
            id=_test_id(),
            vector=_opposite(),
            content="opposite",
            metadata={"document_id": "p9b-doc", "page": 3},
        ),
    ]
    ids = [r.id for r in records]

    await pg.upsert(records)
    await session.commit()

    # get existing / missing
    got = await pg.get(ids[0])
    assert got is not None
    assert got.content == "same"
    assert len(got.vector) == EMBEDDING_DIMENSION
    assert got.metadata == {"document_id": "p9b-doc", "page": 1}
    assert await pg.get("p9b-test:missing") is None

    # cosine ordering: identical -> orthogonal -> opposite
    results = await pg.search(_unit(0), top_k=3, filters={"document_id": "p9b-doc"})
    assert [r.id for r in results] == ids
    assert results[0].score == pytest.approx(1.0, abs=1e-6)
    assert results[1].score == pytest.approx(0.0, abs=1e-6)
    assert results[2].score == pytest.approx(-1.0, abs=1e-6)

    # top_k limits the result count and keeps best-first ordering
    top1 = await pg.search(_unit(0), top_k=1, filters={"document_id": "p9b-doc"})
    assert len(top1) == 1 and top1[0].id == ids[0]

    # upsert updates the existing row and leaves other rows untouched
    await pg.upsert(
        [
            VectorRecord(
                id=ids[0],
                vector=_unit(0),
                content="updated",
                metadata={"document_id": "p9b-doc", "page": 1},
            )
        ]
    )
    await session.commit()
    assert (await pg.get(ids[0])).content == "updated"  # type: ignore[union-attr]
    assert (await pg.get(ids[1])).content == "orthogonal"  # type: ignore[union-attr]

    # delete by ids
    assert await pg.delete(ids=[ids[0], ids[1]]) == 2
    await session.commit()
    assert await pg.get(ids[0]) is None

    # delete by metadata filters removes the remaining row
    assert await pg.delete(filters={"document_id": "p9b-doc"}) == 1
    await session.commit()


@pytest.mark.asyncio
async def test_upsert_preserves_created_at_and_bumps_updated_at(env) -> None:
    pg, session = env
    record_id = _test_id()

    await pg.upsert([VectorRecord(id=record_id, vector=_unit(2), content="v1")])
    await session.commit()
    first = await session.get(VectorRecordModel, record_id)
    assert first is not None
    created_before = first.created_at
    updated_after_first = first.updated_at

    await pg.upsert([VectorRecord(id=record_id, vector=_unit(2), content="v2")])
    await session.commit()
    second = (
        await session.execute(
            select(VectorRecordModel)
            .where(VectorRecordModel.id == record_id)
            .execution_options(populate_existing=True)
        )
    ).scalar_one()

    assert second.created_at == created_before  # preserved on conflict update
    assert second.updated_at >= updated_after_first
    assert second.content == "v2"
