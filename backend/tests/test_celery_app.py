"""F9 worker-side Sentry initialization + Redis settings-contract tests.

``app.workers.celery_app`` resolves its Redis URL through
``app.config.Settings.redis_connection_url`` and raises at import time when
neither ``REDIS_URL`` nor ``REDIS_PASSWORD`` can be resolved. The shared
settings instance is made importable for the whole suite by
``tests/conftest.py``; the import below must stay after that guard (conftest
is always imported first). No test here contacts a real Redis broker.

The Sentry tests prove that the ``worker_process_init`` handler registered on
the Celery app initializes the Sentry SDK inside each forked worker process
with the Celery integration, and that an empty/missing ``SENTRY_DSN`` stays a
no-op. ``sentry_sdk.init`` is monkeypatched with a recorder, so nothing is
ever sent to the external Sentry service.
"""

from celery.signals import worker_process_init  # noqa: E402

import sentry_sdk  # noqa: E402
from sentry_sdk.integrations.celery import CeleryIntegration  # noqa: E402

from app.config import settings  # noqa: E402
from app.workers import celery_app  # noqa: E402

FAKE_SENTRY_DSN = "https://0123456789abcdef@o000000.ingest.sentry.io/0000000"


def _recorded_init():
    calls = []

    def record_init(**kwargs):
        calls.append(kwargs)

    return calls, record_init


def test_worker_process_init_initializes_sentry_with_celery_integration(monkeypatch):
    monkeypatch.setattr(settings, "sentry_dsn", FAKE_SENTRY_DSN)
    monkeypatch.setattr(settings, "environment", "staging")
    calls, record_init = _recorded_init()
    monkeypatch.setattr(sentry_sdk, "init", record_init)

    worker_process_init.send(sender=celery_app.celery_app)

    assert len(calls) == 1
    init_kwargs = calls[0]
    assert init_kwargs["dsn"] == FAKE_SENTRY_DSN
    assert init_kwargs["environment"] == "staging"
    assert init_kwargs["traces_sample_rate"] == settings.sentry_traces_sample_rate
    assert settings.sentry_traces_sample_rate == 0.1
    assert any(
        isinstance(integration, CeleryIntegration)
        for integration in init_kwargs["integrations"]
    )


def test_worker_process_init_uses_settings_environment(monkeypatch):
    monkeypatch.setattr(settings, "sentry_dsn", FAKE_SENTRY_DSN)
    monkeypatch.setattr(settings, "environment", "production")
    calls, record_init = _recorded_init()
    monkeypatch.setattr(sentry_sdk, "init", record_init)

    worker_process_init.send(sender=celery_app.celery_app)

    assert calls[0]["environment"] == "production"


def test_worker_process_init_is_noop_when_sentry_dsn_missing(monkeypatch):
    monkeypatch.setattr(settings, "sentry_dsn", "")
    calls, record_init = _recorded_init()
    monkeypatch.setattr(sentry_sdk, "init", record_init)

    worker_process_init.send(sender=celery_app.celery_app)

    assert calls == []


def test_worker_process_init_is_noop_when_sentry_dsn_empty(monkeypatch):
    monkeypatch.setattr(settings, "sentry_dsn", "")
    calls, record_init = _recorded_init()
    monkeypatch.setattr(sentry_sdk, "init", record_init)

    worker_process_init.send(sender=celery_app.celery_app)

    assert calls == []


def test_worker_process_init_handler_registered_on_celery_app_import():
    assert worker_process_init.has_listeners(sender=celery_app.celery_app) is True


# ---------------------------------------------------------------------------
# Redis URL resolution (Redis settings contract)
#
# ``REDIS_URL`` is module-level state computed at import time from the shared
# pydantic settings instance, so the tests below patch that instance's fields
# (deterministic regardless of the developer's local env files, because the
# process environment / env-file values are irrelevant once the attributes are
# patched) and re-import the module through importlib.
#
# The default (no explicit redis_url) must compose from password/host/port and
# keep the container-network hostname the staging compose network provides;
# the explicit-URL override must be honored verbatim so the host-run local
# worker and the documented plain-uvicorn API process can point at
# 127.0.0.1:6379; an unresolvable configuration must raise the actionable
# RuntimeError from app.config instead of inventing a default.
# ---------------------------------------------------------------------------

import importlib  # noqa: E402

import pytest  # noqa: E402


def _reimport_celery_app():
    import app.workers.celery_app as module

    reloaded = importlib.reload(module)

    # The module registers its Sentry handler via the global
    # ``worker_process_init`` signal at import time; a reload adds a second
    # listener. Disconnect the reloaded handler so the signal registry is
    # left exactly as the original import made it.
    worker_process_init.disconnect(reloaded._initialize_worker_process_sentry)

    return reloaded


def test_redis_url_default_composes_from_settings_parts(monkeypatch):
    monkeypatch.setattr(settings, "redis_url", "")
    monkeypatch.setattr(settings, "redis_password", "default-pw")
    monkeypatch.setattr(settings, "redis_host", "redis")
    monkeypatch.setattr(settings, "redis_port", 6379)

    module = _reimport_celery_app()

    assert module.REDIS_URL == "redis://:default-pw@redis:6379"
    assert module.CELERY_BROKER_URL == "redis://:default-pw@redis:6379/0"
    assert module.CELERY_RESULT_BACKEND == "redis://:default-pw@redis:6379/1"


def test_redis_url_override_is_honored(monkeypatch):
    monkeypatch.setattr(settings, "redis_url", "redis://:default-pw@127.0.0.1:6379")
    monkeypatch.setattr(settings, "redis_password", "default-pw")

    module = _reimport_celery_app()

    assert module.REDIS_URL == "redis://:default-pw@127.0.0.1:6379"
    assert module.CELERY_BROKER_URL == "redis://:default-pw@127.0.0.1:6379/0"
    assert module.CELERY_RESULT_BACKEND == "redis://:default-pw@127.0.0.1:6379/1"


def test_unresolvable_redis_configuration_raises_actionable_error(monkeypatch):
    monkeypatch.setattr(settings, "redis_url", "")
    monkeypatch.setattr(settings, "redis_password", "")

    with pytest.raises(RuntimeError) as excinfo:
        _reimport_celery_app()

    message = str(excinfo.value)
    # Actionable, secret-free diagnostic: names the resolution order and the
    # concrete fix commands.
    assert "REDIS_URL" in message
    assert "REDIS_PASSWORD" in message
    assert "setup-dev.sh" in message
    assert "run-worker-dev.sh" in message


def test_api_publishing_chain_resolves_celery_app_through_settings_contract(
    monkeypatch,
):
    """Regression for the material-registration HTTP 500.

    The documented API start command (uvicorn app.main:app) exports nothing,
    so the old raw ``os.getenv("REDIS_PASSWORD")`` in celery_app.py was
    unreachable for the API process and the lazy publisher import in
    ``app.workers.publishing`` exploded on the first material registration.
    The publishing chain must now import the Celery app whose broker/result
    URLs come from the settings contract the API process actually shares.
    """
    monkeypatch.setattr(settings, "redis_url", "")
    monkeypatch.setattr(settings, "redis_password", "default-pw")
    monkeypatch.setattr(settings, "redis_host", "redis")
    monkeypatch.setattr(settings, "redis_port", 6379)

    module = _reimport_celery_app()

    from app.workers import publishing

    app_from_api_chain = publishing._celery_app()

    assert app_from_api_chain is module.celery_app
    assert app_from_api_chain.conf.broker_url == "redis://:default-pw@redis:6379/0"
    assert app_from_api_chain.conf.result_backend == "redis://:default-pw@redis:6379/1"
