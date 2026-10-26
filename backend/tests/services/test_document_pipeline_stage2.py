"""Unit tests for the Stage-2 pipeline composition (B3).

Covers ``app.services.document_pipeline.chunk_embed_and_persist`` — the
composition of the existing deterministic chunker with injected PAL
embedding/vector providers only. Following the repository's established
conventions:

* the real ``chunk_document()`` runs against hand-built
  ``CanonicalDocument`` fixtures (the chunker is deterministic and
  dependency-free; its own suite lives in
  ``tests/documents/test_chunking.py``) — the tests never re-implement
  chunking, they use the real chunker as the oracle for expected chunk
  texts/ids;
* the embedding and vector-store providers are deterministic in-process
  fakes bound to the frozen PAL interfaces (same isolation strategy as
  ``tests/services/test_ocr.py`` and the Stage-1 suite) — no model load,
  no database, no network;
* async tests carry explicit ``@pytest.mark.asyncio`` markers for the
  repository's strict asyncio mode.
"""

from __future__ import annotations

import pytest

from app.documents import CanonicalDocument, Page
from app.documents.chunking import chunk_document
from app.pal.exceptions import ProviderTimeoutError
from app.pal.interfaces.embedding import EmbeddingInterface
from app.pal.interfaces.vector_db import VectorDBInterface
from app.pal.models.types import EmbeddingResult, HealthStatus, VectorRecord
from app.services.document_pipeline import PersistResult, chunk_embed_and_persist

# ---------------------------------------------------------------------------
# Document fixtures (paragraph discipline → exactly one chunk per paragraph)
# ---------------------------------------------------------------------------


def _paragraph(index: int) -> str:
    """A distinct paragraph whose width cycles 60–64 characters.

    With ``chunk_size=100`` and ``chunk_overlap=0`` no two paragraphs ever
    pack into one chunk (any join exceeds 100 chars), so a document built
    from N paragraphs deterministically produces exactly N chunks — without
    the tests hardcoding anything about the chunker's internals.
    """
    width = 60 + (index % 5)
    prefix = f"chunk-{index:04d} "
    return prefix + "x" * (width - len(prefix))


def _make_document(
    paragraphs: list[str],
    *,
    document_id: str = "lecture",
    language: str | None = "en",
    section: str | None = "Chapter 1",
) -> CanonicalDocument:
    """A one-page document whose text is the blank-line-joined paragraphs."""
    page_metadata: dict[str, object] = {"section": section} if section else {}
    return CanonicalDocument(
        document_id=document_id,
        source=f"/tmp/{document_id}.pdf",
        language=language,
        pages=[
            Page(
                page_number=1,
                text="\n\n".join(paragraphs),
                metadata=page_metadata,
            )
        ],
    )


# ---------------------------------------------------------------------------
# PAL contract fakes (same isolation strategy as the Stage-1 suite)
# ---------------------------------------------------------------------------


def _vector_for(text: str, dimension: int) -> list[float]:
    """Deterministic vector, pure function of the text (leads with length)."""
    base = float(len(text))
    return [base + i / 100 for i in range(dimension)]


class FakeEmbeddingProvider(EmbeddingInterface):
    """Deterministic embedding provider recording every batch call.

    ``calls`` records one entry per ``embed_batch`` invocation (the exact
    text list submitted), so tests can assert batch count, batch sizes, and
    submission order. The returned vector is a pure function of the input
    text, so tests can assert the chunk→embedding pairing survived batching.
    When ``error`` is set, ``embed_batch`` raises it (after recording the
    attempted call), mirroring the Stage-1 fake's failure convention.
    """

    provider_name = "fake-embedding"

    def __init__(self, dimension: int = 8, error: Exception | None = None) -> None:
        self._dimension = dimension
        self.calls: list[list[str]] = []
        self.error = error

    @property
    def dimension(self) -> int:
        return self._dimension

    async def health_check(self) -> HealthStatus:
        return HealthStatus(healthy=True, provider=self.provider_name, message="ok")

    async def embed(self, text: str) -> EmbeddingResult:
        return (await self.embed_batch([text]))[0]

    async def embed_batch(self, texts) -> list[EmbeddingResult]:
        batch = list(texts)  # defensive copy; record exactly what was submitted
        self.calls.append(batch)
        if self.error is not None:
            raise self.error
        return [
            EmbeddingResult(
                vector=_vector_for(text, self._dimension),
                dimension=self._dimension,
                model="fake-embedding-model",
                provider=self.provider_name,
            )
            for text in batch
        ]


class FakeVectorDBProvider(VectorDBInterface):
    """Deterministic vector store recording every upsert payload.

    ``upserts`` records one entry per ``upsert`` invocation (the exact
    record list submitted). The non-persistence operations raise
    ``AssertionError`` so tests fail loudly if Stage 2 ever called them.
    """

    provider_name = "fake-vector-db"

    def __init__(self, error: Exception | None = None) -> None:
        self.upserts: list[list[VectorRecord]] = []
        self.error = error

    async def health_check(self) -> HealthStatus:
        return HealthStatus(healthy=True, provider=self.provider_name, message="ok")

    async def upsert(self, records: list[VectorRecord]) -> None:
        self.upserts.append(list(records))
        if self.error is not None:
            raise self.error

    async def search(self, vector, *, top_k=5, filters=None):
        raise AssertionError("Stage 2 must never call search()")

    async def get(self, id):
        raise AssertionError("Stage 2 must never call get()")

    async def delete(self, *, ids=None, filters=None):
        raise AssertionError("Stage 2 must never call delete()")


# ---------------------------------------------------------------------------
# Test A — basic pipeline: chunk → embed → records → one upsert → result
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_basic_pipeline_chunks_embeds_and_upserts_once() -> None:
    document = _make_document([_paragraph(i) for i in range(3)])
    embedding = FakeEmbeddingProvider()
    vector_db = FakeVectorDBProvider()

    result = await chunk_embed_and_persist(
        document,
        material_id="mat-1",
        embedding_provider=embedding,
        vector_db_provider=vector_db,
        chunk_size=100,
        chunk_overlap=0,
    )

    chunks = chunk_document(document, chunk_size=100, chunk_overlap=0)
    assert len(chunks) == 3

    assert result.material_id == "mat-1"
    assert result.document_id == "lecture"
    assert result.chunk_count == 3
    assert result.embedded_count == 3
    assert result.upserted_count == 3
    assert result.skipped is False
    assert result.vector_ids == [f"mat-1:{chunk.chunk_id}" for chunk in chunks]

    # The real chunker produced the texts that were embedded, in order.
    assert len(embedding.calls) == 1  # 3 chunks fit one default batch of 16
    assert embedding.calls[0] == [chunk.text for chunk in chunks]

    # Exactly one upsert carrying every record, in chunk order.
    assert len(vector_db.upserts) == 1
    assert [record.id for record in vector_db.upserts[0]] == result.vector_ids


# ---------------------------------------------------------------------------
# Test B — embedding batching (35 chunks → 16 + 16 + 3; order preserved)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_embedding_batches_split_and_preserve_order() -> None:
    document = _make_document([_paragraph(i) for i in range(35)])
    embedding = FakeEmbeddingProvider()
    vector_db = FakeVectorDBProvider()

    result = await chunk_embed_and_persist(
        document,
        material_id="mat-2",
        embedding_provider=embedding,
        vector_db_provider=vector_db,
        chunk_size=100,
        chunk_overlap=0,
        batch_size=16,
    )

    chunks = chunk_document(document, chunk_size=100, chunk_overlap=0)
    assert result.chunk_count == 35
    assert result.embedded_count == 35
    assert [len(batch) for batch in embedding.calls] == [16, 16, 3]

    # Order preserved across batches: the concatenated submissions equal the
    # chunk texts in chunk order.
    flattened = [text for batch in embedding.calls for text in batch]
    assert flattened == [chunk.text for chunk in chunks]

    # The batching loop is not tuned to 35/16: a different batch size
    # reshapes the same split (10 → 10 + 10 + 10 + 5).
    embedding_alt = FakeEmbeddingProvider()
    result_alt = await chunk_embed_and_persist(
        document,
        material_id="mat-2b",
        embedding_provider=embedding_alt,
        vector_db_provider=FakeVectorDBProvider(),
        chunk_size=100,
        chunk_overlap=0,
        batch_size=10,
    )
    assert [len(batch) for batch in embedding_alt.calls] == [10, 10, 10, 5]
    assert result_alt.embedded_count == 35


# ---------------------------------------------------------------------------
# Test C — empty input: true no-op with respect to both providers
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_empty_document_is_a_true_provider_noop() -> None:
    document = _make_document(["   ", ""])  # whitespace-only: no usable text
    embedding = FakeEmbeddingProvider()
    vector_db = FakeVectorDBProvider()

    result = await chunk_embed_and_persist(
        document,
        material_id="mat-3",
        embedding_provider=embedding,
        vector_db_provider=vector_db,
    )

    assert result == PersistResult(
        material_id="mat-3",
        document_id="lecture",
        chunk_count=0,
        embedded_count=0,
        upserted_count=0,
        vector_ids=[],
        skipped=True,
    )
    assert embedding.calls == []  # embed_batch never called
    assert vector_db.upserts == []  # upsert never called


# ---------------------------------------------------------------------------
# Test D — vector id rule: {material_id}:{chunk_id}
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_vector_ids_are_scoped_by_material_id() -> None:
    document = _make_document([_paragraph(i) for i in range(3)])
    vector_db = FakeVectorDBProvider()

    result = await chunk_embed_and_persist(
        document,
        material_id="material-42",
        embedding_provider=FakeEmbeddingProvider(),
        vector_db_provider=vector_db,
        chunk_size=100,
        chunk_overlap=0,
    )

    chunks = chunk_document(document, chunk_size=100, chunk_overlap=0)
    expected = [f"material-42:{chunk.chunk_id}" for chunk in chunks]
    assert [record.id for record in vector_db.upserts[0]] == expected
    assert result.vector_ids == expected

    # The storage id is material-scoped, NOT document-scoped: document_id is
    # the source file stem and would collide across materials
    # (decisions.md §2.2). chunk_id itself already begins with the stem.
    for record in vector_db.upserts[0]:
        assert record.id.startswith("material-42:")
        assert record.id != (
            f"{record.metadata['document_id']}:{record.metadata['chunk_id']}"
        )


# ---------------------------------------------------------------------------
# Test E — provenance payload: exactly the decided fields, real values
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_records_carry_full_chunk_provenance() -> None:
    document = _make_document(
        [_paragraph(0), _paragraph(1)],
        document_id="handout",
        language="ar",
        section="Chapter 2",
    )
    vector_db = FakeVectorDBProvider()

    await chunk_embed_and_persist(
        document,
        material_id="mat-5",
        embedding_provider=FakeEmbeddingProvider(),
        vector_db_provider=vector_db,
        chunk_size=100,
        chunk_overlap=0,
    )

    chunks = chunk_document(document, chunk_size=100, chunk_overlap=0)
    assert len(vector_db.upserts) == 1
    for record, chunk in zip(vector_db.upserts[0], chunks):
        # Exact-key equality: no invented fields, none missing.
        assert record.metadata == {
            "material_id": "mat-5",
            "document_id": "handout",
            "chunk_id": chunk.chunk_id,
            "pages": chunk.pages,
            "section": "Chapter 2",
            "language": "ar",
            "char_count": len(chunk.text),
            "page_count": len(chunk.pages),
        }


# ---------------------------------------------------------------------------
# Test F — content: VectorRecord.content == chunk.text
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_record_content_is_the_chunk_text() -> None:
    document = _make_document([_paragraph(i) for i in range(3)])
    vector_db = FakeVectorDBProvider()

    await chunk_embed_and_persist(
        document,
        material_id="mat-6",
        embedding_provider=FakeEmbeddingProvider(),
        vector_db_provider=vector_db,
        chunk_size=100,
        chunk_overlap=0,
    )

    chunks = chunk_document(document, chunk_size=100, chunk_overlap=0)
    for record, chunk in zip(vector_db.upserts[0], chunks):
        assert record.content == chunk.text


# ---------------------------------------------------------------------------
# Test G — multiple embedding batches still produce exactly one upsert
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_single_upsert_covers_all_embedding_batches() -> None:
    document = _make_document([_paragraph(i) for i in range(35)])
    embedding = FakeEmbeddingProvider()
    vector_db = FakeVectorDBProvider()

    result = await chunk_embed_and_persist(
        document,
        material_id="mat-7",
        embedding_provider=embedding,
        vector_db_provider=vector_db,
        chunk_size=100,
        chunk_overlap=0,
        batch_size=16,
    )

    assert len(embedding.calls) == 3  # 16 + 16 + 3 embedding batches
    assert len(vector_db.upserts) == 1  # exactly one persistence call
    assert len(vector_db.upserts[0]) == 35  # carrying the complete set
    assert result.upserted_count == 35
    chunks = chunk_document(document, chunk_size=100, chunk_overlap=0)
    assert [record.id for record in vector_db.upserts[0]] == [
        f"mat-7:{chunk.chunk_id}" for chunk in chunks
    ]


# ---------------------------------------------------------------------------
# Test H — provider errors propagate unchanged (no retry, no swallowing)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_embedding_provider_error_propagates_without_retry() -> None:
    document = _make_document([_paragraph(i) for i in range(3)])
    error = ProviderTimeoutError("embedding provider timed out")
    embedding = FakeEmbeddingProvider(error=error)
    vector_db = FakeVectorDBProvider()

    with pytest.raises(ProviderTimeoutError) as excinfo:
        await chunk_embed_and_persist(
            document,
            material_id="mat-8",
            embedding_provider=embedding,
            vector_db_provider=vector_db,
            chunk_size=100,
            chunk_overlap=0,
        )

    assert excinfo.value is error  # same instance — no wrapping, no retry
    assert len(embedding.calls) == 1  # the failing batch was attempted
    assert vector_db.upserts == []  # nothing was persisted afterwards


@pytest.mark.asyncio
async def test_vector_db_error_propagates_unchanged() -> None:
    document = _make_document([_paragraph(i) for i in range(3)])
    error = ProviderTimeoutError("vector store timed out")
    vector_db = FakeVectorDBProvider(error=error)

    with pytest.raises(ProviderTimeoutError) as excinfo:
        await chunk_embed_and_persist(
            document,
            material_id="mat-9",
            embedding_provider=FakeEmbeddingProvider(),
            vector_db_provider=vector_db,
            chunk_size=100,
            chunk_overlap=0,
        )

    assert excinfo.value is error
    assert len(vector_db.upserts) == 1  # the failing call was attempted once


# ---------------------------------------------------------------------------
# Guard — non-positive batch_size is a caller error, before any work
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_non_positive_batch_size_is_rejected() -> None:
    document = _make_document([_paragraph(0)])
    embedding = FakeEmbeddingProvider()
    vector_db = FakeVectorDBProvider()

    with pytest.raises(ValueError, match="batch_size"):
        await chunk_embed_and_persist(
            document,
            material_id="mat-10",
            embedding_provider=embedding,
            vector_db_provider=vector_db,
            chunk_size=100,
            chunk_overlap=0,
            batch_size=0,
        )

    assert embedding.calls == []  # rejected before any provider interaction
    assert vector_db.upserts == []
