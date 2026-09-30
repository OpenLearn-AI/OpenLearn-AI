"""F9 worker-side Sentry initialization tests.

``app.workers.celery_app`` raises at import time unless ``REDIS_PASSWORD`` is
set, so the environment variable is configured *before* the module import
below (same pattern as ``tests/test_material_tasks.py``).

These tests prove that the ``worker_process_init`` handler registered on the
Celery app initializes the Sentry SDK inside each forked worker process with
the Celery integration, and that an empty/missing ``SENTRY_DSN`` stays a
no-op. ``sentry_sdk.init`` is monkeypatched with a recorder, so nothing is
ever sent to the external Sentry service.
"""

import os

os.environ.setdefault("REDIS_PASSWORD", "test-redis-password")

from celery.signals import worker_process_init  # noqa: E402

import sentry_sdk  # noqa: E402
from sentry_sdk.integrations.celery import CeleryIntegration  # noqa: E402

from app.workers import celery_app  # noqa: E402

FAKE_SENTRY_DSN = "https://0123456789abcdef@o000000.ingest.sentry.io/0000000"


def _recorded_init():
    calls = []

    def record_init(**kwargs):
        calls.append(kwargs)

    return calls, record_init


def test_worker_process_init_initializes_sentry_with_celery_integration(monkeypatch):
    monkeypatch.setenv("SENTRY_DSN", FAKE_SENTRY_DSN)
    monkeypatch.setenv("ENVIRONMENT", "staging")
    calls, record_init = _recorded_init()
    monkeypatch.setattr(sentry_sdk, "init", record_init)

    worker_process_init.send(sender=celery_app.celery_app)

    assert len(calls) == 1
    init_kwargs = calls[0]
    assert init_kwargs["dsn"] == FAKE_SENTRY_DSN
    assert init_kwargs["environment"] == "staging"
    assert init_kwargs["traces_sample_rate"] == 1.0
    assert any(
        isinstance(integration, CeleryIntegration)
        for integration in init_kwargs["integrations"]
    )


def test_worker_process_init_uses_staging_environment_default(monkeypatch):
    monkeypatch.setenv("SENTRY_DSN", FAKE_SENTRY_DSN)
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    calls, record_init = _recorded_init()
    monkeypatch.setattr(sentry_sdk, "init", record_init)

    worker_process_init.send(sender=celery_app.celery_app)

    assert calls[0]["environment"] == "staging"


def test_worker_process_init_is_noop_when_sentry_dsn_missing(monkeypatch):
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    calls, record_init = _recorded_init()
    monkeypatch.setattr(sentry_sdk, "init", record_init)

    worker_process_init.send(sender=celery_app.celery_app)

    assert calls == []


def test_worker_process_init_is_noop_when_sentry_dsn_empty(monkeypatch):
    monkeypatch.setenv("SENTRY_DSN", "")
    calls, record_init = _recorded_init()
    monkeypatch.setattr(sentry_sdk, "init", record_init)

    worker_process_init.send(sender=celery_app.celery_app)

    assert calls == []


def test_worker_process_init_handler_registered_on_celery_app_import():
    assert worker_process_init.has_listeners(sender=celery_app.celery_app) is True