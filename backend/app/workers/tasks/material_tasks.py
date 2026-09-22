"""Week 7 material-processing Celery task.

``process_material`` is the task consumed by name through
``app.workers.publishing.enqueue_material_processing``. It owns the
worker-side database session (``AsyncSessionLocal``) and drives the material
status lifecycle exclusively through the existing material service transition
rules. The content-processing step is a deliberate seam: no backend processing
callable exists yet, so the task never fabricates a ``ready`` result.
"""

import asyncio
import uuid

import structlog

from app.db.session import AsyncSessionLocal
from app.models.material import FAILED_STATUS, PROCESSING_STATUS, READY_STATUS, Material
from app.services.material_service import (
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
    return asyncio.run(_handle_material(material_id, s3_key, course_id, owner_id))


async def _handle_material(
    material_id: str,
    s3_key: str,
    course_id: str,
    owner_id: str,
) -> str | None:
    """Execute the status lifecycle for one material; returns the final status.

    Aborts (returns None) when the material does not exist. A transition
    rejected by ``transition_material_status`` propagates and leaves the stored
    status untouched; a failure inside content processing marks the material
    ``failed`` (committed) and re-raises.
    """
    material_uuid = uuid.UUID(material_id)

    async with AsyncSessionLocal() as session:
        material = await get_material_by_id(session, material_uuid)
        if material is None:
            logger.warning(
                "material_processing_aborted_material_not_found",
                material_id=material_id,
                s3_key=s3_key,
            )
            return None

        await transition_material_status(session, material, PROCESSING_STATUS)
        await session.commit()

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
            await transition_material_status(session, material, FAILED_STATUS)
            await session.commit()
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