"""Static guards for the authenticated local MinIO checks (RC-1).

The local dev MinIO container ships a default ``local`` alias with EMPTY
credentials. An unauthenticated ``mc ready local`` answers even then, while
every authenticated operation (``mc stat``/``ls``/``rm``) is denied — so the
old scripts reported "MinIO is not ready or the materials bucket is missing"
even though MinIO was up and the bucket existed, and the smoke test's cleanup
could not verify deletions.

These are file-content assertions, not behavior tests: they pin the shape of
the fix so a refactor cannot silently reintroduce the raw, unauthenticated
``docker exec … mc <auth-op>`` calls. Runtime behavior (that the helper really
authenticates after a container recreation) is exercised by the setup/verifier
runs, not here. If you intentionally change how the checks authenticate, update
these assertions together with the three scripts.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

_SCRIPTS = (
    REPO_ROOT / "scripts" / "setup-dev.sh",
    REPO_ROOT / "scripts" / "verify-local-environment.sh",
    REPO_ROOT / "scripts" / "run-material-smoke-test.sh",
)
_DEV_COMPOSE = REPO_ROOT / "infra" / "docker-compose.dev.yml"

# Authenticated operations that MUST go through the credential-establishing
# helper — a raw `docker exec … mc stat|ls|rm` would silently use the image's
# empty default alias again.
_RAW_AUTH_OP = re.compile(r"exec\s+-T\s+minio\s+mc\s+(stat|ls|rm)\b")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_each_script_defines_the_authenticated_helper() -> None:
    for script in _SCRIPTS:
        text = _read(script)
        assert "minio_mc() {" in text, f"{script.name} must define minio_mc()"


def test_no_script_runs_authenticated_mc_without_the_helper() -> None:
    offenders = []
    for script in _SCRIPTS:
        for match in _RAW_AUTH_OP.finditer(_read(script)):
            offenders.append(f"{script.name}: raw '{match.group(0)}'")

    assert not offenders, (
        "authenticated mc operations must use the minio_mc helper "
        f"(re-establishes the alias from container credentials): {offenders}"
    )


def test_helper_derives_credentials_from_container_env_not_literals() -> None:
    for script in _SCRIPTS:
        text = _read(script)
        # The alias is rebuilt from the container's own runtime credentials …
        assert '"$MINIO_ROOT_USER"' in text
        assert '"$MINIO_ROOT_PASSWORD"' in text
        # … and no literal secret/assignment sneaks into the scripts.
        assert "MINIO_ROOT_PASSWORD=" not in text


def test_dev_compose_healthcheck_is_authenticated() -> None:
    text = _read(_DEV_COMPOSE)
    # The old unauthenticated check must be gone …
    assert '["CMD", "mc", "ready", "local"]' not in text
    # … replaced by an authenticated bucket listing from the container env.
    assert "mc ls local/" in text
    assert "$$MINIO_ROOT_USER" in text and "$$MINIO_ROOT_PASSWORD" in text


def test_setup_failure_message_is_no_longer_misleading() -> None:
    setup = _read(REPO_ROOT / "scripts" / "setup-dev.sh")
    assert "MinIO is not ready or the materials bucket is missing" not in setup
    # The three failure modes are distinguished explicitly.
    assert "authenticated requests are DENIED" in setup
    assert "does not exist" in setup
