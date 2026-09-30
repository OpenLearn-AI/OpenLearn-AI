import os

from celery import Celery
from celery.signals import worker_process_init


REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

if not REDIS_PASSWORD:
    raise RuntimeError(
        "REDIS_PASSWORD environment variable is not set"
    )


REDIS_URL = f"redis://:{REDIS_PASSWORD}@redis:6379"

CELERY_BROKER_URL = f"{REDIS_URL}/0"
CELERY_RESULT_BACKEND = f"{REDIS_URL}/1"


celery_app = Celery(
    "openlearn",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        "app.workers.tasks.sample",
        "app.workers.tasks.material_tasks",
    ],
)


celery_app.conf.update(
    # Serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # Redis startup retry
    broker_connection_retry_on_startup=True,

    # Task time limits (W7 F10): soft 10m / hard 11m. SoftTimeLimitExceeded
    # feeds the existing material failure path (result: failed). The hard
    # kill / OOM / container restart case remains the documented W7 residual
    # gap; no reaper is built.
    task_soft_time_limit=600,
    task_time_limit=660,

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task routing
    task_routes={
        "app.workers.tasks.ocr_tasks.*": {
            "queue": "ocr_queue",
        },
    },

    # Celery Beat
    beat_schedule={},
)


@worker_process_init.connect
def _initialize_worker_process_sentry(**kwargs) -> None:
    """F9: initialize Sentry in each forked Celery worker process.

    Connecting the receiver at import time only registers the handler; the SDK
    is initialized per worker process when the signal fires — never in the
    master process and never via the API's full observability setup.
    """
    from app.observability import setup_worker_sentry

    setup_worker_sentry()

