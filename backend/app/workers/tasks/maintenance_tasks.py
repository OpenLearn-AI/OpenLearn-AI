"""Periodic maintenance tasks (scheduled by Celery Beat)."""

import asyncio
from datetime import timedelta

import structlog
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.services.material_service import fail_stuck_materials
from app.workers.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(name="app.workers.tasks.maintenance_tasks.reap_stuck_materials")
def reap_stuck_materials() -> int:
    """Mark materials stuck in ``pending``/``processing`` as ``failed``.

    Covers a lost enqueue or a worker killed past the Celery time limits
    (review finding B-07). The owner can then retry manually. Returns the
    number of materials moved to ``failed``.
    """

    async def _run() -> int:
        # Task-local engine, disposed before the loop closes (same ownership
        # model as ``process_material``).
        engine = create_async_engine(settings.database_url)
        session_factory = async_sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False
        )
        try:
            async with session_factory() as session:
                stuck_ids = await fail_stuck_materials(
                    session,
                    timedelta(minutes=settings.material_stuck_timeout_minutes),
                )
        finally:
            await engine.dispose()
        for material_id in stuck_ids:
            logger.warning("material_stuck_marked_failed", material_id=str(material_id))
        return len(stuck_ids)

    return asyncio.run(_run())
