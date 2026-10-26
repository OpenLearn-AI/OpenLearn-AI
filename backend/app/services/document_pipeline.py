"""Document pipeline composition (AI Week 7–8; Stage 1 = batch B2, Stage 2 = batch B3).

Composes the existing, independently tested application services into the
two stage boundaries fixed by the approved B1 decisions
(``docs/tasks/ai-week7-8/decisions.md`` §2.1, §2.2, and §4):

.. code-block:: text

    Stage 1 (B2):

    local source path
        →  ingest_document()             (Docling extraction; synchronous)
        →  targeted OCR enrichment       (async; PDF-only per B1 decision (c))
        →  enriched CanonicalDocument

    Stage 2 (B3):

    enriched CanonicalDocument
        →  chunk_document()              (existing deterministic chunker; synchronous)
        →  empty-input guard             (skipped=True no-op; zero provider calls)
        →  embed_batch()                 (async; batch_size-sized batches, order kept)
        →  VectorRecord construction     (id = {material_id}:{chunk_id}; JSONB provenance)
        →  vector_db_provider.upsert()   (async; exactly one call for the full set)
        →  PersistResult

This module is composition only, per ADR-0009 and ADR-0001:

* it duplicates no ingestion/OCR/chunking logic — the existing services remain
  the sole authority for extraction, the OCR quality gate
  (``settings.ocr_min_text_chars``), OCR text replacement, OCR metadata,
  page-artifact rendering, and deterministic chunking (``None`` sizes fall
  through to ``settings.chunk_size``/``settings.chunk_overlap`` inside the
  chunker itself);
* it adds no pipeline class, registry, stage framework, plugin machinery, or
  retry/fallback policy — provider errors propagate unchanged (the PAL layer
  owns error normalization, the router owns provider fallback, and the Celery
  layer owns task retry/routes);
* it imports no provider SDK — providers and the page-source resolver are
  injected (TS §7.3); the only PAL imports are interface contracts and PAL
  DTOs (``OCRInterface``, ``EmbeddingInterface``, ``VectorDBInterface``,
  ``EmbeddingResult``, ``VectorRecord``);
* ``ingest_document()`` is called synchronously and directly: the future
  caller (B5) invokes this async stage from the Celery task's existing
  task-local event loop, where a CPU-bound blocking call delays nothing else
  (B1 decision (a) sync/async boundary);
* it does not touch the Celery task, the material lifecycle, storage, or any
  provider implementation (B5 wires the seam);
* Stage 2 depends only on the frozen PAL interfaces, never on BGE-M3 or
  pgvector; it calls ``upsert()`` exactly once for the complete record set
  and never commits — the vector provider executes on the caller's
  transaction (decisions.md §2.4) and the session/transaction lifecycle is
  the B5 seam's responsibility. Vector-record identity is
  ``{material_id}:{chunk_id}`` because ``document_id`` is the source file
  stem (TS §11.3) and would collide across materials; ``chunk_id``,
  ``document_id``, and page references survive inside the record's JSONB
  provenance payload (decisions.md §2.2).

PDF detection follows the exact suffix rule the PDF OCR components already
enforce (``.pdf``, case-insensitive), so behavior can never disagree between
layers. Non-PDF sources are outside the Week 7–8 targeted-OCR scope: they
skip OCR gracefully — no resolver call, no provider call, no error — and
record the document-level metadata note defined by B1 decision (c).
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from app.documents import CanonicalDocument
from app.documents.chunking import Chunk, chunk_document
from app.pal.interfaces.embedding import EmbeddingInterface
from app.pal.interfaces.ocr import OCRInterface
from app.pal.interfaces.vector_db import VectorDBInterface
from app.pal.models.types import EmbeddingResult, VectorRecord
from app.services.ingestion import ingest_document
from app.services.ocr import PageSourceResolver, enrich_document_with_ocr
from app.services.ocr_source import pdf_page_source_resolver

#: Document-level metadata key for the Stage-1 OCR disposition. The page-level
#: OCR enrichment uses the same key on ``Page.metadata``; this module records
#: the skip disposition for non-PDF sources at the document level only.
_OCR_METADATA_KEY = "ocr"

#: Document-level note recorded for sources outside the Week 7–8 targeted-OCR
#: scope (B1 decision (c), decisions.md §4). Copied per document so the note
#: dict is never shared or mutated across calls.
_OCR_SKIP_NOTE: dict[str, object] = {
    "applied": False,
    "skipped": True,
    "reason": "non_pdf_source_not_in_week7_8_ocr_scope",
}


def _is_pdf_source(source_path: str | Path) -> bool:
    """Return True when ``source_path`` has the ``.pdf`` suffix.

    Same rule as ``create_single_page_pdf`` and the Gemini provider enforce,
    per decisions.md §4 — suffix of the local path only; no MIME sniffing and
    no content inspection.
    """
    return Path(source_path).suffix.lower() == ".pdf"


async def ingest_and_enrich(
    source_path: str | Path,
    *,
    ocr_provider: OCRInterface,
    page_source_resolver: PageSourceResolver | None = None,
) -> CanonicalDocument:
    """Ingest a local document and apply Week 7–8 targeted-OCR enrichment.

    Behavior:

    * Ingestion always runs first via the existing synchronous
      :func:`app.services.ingestion.ingest_document`; its typed errors
      (``DocumentNotFoundError``, ``UnsupportedDocumentTypeError``,
      ``DocumentConversionError``) propagate unchanged.
    * PDF sources (``.pdf`` suffix): OCR enrichment runs through the existing
      :func:`app.services.ocr.enrich_document_with_ocr` — only pages below
      ``settings.ocr_min_text_chars`` are processed, each eligible page's
      source artifact is obtained from the resolver and passed verbatim to
      ``ocr_provider.extract_text``, and the OCR result replaces the page
      text with the ``ocr`` metadata merged (existing service contract).
      When ``page_source_resolver`` is ``None``, the existing
      :func:`app.services.ocr_source.pdf_page_source_resolver` is used;
      its single-page artifacts are written deterministically next to the
      source file (cleanup of the caller's task-local temporary directory
      is the B5 seam's responsibility per decisions.md §5).
    * Non-PDF sources: the provider and resolver are never invoked and no
      error is raised; the document is returned with the B1 (c) skip note
      merged into ``document.metadata["ocr"]`` — every pre-existing
      metadata key is preserved.

    All exceptions raised by the OCR provider propagate unchanged: this
    stage implements no retry, fallback, or error conversion.
    """
    # Step 1 — ingestion: the existing Docling service, unchanged and
    # called synchronously (B1 (a) sync/async boundary).
    document = ingest_document(source_path)

    # Step 2 — Week 7–8 targeted OCR is PDF-only (B1 decision (c)).
    if not _is_pdf_source(source_path):
        document.metadata = {
            **document.metadata,
            _OCR_METADATA_KEY: dict(_OCR_SKIP_NOTE),
        }
        return document

    # Step 3 — PDF path: default to the existing PDF page-source resolver;
    # an explicitly injected resolver is used verbatim.
    resolver = (
        page_source_resolver
        if page_source_resolver is not None
        else pdf_page_source_resolver()
    )
    return await enrich_document_with_ocr(document, ocr_provider, resolver)


# ---------------------------------------------------------------------------
# Stage 2 — chunk → embed → persist (batch B3)
# ---------------------------------------------------------------------------


class PersistResult(BaseModel):
    """Per-document outcome of Stage 2 (decisions.md §2.2).

    ``chunk_count`` is the number of chunks the existing chunker produced;
    ``embedded_count`` the number of chunks actually embedded;
    ``upserted_count`` the number of vector records handed to the provider;
    ``vector_ids`` the storage ids in chunk order. ``skipped`` is ``True``
    only for the empty-input no-op (no chunks → zero provider calls).
    """

    material_id: str
    document_id: str
    chunk_count: int
    embedded_count: int
    upserted_count: int
    vector_ids: list[str]
    skipped: bool = False


def _vector_provenance(
    material_id: str, document: CanonicalDocument, chunk: Chunk
) -> dict[str, object]:
    """Build the JSONB provenance payload for one chunk (decisions.md §2.2).

    Every value is derived from the existing chunk/document fields — the
    pipeline invents no provenance of its own. ``char_count``/``page_count``
    mirror the chunker's own definitions (``len(chunk.text)`` /
    ``len(chunk.pages)``; ``documents/chunking.py`` records the same values
    in ``chunk.metadata``).
    """
    return {
        "material_id": material_id,
        "document_id": document.document_id,
        "chunk_id": chunk.chunk_id,
        "pages": chunk.pages,
        "section": chunk.section,
        "language": chunk.language,
        "char_count": len(chunk.text),
        "page_count": len(chunk.pages),
    }


async def chunk_embed_and_persist(
    document: CanonicalDocument,
    *,
    material_id: str,
    embedding_provider: EmbeddingInterface,
    vector_db_provider: VectorDBInterface,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    batch_size: int = 16,
) -> PersistResult:
    """Turn an enriched document into queryable vector rows (Stage 2).

    Behavior:

    * Chunking runs first via the existing deterministic
      :func:`app.documents.chunking.chunk_document`, called synchronously
      (B1 §2.3 sync/async boundary); ``chunk_size``/``chunk_overlap`` are
      passed through verbatim — ``None`` falls through to
      ``settings.chunk_size``/``settings.chunk_overlap`` inside the chunker,
      which stays the sole chunking authority.
    * Empty-input guard: a document with no usable text yields zero chunks
      and a ``skipped=True`` :class:`PersistResult` — the embedding provider
      and the vector store are never invoked.
    * Embedding is batched: :meth:`EmbeddingInterface.embed_batch` is called
      once per ``batch_size``-sized slice of the chunk list and the results
      are extended in submission order (provider contract: one result per
      input, in input order). No assumption is made about the chunk count
      relative to ``batch_size``.
    * Each chunk/embedding pair becomes one existing
      :class:`app.pal.models.types.VectorRecord` with storage id
      ``{material_id}:{chunk_id}`` (``material_id`` scoping keeps different
      materials independent while same-material re-ingestion stays
      idempotent — the postgres provider upserts on id conflict),
      ``content = chunk.text``, and the full provenance payload.
    * Persistence: :meth:`VectorDBInterface.upsert` is called exactly once
      for the complete record set — never once per embedding batch — and
      never commits; the caller owns the transaction (B5).
    * A ``batch_size`` below 1 is a caller programming error and raises
      ``ValueError`` before any work (same validation style as the chunker's
      own parameter checks).

    All provider exceptions propagate unchanged: this stage implements no
    retry, fallback, error conversion, or exception swallowing.
    """
    if batch_size < 1:
        raise ValueError(f"batch_size must be >= 1, got {batch_size}")

    # Step 1 — chunking: the existing deterministic chunker; ``None`` sizes
    # fall through to the settings defaults inside it.
    chunks: list[Chunk] = chunk_document(
        document, chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    # Step 2 — empty-input guard: a true provider no-op (decisions.md §2.2).
    if not chunks:
        return PersistResult(
            material_id=material_id,
            document_id=document.document_id,
            chunk_count=0,
            embedded_count=0,
            upserted_count=0,
            vector_ids=[],
            skipped=True,
        )

    # Step 3 — batched embedding: one call per batch, order preserved.
    embeddings: list[EmbeddingResult] = []
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        embeddings.extend(
            await embedding_provider.embed_batch([chunk.text for chunk in batch])
        )

    # Step 4 — VectorRecord construction (id = {material_id}:{chunk_id}).
    records = [
        VectorRecord(
            id=f"{material_id}:{chunk.chunk_id}",
            vector=embedding.vector,
            content=chunk.text,
            metadata=_vector_provenance(material_id, document, chunk),
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]

    # Step 5 — a single upsert for the complete record set; the provider
    # never commits (the caller owns the transaction, B5).
    await vector_db_provider.upsert(records)

    return PersistResult(
        material_id=material_id,
        document_id=document.document_id,
        chunk_count=len(chunks),
        embedded_count=len(embeddings),
        upserted_count=len(records),
        vector_ids=[record.id for record in records],
        skipped=False,
    )
