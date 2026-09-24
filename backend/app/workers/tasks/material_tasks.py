"""Week 7 material-processing Celery task.

``process_material`` is the task consumed by name through
``app.workers.publishing.enqueue_material_processing``. It drives the material
status lifecycle exclusively through the existing material service transition
rules. The content-processing step is a deliberate seam: no backend processing
callable exists yet, so the task never fabricates a ``ready`` result.

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
import uuid

import structlog
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.models.material import FAILED_STATUS, READY_STATUS, Material
from app.services.material_service import (
    claim_pending_material,
    get_material_by_id,
    transition_material_status,
)
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
) -> None:
    """[AI/ML-owned] Content-processing boundary.

    No backend processing callable exists yet; the AI/ML team provides the
    implementation behind this seam. It intentionally raises so a material is
    never marked ``ready`` without real processing.
    """
    raise NotImplementedError(
        "material content processing is not implemented yet "
        "(AI/ML-owned pipeline contract)"
    )