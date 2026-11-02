"""Course-scoped material retrieval (Week 10 foundation, Option A).

Turns one authorized course + query into ranked chunks through the existing
PAL provider stack, with no PAL changes and no direct vector SQL:

    authorized course
        → list_materials_by_course()        (existing service, one query)
        → EmbeddingInterface.embed()        (configured PAL embedding provider)
        → VectorDBInterface.search()        per material, session-bound provider
            filters={"material_id": ...}    JSONB containment, enforced in the
                                            WHERE clause before LIMIT
        → merge, order by score desc / vector id asc, truncate to top_k
        → RetrievalResult provenance

Design decisions:

* Course scope (Option A): materials are resolved from the authorized course
  and each PAL search is filtered by ``material_id``; no client-supplied
  filter ever reaches the store. One search per material is fan-out keyed on
  materials per course — at existing material counts this is far below any
  latency concern; scaling beyond it is a measured-later decision, not
  designed for here.
* Availability: materials are not filtered by status. Vector presence governs
  retrievability — committed vectors survive failed or in-flight
  reprocessing because delete + upsert + ``ready`` share one transaction
  (see ``app/workers/tasks/material_tasks.py``), and a never-processed
  material simply contributes no candidates.
* Global top-K correctness: ``top_k`` candidates per material suffice
  because a single material can contribute at most ``top_k`` entries to any
  global top_k.
* Embedding provider lifetime: ``BGEM3EmbeddingProvider`` caches the loaded
  model on the instance, so a fresh provider per request would reload the
  model on every search. One provider is kept per
  ``(provider, dimension, model, device)`` config quadruple for the process
  lifetime — the BGE-M3 provider reads all four (dimension fixes the vector
  geometry; model and device select the loaded weights), so any change
  rebuilds it. This adds no concurrency control — encoding still runs behind
  the provider's existing ``asyncio.to_thread`` boundary.
* The vector provider is constructed per request, bound to the caller's
  session (the factory contract); it never commits.
* Candidate provenance is validated before ranking: metadata ``material_id``
  must equal the server-side material being searched (never authorization
  evidence by itself), the storage id must match the
  ``{material_id}:{chunk_id}`` contract in both halves, and ``chunk_id``,
  ``content``, ``pages`` and a finite ``score`` must be well-formed.
  Malformed candidates are skipped with a structured server-side warning
  (never the query text or document content) instead of being defaulted —
  the pipeline stamps all of these, so a violation means bad data.
* Result provenance comes from the stored JSONB metadata exactly as the
  pipeline stamped it (``app/services/document_pipeline.py``); absent or
  inconsistent provenance is rejected, never invented.
"""

from __future__ import annotations

import math
import threading
import uuid

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.pal.factory import get_embedding_provider, get_vector_db_provider
from app.pal.interfaces.embedding import EmbeddingInterface
from app.pal.models.types import VectorSearchResult
from app.schemas.retrieval import RetrievalResult
from app.services.material_service import list_materials_by_course

logger = structlog.get_logger(__name__)

_embedding_provider: EmbeddingInterface | None = None
#: (provider, dimension, model, device) — all four BGEM3 inputs.
_embedding_provider_key: tuple[str, int, str, str] | None = None
_embedding_lock = threading.Lock()


def _get_embedding_provider() -> EmbeddingInterface:
    """Return the configured embedding provider, cached per config quadruple."""
    global _embedding_provider, _embedding_provider_key
    key = (
        settings.ai_embedding_provider,
        settings.ai_embedding_dimension,
        settings.ai_embedding_model,
        settings.ai_embedding_device,
    )
    with _embedding_lock:
        if _embedding_provider is None or _embedding_provider_key != key:
            _embedding_provider = get_embedding_provider(
                provider=key[0], dimension=key[1]
            )
            _embedding_provider_key = key
    return _embedding_provider


def merge_ranked_results(
    candidates: list[VectorSearchResult],
    top_k: int,
) -> list[VectorSearchResult]:
    """Order merged candidates by score desc, vector id asc; take top_k.

    The tie-breaker makes repeated searches return the same list when
    several chunks share an identical similarity score.
    """
    candidates.sort(key=lambda candidate: (-candidate.score, candidate.id))
    return candidates[:top_k]


def candidate_provenance_error(
    candidate: VectorSearchResult,
    expected_material_id: str,
) -> str | None:
    """Return a machine-readable reason when candidate provenance is broken.

    ``expected_material_id`` is the storage-id material half of the
    server-side material currently being searched — never taken from the
    candidate. All pipeline-stamped provenance must be consistent:

    * metadata ``material_id`` equals the expected material id;
    * ``candidate.id`` follows ``{material_id}:{chunk_id}`` with both halves
      consistent (a UUID contains no colon, so the first split isolates it);
    * metadata ``chunk_id`` is a non-empty string equal to the id's suffix;
    * ``content`` is present and non-empty;
    * ``pages`` is a non-empty list of positive integers (1-based, per the
      pipeline's page conventions) — booleans are rejected although they
      would pass an ``int`` check;
    * ``score`` is a finite number.

    ``None`` means the candidate is trustworthy as stored.
    """
    metadata = candidate.metadata
    if metadata.get("material_id") != expected_material_id:
        return "metadata_material_id_mismatch"

    vector_id = candidate.id
    if not vector_id or ":" not in vector_id:
        return "malformed_vector_id"
    id_material_prefix, id_chunk_suffix = vector_id.split(":", 1)
    if id_material_prefix != expected_material_id:
        return "vector_id_material_prefix_mismatch"

    chunk_id = metadata.get("chunk_id")
    if not isinstance(chunk_id, str) or not chunk_id:
        return "missing_or_invalid_chunk_id"
    if id_chunk_suffix != chunk_id:
        return "vector_id_chunk_suffix_mismatch"

    content = candidate.content
    if not isinstance(content, str) or not content:
        return "missing_or_empty_content"

    pages = metadata.get("pages")
    if not isinstance(pages, list) or not pages:
        return "missing_or_malformed_pages"
    if any(
        not isinstance(page, int) or isinstance(page, bool) or page < 1
        for page in pages
    ):
        return "invalid_page_number"

    score = candidate.score
    if (
        not isinstance(score, (int, float))
        or isinstance(score, bool)
        or not math.isfinite(score)
    ):
        return "non_finite_score"

    return None


async def search_course_materials(
    db: AsyncSession,
    *,
    course_id: uuid.UUID,
    query: str,
    top_k: int,
) -> list[RetrievalResult]:
    """Rank chunks across a course's materials against ``query``.

    The caller must have authorized ``course_id`` first (HTTP concerns stay
    in the API layer). Raises whatever the PAL providers raise — provider
    failures are never converted here into empty results.

    Returns at most ``top_k`` results, only from materials of the course.
    """
    materials = await list_materials_by_course(db, course_id)
    if not materials:
        return []

    embedding = await _get_embedding_provider().embed(query)

    vector_db = get_vector_db_provider(session=db)
    candidates: list[VectorSearchResult] = []
    for material in materials:
        expected_material_id = str(material.id)
        for candidate in await vector_db.search(
            embedding.vector,
            top_k=top_k,
            filters={"material_id": expected_material_id},
        ):
            reason = candidate_provenance_error(candidate, expected_material_id)
            if reason is not None:
                # Structured diagnostic only: never the query text and never
                # retrieved document content.
                logger.warning(
                    "retrieval_candidate_rejected",
                    reason=reason,
                    material_id=expected_material_id,
                    vector_id=candidate.id,
                )
                continue
            candidates.append(candidate)

    return [
        RetrievalResult(
            # Validated above: the id prefix equals the searched material's
            # server-side id. No further DB access — no N+1 by construction.
            material_id=uuid.UUID(candidate.id.split(":", 1)[0]),
            chunk_id=candidate.metadata["chunk_id"],
            content=candidate.content,
            pages=candidate.metadata["pages"],
            score=candidate.score,
        )
        for candidate in merge_ranked_results(candidates, top_k)
    ]
