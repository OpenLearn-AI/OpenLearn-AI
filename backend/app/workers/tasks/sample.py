from app.workers.celery_app import celery_app


@celery_app.task
def sample_task(message: str) -> str:
    return f"Sample task completed: {message}"
