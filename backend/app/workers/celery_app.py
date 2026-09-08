import os

from celery import Celery


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
    include=["app.workers.tasks.sample"],
)


celery_app.conf.update(
    # Serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # Redis startup retry
    broker_connection_retry_on_startup=True,

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

