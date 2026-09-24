"""Week 7 Celery publisher for material processing.

Backend-owned glue: publishes the material-processing task by name via
``send_task`` so the AI/ML task implementation is never imported here. The
Celery app is imported lazily (at call time) to avoid the ``REDIS_PASSWORD``
import-time requirement in ``app.workers.celery_app``.
"""

import asyncio
import uuid
from importlib import import_module

MATERIAL_PROCESSING_TASK_NAME = "app.workers.tasks.material_tasks.process_material"


def _celery_app():
    return import_module("app.workers.celery_app").celery_app


async def enqueue_material_processing(
    material_id: uuid.UUID,
    s3_key: str,
    course_id: uuid.UUID,
    owner_id: uuid.UUID,
) -> str:
    """Publish the processing task and return the Celery task id as the job id."""
    celery_app = _celery_app()
    result = await asyncio.to_thread(
        celery_app.send_task,
        MATERIAL_PROCESSING_TASK_NAME,
        args=[
            str(material_id),
            s3_key,
            str(course_id),
            str(owner_id),
        ],
    )
    return str(result.id)
