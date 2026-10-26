"""Static deployment-path guards for the Gemini AI configuration.

These are file-content assertions, not behavior tests: they pin the tracked
deployment artifacts to the B6-PREP-GEMINI decisions — the deployed reasoning
path routes to Gemini through the LiteLLM gateway with no OpenAI upstream and
no ``OPENAI_API_KEY`` requirement, the gateway alias stays identical to the
application's configured reasoning model, and the gateway's budget/auth
settings survive refactors — and to the B8 OCR remediation decision: the
worker's direct-Gemini ``AI_OCR_MODEL`` stays identical to the application's
``ai_ocr_model`` default. Runtime behavior (routing, budget enforcement, OCR
quality) is NOT asserted here — that belongs to the staging verification
batches. If you intentionally change the routing or a model, update these
assertions together with ``infra/``, the deploy workflow, and the ledger.
"""

from __future__ import annotations

import re
from pathlib import Path

from app.config import Settings

# This file lives at <repo>/backend/tests/test_ai_deployment_path.py, so the
# repository root is two parents up — independent of the pytest working dir.
REPO_ROOT = Path(__file__).resolve().parents[2]

_GATEWAY_CONFIG = REPO_ROOT / "infra" / "litellm-config.yaml"
_COMPOSE = REPO_ROOT / "infra" / "docker-compose.staging.yml"
_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "deploy-staging.yml"
_ENV_EXAMPLE = REPO_ROOT / "infra" / ".env.staging.example"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_gateway_config_has_no_openai_upstream() -> None:
    text = _read(_GATEWAY_CONFIG)

    assert "openai/" not in text  # no OpenAI-prefixed model upstream
    assert "OPENAI_API_KEY" not in text  # the deployment needs no OpenAI key
    # The single reasoning upstream is Gemini via the AI Studio integration,
    # keyed by the container's GEMINI_API_KEY.
    assert 'model_name: "gemini-3.6-flash"' in text
    assert 'model: "gemini/gemini-3.6-flash"' in text
    assert 'api_key: "os.environ/GEMINI_API_KEY"' in text


def test_gateway_config_preserves_budget_and_auth_settings() -> None:
    text = _read(_GATEWAY_CONFIG)

    assert 'master_key: "os.environ/LITELLM_MASTER_KEY"' in text
    assert "max_budget: 10.0" in text
    assert 'budget_duration: "30d"' in text
    assert "drop_params: true" in text
    assert 'success_callback: ["langfuse"]' in text
    assert 'default_model: "gemini-3.6-flash"' in text


def test_gateway_alias_matches_application_default() -> None:
    config_text = _read(_GATEWAY_CONFIG)
    compose_text = _read(_COMPOSE)

    # The application default is read from the Settings class (not the
    # instance) so this assertion cannot be perturbed by environment
    # variables in the test sandbox or CI.
    app_default = Settings.model_fields["ai_reasoning_model"].default
    assert app_default == "gemini-3.6-flash"
    assert 'model_name: "gemini-3.6-flash"' in config_text

    # The worker env must send the same alias as its chat-completion model.
    match = re.search(r"^\s*AI_REASONING_MODEL:\s*(\S+)\s*$", compose_text, re.M)
    assert match is not None, "AI_REASONING_MODEL missing from celery_worker env"
    assert match.group(1) == app_default


def test_worker_ocr_model_matches_application_default() -> None:
    compose_text = _read(_COMPOSE)

    # The OCR model is direct-Gemini (google-genai in the worker; the LiteLLM
    # gateway is not in the OCR path), so unlike the reasoning alias there is
    # no gateway entry to match — but the worker's env override must still
    # equal the application default so staging and the code default cannot
    # drift apart. B8's staging run (b8v1791396817) exposed exactly this
    # drift class: a stale gemini-2.5-flash OCR model survived B6's
    # reasoning-model migration because nothing pinned the OCR pair.
    app_default = Settings.model_fields["ai_ocr_model"].default
    assert app_default == "gemini-3.6-flash"

    match = re.search(r"^\s*AI_OCR_MODEL:\s*(\S+)\s*$", compose_text, re.M)
    assert match is not None, "AI_OCR_MODEL missing from celery_worker env"
    assert match.group(1) == app_default


def test_compose_wires_gemini_to_gateway_and_worker_without_openai() -> None:
    text = _read(_COMPOSE)

    assert "OPENAI_API_KEY" not in text
    # Worker: gateway access + direct OCR key (mapping-style env entries).
    assert "LITELLM_API_BASE: http://litellm:4000" in text
    assert "LITELLM_API_KEY: ${LITELLM_API_KEY}" in text
    assert "AI_REASONING_PROVIDER: litellm" in text
    assert "GEMINI_API_KEY: ${GEMINI_API_KEY}" in text
    # Gateway container receives the same Gemini key for its upstream.
    assert "- GEMINI_API_KEY=${GEMINI_API_KEY}" in text


def test_workflow_requires_gemini_and_not_openai() -> None:
    text = _read(_WORKFLOW)

    assert "OPENAI_API_KEY" not in text
    assert "GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }}" in text
    assert "LITELLM_API_KEY=${{ secrets.LITELLM_API_KEY }}" in text
    # The fail-loud guard covers exactly the AI runtime secrets.
    assert "for required_var in LITELLM_API_KEY GEMINI_API_KEY" in text


def test_env_example_documents_gemini_roles_without_openai() -> None:
    text = _read(_ENV_EXAMPLE)

    assert "OPENAI_API_KEY" not in text
    assert "GEMINI_API_KEY=" in text
