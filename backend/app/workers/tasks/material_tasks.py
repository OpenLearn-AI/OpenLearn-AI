"""Week 7 material-processing Celery task.

``process_material`` is the task consumed by name through
``app.workers.publishing.enqueue_material_processing``. It drives the material
status lifecycle exclusively through the existing material service transition
rules. The content-processing step (wired in batch B5) composes the AI/ML
pipeline: storage fetch → Stage 1 (ingest + targeted OCR) → Stage 2
(chunk → embed → persist), with providers built through the existing PAL
factory and the pgvector provider bound to this task's live ``AsyncSession``
so vector rows commit atomically with the ``ready`` transition (decisions.md
§2.4).

Phase 1B ownership model: each ``process_material`` invocation creates a
task-local async engine and session factory inside its own event loop
(``asyncio.run``) and disposes the engine in a ``finally`` block before that
loop closes. Pooled asyncpg connections are loop-bound, so the engine/pool
never survives from one task's event loop into the next.

W8 claiming model: the ``pending`` -> ``processing`` claim is a single atomic
conditional UPDATE (``claim_pending_material``), so concurrent or duplicate
deliveries of the same material can never claim it more than once.
"""

import asyncio
import tempfile
import uuid

import structlog
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.models.material import FAILED_STATUS, READY_STATUS, Material
from app.pal.factory import (
    get_embedding_provider,
    get_ocr_provider,
    get_vector_db_provider,
)
from app.services.document_pipeline import chunk_embed_and_persist, ingest_and_enrich
from app.services.material_service import (
    claim_pending_material,
    get_material_by_id,
    transition_material_status,
)
from app.services.storage import download_material_to_temp
from app.workers.celery_app import celery_app
from app.workers.publishing import MATERIAL_PROCESSING_TASK_NAME

logger = structlog.get_logger(__name__)


@celery_app.task(name=MATERIAL_PROCESSING_TASK_NAME)
def process_material(
    material_id: str,
    s3_key: str,
    course_id: str,
    owner_id: str,
) -> str | None:
    """Celery task entrypoint; wraps the async processing lifecycle."""

    async def _run() -> str | None:
        engine = create_async_engine(settings.database_url)
        session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        try:
            return await _handle_material(
                material_id,
                s3_key,
                course_id,
                owner_id,
                session_factory=session_factory,
            )
        finally:
            await engine.dispose()

    return asyncio.run(_run())


async def _handle_material(
    material_id: str,
    s3_key: str,
    course_id: str,
    owner_id: str,
    session_factory: async_sessionmaker[AsyncSession],
) -> str | None:
    """Execute the status lifecycle for one material; returns the final status.

    Locked 1D contract: a missing material returns ``None``; a material already
    ``processing``, ``ready``, or ``failed`` is left untouched and its current
    status string is returned (no content processing, no state change). A
    transition rejected by ``transition_material_status`` propagates and leaves
    the stored status untouched; a failure inside content processing marks the
    material ``failed`` (committed) and re-raises.

    W8: claiming is atomic. ``claim_pending_material`` performs a single
    conditional UPDATE (``pending`` -> ``processing``) that succeeds for exactly
    one worker, so duplicate or concurrent deliveries of the same material can
    never both process its content. When the claim returns ``None`` the material
    is either missing (``None`` returned) or no longer pending (current status
    returned as a no-op).

    ``session_factory`` is supplied by the caller (task-local in the Celery
    path); this function never creates engines or sessions of its own.
    """
    material_uuid = uuid.UUID(material_id)

    async with session_factory() as session:
        material = await claim_pending_material(session, material_uuid)
        if material is None:
            material = await get_material_by_id(session, material_uuid)
            if material is None:
                logger.warning(
                    "material_processing_aborted_material_not_found",
                    material_id=material_id,
                    s3_key=s3_key,
                )
                return None

            logger.info(
                "material_processing_skipped_not_pending",
                material_id=material_id,
                s3_key=s3_key,
                status=material.status,
            )
            return material.status

        try:
            await _process_material_content(
                material,
                s3_key,
                course_id,
                owner_id,
                session=session,
            )
        except Exception:
            logger.exception(
                "material_processing_failed",
                material_id=material_id,
                s3_key=s3_key,
            )
            try:
                await session.rollback()
                material = await get_material_by_id(session, material_uuid)
                if material is not None:
                    try:
                        await transition_material_status(
                            session, material, FAILED_STATUS
                        )
                        await session.commit()
                    except Exception:
                        logger.exception(
                            "material_failed_persistence_failed",
                            material_id=material_id,
                            s3_key=s3_key,
                        )
            except Exception:
                logger.exception(
                    "material_failed_recovery_failed",
                    material_id=material_id,
                    s3_key=s3_key,
                )
            raise

        await transition_material_status(session, material, READY_STATUS)
        await session.commit()
        return material.status


async def _process_material_content(
    material: Material,
    s3_key: str,
    course_id: str,
    owner_id: str,
    *,
    session: AsyncSession,
) -> None:
    """[AI/ML-owned] Content-processing boundary, wired in batch B5.

    Composition per decisions.md §5–§7 (no pipeline logic of its own):

    * fetches the stored object into a per-task temporary directory via the
      Backend-agreed storage helper; the whole directory (downloaded source
      plus OCR page artifacts) is deleted deterministically by the
      ``TemporaryDirectory`` context on success and on failure;
    * runs Stage 1 (``ingest_and_enrich``) and Stage 2
      (``chunk_embed_and_persist``) from ``app.services.document_pipeline``
      with providers built through the existing PAL factory from settings —
      no second selection mechanism, no credentials here;
    * the pgvector provider is session-backed: it receives this task's live
      ``AsyncSession`` (decisions.md §2.4), so vector upserts commit
      atomically with the caller's ``ready`` transition, and the existing
      failure path (rollback → ``failed`` → re-raise) discards partial
      vector writes;
    * synchronous calls (storage download, Docling ingestion, chunking) run
      inline — the event loop is task-local (B1 §2.3 sync/async boundary);
    * ``course_id``/``owner_id`` stay part of the pinned positional seam
      contract; the pipeline stages consume ``material.id`` and ``s3_key``.

    Any exception propagates to ``_handle_material``, which records the
    material as ``failed`` and re-raises (pinned lifecycle unchanged).
    """
    with tempfile.TemporaryDirectory(prefix="material-processing-") as temp_dir:
        local_path = download_material_to_temp(s3_key, temp_dir)

        ocr_provider = get_ocr_provider()
        document = await ingest_and_enrich(local_path, ocr_provider=ocr_provider)

        embedding_provider = get_embedding_provider()
        vector_db_provider = get_vector_db_provider(session=session)
        result = await chunk_embed_and_persist(
            document,
            material_id=str(material.id),
            embedding_provider=embedding_provider,
            vector_db_provider=vector_db_provider,
        )

        logger.info(
            "material_content_processed",
            material_id=str(material.id),
            s3_key=s3_key,
            document_id=result.document_id,
            chunk_count=result.chunk_count,
            embedded_count=result.embedded_count,
            upserted_count=result.upserted_count,
            skipped=result.skipped,
        )
