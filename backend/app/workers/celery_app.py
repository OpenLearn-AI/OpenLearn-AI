from celery import Celery
from celery.signals import worker_process_init

from app.config import settings


# Broker/result Redis location, resolved through the shared pydantic settings
# contract (app.config.Settings.redis_connection_url) so that the API process
# started with the documented command (uvicorn app.main:app --reload --port
# 8000) and the worker started via scripts/run-worker-dev.sh receive
# COMPATIBLE settings:
#
#   precedence: process environment (REDIS_URL / REDIS_PASSWORD)
#             > backend/.env
#             > repository-root .env.local (written by scripts/setup-dev.sh)
#             > Settings defaults
#
# The default host stays "redis" — the container-network hostname used by
# staging and by any compose-hosted worker. Local host processes point at the
# loopback-published Redis via REDIS_URL, which scripts/setup-dev.sh writes
# into .env.local and scripts/run-worker-dev.sh also exports. Nothing sets
# these variables in staging, so the composed default below is byte-identical
# to the previous hardcode. An unresolvable configuration raises immediately
# with an actionable diagnostic (see app/config.py) — it must never fall back
# to an unauthenticated default.
REDIS_URL = settings.redis_connection_url

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
        # W8: material processing → dedicated ingestion queue. Heavy work
        # (OCR + embeddings) stays isolated from lightweight tasks.
        "app.workers.tasks.material_tasks.process_material": {
            "queue": "ingestion_queue",
        },
    },

    # Retry policy (W8): the atomic pending→processing claim
    # (claim_pending_material) makes re-delivery idempotent — a retried
    # task whose material is no longer pending returns the current status
    # without reprocessing. Backoff respects transient upstream failures.
    task_annotations={
        "app.workers.tasks.material_tasks.process_material": {
            "max_retries": 3,
            "default_retry_delay": 60,
            "retry_backoff": True,
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
