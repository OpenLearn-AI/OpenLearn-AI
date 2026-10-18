#!/usr/bin/env bash
# ============================================================================
# run-worker-dev.sh — start the local material-processing Celery worker
#
# OpenLearn-AI — frontend-redesign — local environment batch.
#
# This is the local counterpart of the staging worker service
# (infra/docker-compose.staging.yml `celery_worker`), adapted to the local
# topology where the API and the worker run as host processes from
# backend/.venv:
#
#   staging:  celery -A app.workers.celery_app worker --loglevel=info -E \
#                 -Q celery,ingestion_queue
#             (inside the backend image, on the compose network, where the
#              hardcoded "redis" hostname resolves)
#
#   local:    the SAME command, run from backend/ with the venv interpreter,
#             with REDIS_URL exported so the broker points at the Redis
#             published by infra/docker-compose.dev.yml on 127.0.0.1:6379
#             (the host cannot resolve the container-network "redis" name;
#              app/workers/celery_app.py honors the REDIS_URL override and
#              keeps the staging default when it is unset).
#
# What it reads (never printed):
#   .env.local     REDIS_PASSWORD (required), REDIS_URL (optional override)
#   backend/.env   DATABASE_URL, S3_*, AI_* (read by app.config via pydantic
#                  settings, exactly as the API process reads them)
#
# Prerequisites:
#   * scripts/setup-dev.sh has been run at least once (backend/.venv exists)
#   * the compose services db + redis (+ minio for processing) are up
#
# The worker consumes BOTH queues staging routes to it: the default `celery`
# queue and the dedicated `ingestion_queue` where
# app.workers.tasks.material_tasks.process_material is delivered. A worker
# that listens only on the default queue silently loses material tasks.
#
# First-run note: with the default local provider block (AI_EMBEDDING_PROVIDER
# =bge-m3) the FIRST processed material downloads the BAAI/bge-m3 model
# (~2 GB) from HuggingFace into the local HuggingFace cache; later runs reuse
# it. See backend/.env.example for what each provider setting exercises.
#
# Usage:
#   bash scripts/run-worker-dev.sh
#   bash scripts/run-worker-dev.sh --once-check   # print resolved config and exit
#                                                 # (secret values shown as <set>)
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

ONCE_CHECK=0
for arg in "$@"; do
  case "$arg" in
    --once-check) ONCE_CHECK=1 ;;
    *) echo "unknown option: $arg" >&2; exit 64 ;;
  esac
done

# --- locate the environment files -------------------------------------------
if [ ! -f "${REPO_ROOT}/.env.local" ]; then
  echo "ERROR: ${REPO_ROOT}/.env.local not found — run scripts/setup-dev.sh first." >&2
  exit 66
fi
if [ ! -f "${REPO_ROOT}/backend/.env" ]; then
  echo "ERROR: ${REPO_ROOT}/backend/.env not found — run scripts/setup-dev.sh first." >&2
  exit 66
fi

# --- venv --------------------------------------------------------------------
if [ -x "${REPO_ROOT}/backend/.venv/bin/celery" ]; then
  CELERY_BIN="${REPO_ROOT}/backend/.venv/bin/celery"
elif [ -x "${REPO_ROOT}/backend/.venv/Scripts/celery.exe" ]; then
  CELERY_BIN="${REPO_ROOT}/backend/.venv/Scripts/celery.exe"
else
  echo "ERROR: backend/.venv has no celery executable — run scripts/setup-dev.sh first." >&2
  exit 66
fi

# --- worker environment ------------------------------------------------------
env_var_value() {
  sed -n "s/^${1}=//p" "$2" | head -1 | tr -d '\r'
}

REDIS_PASSWORD="$(env_var_value REDIS_PASSWORD "${REPO_ROOT}/.env.local")"
if [ -z "${REDIS_PASSWORD}" ]; then
  echo "ERROR: REDIS_PASSWORD not set in .env.local — run scripts/setup-dev.sh." >&2
  exit 66
fi
export REDIS_PASSWORD

# REDIS_URL: honor an explicit .env.local override; otherwise default to the
# published loopback port of the dev compose Redis service.
REDIS_URL_FROM_ENV_FILE="$(env_var_value REDIS_URL "${REPO_ROOT}/.env.local")"
if [ -n "${REDIS_URL_FROM_ENV_FILE}" ]; then
  export REDIS_URL="${REDIS_URL_FROM_ENV_FILE}"
else
  export REDIS_URL="redis://:${REDIS_PASSWORD}@127.0.0.1:6379"
fi

# --- resolved-config printout (secrets masked) -------------------------------
if [ "${ONCE_CHECK}" = "1" ]; then
  echo "worker binary : ${CELERY_BIN}"
  echo "working dir   : ${REPO_ROOT}/backend"
  echo "queues        : celery,ingestion_queue (staging parity)"
  echo "REDIS_URL     : ${REDIS_URL//:${REDIS_PASSWORD}@/:<set>@}"
  echo "REDIS_PASSWORD: <set>"
  echo "AI providers  : $(env_var_value AI_OCR_PROVIDER "${REPO_ROOT}/backend/.env" || echo '<unset: config default mock>') ocr | $(env_var_value AI_EMBEDDING_PROVIDER "${REPO_ROOT}/backend/.env" || echo '<unset: config default mock>') embeddings | $(env_var_value AI_VECTOR_DB_PROVIDER "${REPO_ROOT}/backend/.env" || echo '<unset: config default mock>') vectors"
  exit 0
fi

# --- exec the worker (staging command, local topology) -----------------------
cd "${REPO_ROOT}/backend"
exec "${CELERY_BIN}" -A app.workers.celery_app worker --loglevel=info -E -Q celery,ingestion_queue
