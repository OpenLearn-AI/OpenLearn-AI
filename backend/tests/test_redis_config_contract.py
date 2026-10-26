"""Regression tests for the Redis configuration-loading contract.

Root cause under test: ``app.workers.celery_app`` used to read
``REDIS_PASSWORD`` via raw ``os.getenv`` — a mechanism the documented API
startup command (``uvicorn app.main:app``) never satisfies, because the
process environment of a plain uvicorn shell contains no such variable. The
first material registration then failed with HTTP 500 from the import-time
``RuntimeError`` inside the lazy publisher import.

The contract now centralizes Redis resolution in ``app.config.Settings``,
which reads, in order of increasing precedence:

    repository-root .env.local  <  backend/.env  <  process environment

(the LATER file in ``env_file`` wins for shared keys — verified empirically
against pydantic-settings==2.15.0). These tests pin that contract with
temporary env files and direct ``Settings(_env_file=...)`` instantiation, plus
the URL-composition and fail-fast behavior. No real Redis service and no
developer-local configuration are involved: every test isolates the process
environment and uses ``tmp_path`` files.
"""

import pytest
from pydantic_settings import SettingsConfigDict

from app.config import Settings

REDIS_ENV_VARS = ("REDIS_URL", "REDIS_PASSWORD", "REDIS_HOST", "REDIS_PORT")


@pytest.fixture(autouse=True)
def isolated_redis_environment(monkeypatch):
    """Keep every test independent of the developer's real environment."""
    for var in REDIS_ENV_VARS:
        monkeypatch.delenv(var, raising=False)


def _make_settings_class(env_files):
    class ContractSettings(Settings):
        model_config = SettingsConfigDict(
            env_file=env_files,
            env_file_encoding="utf-8",
            extra="ignore",
        )

    return ContractSettings


def test_env_local_fills_gap_when_backend_env_lacks_redis(tmp_path):
    """The load-bearing regression: REDIS_PASSWORD lives only in .env.local."""
    env_local = tmp_path / ".env.local"
    env_local.write_text("REDIS_PASSWORD=generated-password\n")
    backend_env = tmp_path / "backend.env"
    backend_env.write_text("KEYCLOAK_AUDIENCE=openlearn-api\n")

    cls = _make_settings_class((env_local, backend_env))
    cfg = cls()

    assert cfg.redis_password == "generated-password"
    assert cfg.keycloak_audience == "openlearn-api"
    # Composition still happens with the staging-default host.
    assert cfg.redis_connection_url == "redis://:generated-password@redis:6379"


def test_backend_env_shadows_env_local_for_shared_keys(tmp_path):
    """backend/.env is the later file and stays authoritative for shared keys."""
    env_local = tmp_path / ".env.local"
    env_local.write_text("REDIS_PASSWORD=generated-password\nREDIS_HOST=from-env-local\n")
    backend_env = tmp_path / "backend.env"
    backend_env.write_text("REDIS_HOST=from-backend-env\n")

    cls = _make_settings_class((env_local, backend_env))
    cfg = cls()

    assert cfg.redis_password == "generated-password"
    assert cfg.redis_host == "from-backend-env"
    assert cfg.redis_connection_url == "redis://:generated-password@from-backend-env:6379"


def test_process_environment_beats_both_env_files(tmp_path, monkeypatch):
    env_local = tmp_path / ".env.local"
    env_local.write_text("REDIS_PASSWORD=from-env-local\n")
    backend_env = tmp_path / "backend.env"
    backend_env.write_text("REDIS_PASSWORD=from-backend-env\n")
    monkeypatch.setenv("REDIS_PASSWORD", "from-process-env")

    cls = _make_settings_class((env_local, backend_env))
    cfg = cls()

    assert cfg.redis_password == "from-process-env"


def test_missing_env_local_file_is_tolerated(tmp_path):
    """Fresh clones and staging (no .env.local) must not crash at import."""
    backend_env = tmp_path / "backend.env"
    backend_env.write_text("REDIS_PASSWORD=from-backend-env\n")

    cls = _make_settings_class((tmp_path / "does-not-exist.local", backend_env))
    cfg = cls()

    assert cfg.redis_password == "from-backend-env"


def test_redis_connection_url_composes_from_parts():
    cfg = Settings(
        redis_url="",
        redis_password="s3cret-pw",
        redis_host="redis",
        redis_port=6379,
    )

    assert cfg.redis_connection_url == "redis://:s3cret-pw@redis:6379"


def test_redis_url_override_wins_outright_without_password():
    """An explicit full URL embeds its own credentials; no password required."""
    cfg = Settings(
        redis_url="redis://:override-pw@127.0.0.1:6379",
        redis_password="",
    )

    assert cfg.redis_connection_url == "redis://:override-pw@127.0.0.1:6379"


def test_unresolvable_configuration_raises_actionable_secret_free_error():
    cfg = Settings(redis_url="", redis_password="")

    with pytest.raises(RuntimeError) as excinfo:
        _ = cfg.redis_connection_url

    message = str(excinfo.value)
    assert "REDIS_URL" in message
    assert "REDIS_PASSWORD" in message
    assert "setup-dev.sh" in message
    assert "run-worker-dev.sh" in message
    # The diagnostic must never carry a credential value.
    assert "s3cret-pw" not in message
