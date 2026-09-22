"""Focused unit tests for the Week 7 Celery publisher.

The publisher must dispatch by task name via ``send_task`` with JSON-safe
string arguments, and must not import ``app.workers.celery_app`` (which raises
unless ``REDIS_PASSWORD`` is set) at module import time.
"""

import uuid

import pytest

from app.workers import publishing


class FakeTaskResult:
    def __init__(self, task_id: str):
        self.id = task_id


class FakeCeleryApp:
    def __init__(self):
        self.calls = []

    def send_task(self, name, args=None):
        self.calls.append((name, args))
        return FakeTaskResult(task_id=f"job-{len(self.calls)}")


@pytest.mark.asyncio
async def test_enqueue_material_processing_sends_by_task_name_with_string_args(
    monkeypatch,
):
    fake_app = FakeCeleryApp()
    monkeypatch.setattr(publishing, "_celery_app", lambda: fake_app)

    material_id = uuid.uuid4()
    course_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    s3_key = f"courses/{course_id}/materials/lecture-1.pdf"

    job_id = await publishing.enqueue_material_processing(
        material_id,
        s3_key,
        course_id,
        owner_id,
    )

    assert len(fake_app.calls) == 1
    name, args = fake_app.calls[0]

    assert name == "app.workers.tasks.material_tasks.process_material"
    assert name == publishing.MATERIAL_PROCESSING_TASK_NAME

    assert args == [
        str(material_id),
        s3_key,
        str(course_id),
        str(owner_id),
    ]

    assert isinstance(args[0], str)
    assert args[0] == str(material_id)
    assert isinstance(args[1], str)
    assert args[1] == s3_key
    assert isinstance(args[2], str)
    assert args[2] == str(course_id)
    assert isinstance(args[3], str)
    assert args[3] == str(owner_id)

    assert job_id == "job-1"


@pytest.mark.asyncio
async def test_enqueue_material_processing_returns_task_id_unchanged(monkeypatch):
    fake_app = FakeCeleryApp()
    monkeypatch.setattr(publishing, "_celery_app", lambda: fake_app)

    material_id = uuid.uuid4()
    course_id = uuid.uuid4()
    owner_id = uuid.uuid4()

    job_id = await publishing.enqueue_material_processing(
        material_id,
        "some-object-key.pdf",
        course_id,
        owner_id,
    )

    assert job_id == "job-1"
