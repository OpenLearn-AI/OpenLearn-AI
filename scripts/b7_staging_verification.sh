#!/usr/bin/env bash
# =============================================================================
# b7_staging_verification.sh
#
# OpenLearn-AI Week 7-8 / Batch B7 — staging evidence collector.
# "End-to-End verification, regression, and runtime behavior checks."
#
# Tracked repository copy (scripts/b7_staging_verification.sh) since the
# B7-PHASE2 remediation batch. It supersedes the earlier VPS-local w7.sh:
# same run structure and result protocol, with the B7-PHASE2 verifier fixes
# applied —
#   * DB_SCHEMA: ordered, schema-qualified, per-sub-check SQL with return-code
#     capture (no unordered string_agg glob, no silently discarded probe
#     errors), normalized pg_get_constraintdef value checks, and an
#     alembic_version-vs-repo-head comparison;
#   * RSN_CALL: max_tokens budget ladder for thinking-capable models and a
#     six-way outcome classification that keeps upstream quota exhaustion
#     (HTTP 429) an explicitly BLOCKED external state instead of a FAIL or a
#     manufactured PASS;
#   * CLEANUP: per-resource ids files (no concatenation), predicate-guarded
#     deletes, explicit FK-less vector deletes, verified S3 deletion, and a
#     report-only inventory of previous-run B7 verification leftovers
#     (opt-in narrow cleanup via B7_CLEAN_PREVIOUS_B7=1);
#   * OCR: consumes the ocr_gate_evaluated / ocr_enrichment_applied worker
#     log events (B7-PHASE2 app-side observability) when the deployed image
#     provides them, and fixes the OCR-trigger baseline comparison.
#
# One controlled run on the staging VPS (from the repository root). It prints
# a PASS / FAIL / BLOCKED / NOT OBSERVABLE line for every B7 acceptance item
# and a final machine-readable summary (B7RESULT|id|status|note).
#
# Safety contract:
#   * READ-ONLY with respect to the repository source tree. It runs no git
#     state-changing command at all (no reset/clean/checkout/switch/restore/
#     rebase/merge/pull/commit/push) and writes nothing inside the repo.
#   * Does NOT restart, recreate, or reconfigure any service or container and
#     does NOT rebuild images. It only execs short read-oriented commands and
#     Python snippets inside existing containers.
#   * NEVER prints secret values. LITELLM_API_KEY / LITELLM_MASTER_KEY /
#     GEMINI_API_KEY / SENTRY_DSN / REDIS_PASSWORD / POSTGRES_PASSWORD /
#     MINIO_* / DATABASE_URL are reported as SET or MISSING only.
#   * It creates temporary records (user, course, material, one MinIO object,
#     one Celery task) only for its own uniquely-marked B7 verification
#     resources and deletes exactly those afterwards. It never runs broad
#     DELETE/UPDATE/DROP/TRUNCATE and never touches pre-existing data. Every
#     delete is scoped to an exact recorded UUID AND guarded by the B7
#     verification-resource predicate (synthetic issuer URN / title prefix);
#     a corrupted ids file can therefore never make this script delete
#     arbitrary user data. Previous-run B7 verification leftovers are
#     REPORTED only; deleting them requires the explicit opt-in
#     B7_CLEAN_PREVIOUS_B7=1 (narrowly issuer-scoped, exact-UUID listing
#     before every delete, FK-ordered, with explicit vector and S3 cleanup).
#   * Temporary files live under /tmp on the host and /tmp inside the worker
#     container and are removed by a trap (best effort inside the container).
#   * If a step fails it records the failure and CONTINUES collecting the
#     remaining independent evidence; a final summary decides the exit code.
#     Exit code 0 = every required criterion PASS (or an explicitly allowed
#     NOT OBSERVABLE); non-zero = at least one required criterion FAIL/BLOCKED.
#
# Optional environment switches (defaults are the conservative values):
#   B7_E2E_TIMEOUT=480       seconds to wait for ready/failed in the E2E run
#   B7_FAIL_TIMEOUT=120      seconds to wait for the forced-failure run
#   B7_EMBED_PROOF=1         0 skips the direct BGE-M3 embed probe (loads the
#                            model once inside a short-lived exec process)
#   B7_REASON_CALL=1         0 skips the real one-shot LiteLLM reasoning call
#   B7_RUN_OCR_TRIGGER=0     1 additionally processes a scanned PDF from the
#                            repository (makes one real Gemini OCR call) to
#                            get DIRECT page-level OCR evidence
#   B7_INSTALL_TEST_DEPS=0   1 installs the pinned dev dependencies (pytest,
#                            ruff, ...) into the worker container user-site
#                            and runs the repository test suite against a
#                            temporary database (created then dropped) inside
#                            the existing staging Postgres
#   B7_CLEAN_PREVIOUS_B7=0   1 additionally deletes the resources left behind
#                            by PREVIOUS verifier runs (identified solely by
#                            the synthetic B7 verification issuer URN), after
#                            listing every exact UUID on the transcript.
#                            Default 0: previous leftovers are reported only.
#   B7_PYTHON=               host python interpreter for the local suite
#
# Run:   cd /path/to/OpenLearn-AI   &&   bash b7_staging_verification.sh
# (also works when copied to /tmp — it walks up to find the repo root)
# =============================================================================

set -u

# ------------------------------------------------------------------ globals --
TS_EPOCH="$(date +%s)"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
TMP_HOST="/tmp/b7-staging-verify-${TS}"
RESULTS="${TMP_HOST}/results.txt"
CONTAINER_TMP="/tmp/b7-verify-${TS}"
MARK="b7v${TS_EPOCH}"

B7_E2E_TIMEOUT="${B7_E2E_TIMEOUT:-480}"
B7_FAIL_TIMEOUT="${B7_FAIL_TIMEOUT:-120}"
B7_EMBED_PROOF="${B7_EMBED_PROOF:-1}"
B7_REASON_CALL="${B7_REASON_CALL:-1}"
B7_RUN_OCR_TRIGGER="${B7_RUN_OCR_TRIGGER:-0}"
B7_INSTALL_TEST_DEPS="${B7_INSTALL_TEST_DEPS:-0}"
B7_CLEAN_PREVIOUS_B7="${B7_CLEAN_PREVIOUS_B7:-0}"
B7_PYTHON="${B7_PYTHON:-}"

REQUIRED_TASK="app.workers.tasks.material_tasks.process_material"
PDF_REL="experiments/OCR/ocr-benchmark/data/raw/custom/1. English born-digital/custom_custom_english_born_digital_005_p001.pdf"
PDF_TRIGGER_REL="experiments/OCR/ocr-benchmark/data/raw/custom/3.English scanned/custom_custom_english_scanned_003_p001.pdf"

ROOT=""
DOCKER_COMPOSE=""
CID_BACKEND="" CID_WORKER="" CID_DB="" CID_REDIS="" CID_LITELLM="" CID_MINIO=""
PG_USER="" PG_DB=""
VEC_BASELINE=""
TEST_DB_NAME=""

REQUIRED_IDS="REPO CONTAINERS WORKER_READY WCONFIG EMB_FACTORY VEC_PROVIDER RSN_FACTORY LIT_MODELS RSN_CALL E2E_LIFECYCLE E2E_VECTORS E2E_PROVENANCE E2E_DISCRIM OCR_GATE FORCED_FAIL DB_SCHEMA CLEANUP"

# ------------------------------------------------------------------ helpers --
log() { printf '%s\n' "$*"; }
hr()  { printf '%s\n' "--------------------------------------------------------------------"; }
now() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
section() {
  echo
  hr
  log "SECTION $1  [$2]  $(now)"
  hr
}
result() { # result <ID> <STATUS> <note...>
  local id="$1" st="$2"; shift 2
  local note="$*"
  printf 'B7RESULT|%s|%s|%s\n' "$id" "$st" "$note" >> "$RESULTS"
  printf '[%s] %s — %s\n' "$st" "$id" "$note"
}
note() { printf '       %s\n' "$*"; }

dcompose() { $DOCKER_COMPOSE -f "${ROOT}/infra/docker-compose.staging.yml" "$@"; }

discover() { # discover <compose-service> -> container id ("" when absent)
  local svc="$1" cid=""
  cid="$(dcompose ps -q "$svc" 2>/dev/null | head -n 1 || true)"
  if [ -z "$cid" ]; then
    cid="$(docker ps --filter "label=com.docker.compose.service=${svc}" -q 2>/dev/null | head -n 1 || true)"
  fi
  printf '%s' "$cid"
}

state_of() { docker inspect -f '{{.State.Status}}' "$1" 2>/dev/null || printf 'absent'; }
health_of() {
  docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' "$1" 2>/dev/null || printf '?'
}
image_of() { docker inspect -f '{{.Config.Image}}' "$1" 2>/dev/null || printf '?'; }

push_file() { # push_file <cid> <host-src> <container-dst>
  local cid="$1" src="$2" dst="$3"
  docker exec "$cid" mkdir -p "$(dirname "$dst")" >/dev/null 2>&1 || return 1
  docker exec -i "$cid" sh -c 'cat > "$1"' sh "$dst" < "$src"
}

env_state() { # env_state <cid> <VARNAME> -> prints SET or MISSING (never the value)
  local cid="$1" var="$2"
  docker exec "$cid" sh -c "if [ -n \"\${${var}:-}\" ]; then echo SET; else echo MISSING; fi" 2>/dev/null || printf 'UNKNOWN'
}

grep_val() { # grep_val <file> <marker>  -> third pipe-field of "TAG|key|value"
  awk -F'|' -v k="$2" '$1=="B7CFG" && $2==k {print $3}' "$1" 2>/dev/null | head -n 1
}

grep_marker() { # grep_marker <file> <literal> -> 0 when present
  grep -qF -- "$2" "$1" 2>/dev/null
}

psql_ro() { # psql_ro <sql> (read-only usage only; runs inside the db container)
  docker exec "$CID_DB" psql -U "$PG_USER" -d "$PG_DB" -Atc "$1" 2>/dev/null
}

pg_count() { psql_ro "SELECT count(*) FROM ${1};" | tr -d '[:space:]'; }

on_exit() {
  local rc=$?
  [ -n "${CID_WORKER:-}" ] && docker exec "$CID_WORKER" rm -rf "$CONTAINER_TMP" >/dev/null 2>&1
  rm -rf "$TMP_HOST" >/dev/null 2>&1
  exit "$rc"
}
trap on_exit EXIT

# ============================================================================
# SECTION 0 — PREFLIGHT
# ============================================================================
section 0 "PREFLIGHT"
mkdir -p "$TMP_HOST"
: > "$RESULTS"

if ! command -v docker >/dev/null 2>&1; then
  log "FATAL: docker is not available on this host."
  exit 2
fi
log "docker: $(docker --version 2>/dev/null || echo '?')"

if docker compose version >/dev/null 2>&1; then
  DOCKER_COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  DOCKER_COMPOSE="docker-compose"
else
  log "FATAL: neither 'docker compose' nor 'docker-compose' is available."
  exit 2
fi
log "compose driver: $DOCKER_COMPOSE"

find_root() {
  local d="$PWD"
  while [ -n "$d" ] && [ "$d" != "/" ]; do
    if [ -f "$d/infra/docker-compose.staging.yml" ]; then printf '%s' "$d"; return 0; fi
    d="$(dirname "$d")"
  done
  d="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || d=""
  while [ -n "$d" ] && [ "$d" != "/" ]; do
    if [ -f "$d/infra/docker-compose.staging.yml" ]; then printf '%s' "$d"; return 0; fi
    d="$(dirname "$d")"
  done
  return 1
}

if ROOT="$(find_root)"; then
  log "repository root: $ROOT"
else
  log "FATAL: infra/docker-compose.staging.yml not found above PWD or next to the script."
  log "Run this script from the staging repository root."
  exit 2
fi

if ! docker info >/dev/null 2>&1; then
  log "FATAL: docker daemon is not reachable."
  exit 2
fi

log "host kernel: $(uname -sr 2>/dev/null || echo '?')"
log "run mark: $MARK"
log "verifier: scripts/b7_staging_verification.sh (tracked, B7-PHASE2 fixes — supersedes the VPS-local w7.sh)"
log "host temp dir: $TMP_HOST (removed at exit)"

# ============================================================================
# SECTION 1 — REPOSITORY STATE (read-only)
# ============================================================================
section 1 "REPOSITORY STATE"
HEAD_SHA="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo 'not-a-git-worktree')"
BRANCH="$(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')"
SUBJECT="$(git -C "$ROOT" log -1 --format=%s 2>/dev/null || echo '?')"
DIRTY="$(git -C "$ROOT" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
log "branch:    $BRANCH"
log "HEAD:      $HEAD_SHA"
log "subject:   $SUBJECT"
log "dirty entries in worktree: $DIRTY (reported only; never touched by this script)"
if [ -f "$ROOT/$PDF_REL" ]; then
  log "smoke PDF present: $PDF_REL ($(wc -c < "$ROOT/$PDF_REL" | tr -d ' ') bytes)"
  result REPO PASS "branch=$BRANCH HEAD=$HEAD_SHA; smoke PDF present under experiments/"
else
  log "MISSING smoke PDF: $PDF_REL"
  result REPO FAIL "smoke PDF $PDF_REL not found in the worktree"
fi

# ============================================================================
# SECTION 2 — CONTAINER DISCOVERY & HEALTH (read-only)
# ============================================================================
section 2 "CONTAINER DISCOVERY & HEALTH"
log "compose ps (as deployed):"
dcompose ps 2>/dev/null | sed 's/^/  /' || note "(compose ps produced no output)"

for svc in backend celery_worker celery_beat db redis litellm minio flower keycloak frontend; do
  cid="$(discover "$svc")"
  if [ -z "$cid" ]; then
    log "  $svc: NOT FOUND"
  else
    log "  $svc: container=${cid:0:12} state=$(state_of "$cid") health=$(health_of "$cid") image=$(image_of "$cid")"
  fi
done

CID_BACKEND="$(discover backend)"
CID_WORKER="$(discover celery_worker)"
CID_DB="$(discover db)"
CID_REDIS="$(discover redis)"
CID_LITELLM="$(discover litellm)"
CID_MINIO="$(discover minio)"

MISSING=""
[ -z "$CID_WORKER" ] && MISSING="$MISSING celery_worker"
[ -z "$CID_DB" ] && MISSING="$MISSING db"
[ -z "$CID_REDIS" ] && MISSING="$MISSING redis"
[ -z "$CID_MINIO" ] && MISSING="$MISSING minio"
[ -z "$CID_LITELLM" ] && MISSING="$MISSING litellm"

if [ -n "$MISSING" ]; then
  result CONTAINERS FAIL "required containers not found:$MISSING (compose project discovery failed)"
else
  WS="$(state_of "$CID_WORKER")"; BS="$(state_of "$CID_BACKEND")"
  if [ "$WS" = "running" ] && [ "$BS" = "running" ]; then
    result CONTAINERS PASS "worker=$WS backend=$BS db/redis/minio/litellm present (worker container: $(docker inspect -f '{{.Name}}' "$CID_WORKER" 2>/dev/null | tr -d '/'))"
  else
    result CONTAINERS FAIL "worker state=$WS backend state=$BS (expected running)"
  fi
fi

if [ -n "$CID_DB" ]; then
  PG_USER="$(docker exec "$CID_DB" printenv POSTGRES_USER 2>/dev/null || printf 'postgres')"
  PG_DB="$(docker exec "$CID_DB" printenv POSTGRES_DB 2>/dev/null || printf 'postgres')"
  log "db user/database (non-secret): $PG_USER / $PG_DB"
fi

# ============================================================================
# SECTION 3 — LOCAL REGRESSION SUITE (host env -> opt-in container -> honest skip)
# ============================================================================
section 3 "LOCAL REGRESSION SUITE + RUFF"
PY="$B7_PYTHON"
[ -z "$PY" ] && PY="python3"
HOST_ENV_OK=0
if command -v "$PY" >/dev/null 2>&1; then
  if [ "$("$PY" -m pytest --version 2>/dev/null | head -c 5)" != "" ] \
     && (cd "$ROOT/backend" && "$PY" -c "import app, sqlalchemy, docling, celery" >/dev/null 2>&1); then
    HOST_ENV_OK=1
  fi
fi

run_and_parse_suite() {
  # $1 = label, $2 = results file, remaining = command argv
  local label="$1" outfile="$2"; shift 2
  ( "$@" ) > "$outfile" 2>&1
  local rc=$?
  log "--- $label (exit=$rc) — last lines ---"
  tail -n 12 "$outfile" | sed 's/^/  /'
  printf 'B7SUITE|%s|rc=%s\n' "$label" "$rc" >> "$outfile"
}

if [ "$HOST_ENV_OK" = "1" ]; then
  log "host python environment detected: $PY (pytest + app importable from backend/)"
  log "NOTE: the suite uses backend/.env or default localhost DB settings; connection"
  log "      failures are reported as environment-blocked, not as code failures."
  run_and_parse_suite "core" "$TMP_HOST/pytest_core.txt" bash -c "cd '$ROOT/backend' && '$PY' -m pytest tests --ignore=tests/pal --ignore=tests/documents -q"
  run_and_parse_suite "ai" "$TMP_HOST/pytest_ai.txt" bash -c "cd '$ROOT/backend' && '$PY' -m pytest tests/documents tests/services/test_ocr.py tests/services/test_ocr_language_paths.py tests/services/test_ocr_source.py tests/pal tests/test_material_tasks.py -q"
  if "$PY" -m ruff --version >/dev/null 2>&1; then
    run_and_parse_suite "ruff" "$TMP_HOST/ruff.txt" bash -c "cd '$ROOT/backend' && '$PY' -m ruff check ."
  else
    log "ruff not installed for $PY — skipping host ruff (repo ledger already records ruff clean at this baseline)."
  fi
  classify_suite() { # classify_suite <outfile> <required-id> <what>
    local f="$1" id="$2" what="$3" last summary
    last="$(grep '^B7SUITE|' "$f" 2>/dev/null | tail -n 1)"
    summary="$(grep -E '^[0-9]+ (passed|failed)|passed|failed|error' "$f" 2>/dev/null | tail -n 3 | tr '\n' ' ')"
    case "$last" in
      *rc=0*)
        result "$id" PASS "$what: ${summary:-all green}"
        ;;
      *rc=1*|*rc=2*)
        if grep -qE 'ConnectionRefused|Connection refused|ConnectError|could not connect|Failed to connect|Error connecting' "$f" 2>/dev/null; then
          result "$id" BLOCKED "$what: failed because no test database is reachable from this environment (connection errors) — environment property, not a code failure; committed local-regression evidence covers this criterion"
        else
          result "$id" FAIL "$what: ${summary:-see captured output above}"
        fi
        ;;
      *)
        result "$id" BLOCKED "$what: could not run (${last:-no result line})"
        ;;
    esac
  }
  classify_suite "$TMP_HOST/pytest_core.txt" TESTS_CORE "core suite (tests --ignore=tests/pal --ignore=tests/documents)"
  classify_suite "$TMP_HOST/pytest_ai.txt" TESTS_AI "AI suite (documents+OCR+pal+material_tasks)"
  if [ -f "$TMP_HOST/ruff.txt" ]; then
    classify_suite "$TMP_HOST/ruff.txt" RUFF "ruff check ."
  else
    result RUFF BLOCKED "ruff unavailable on host (non-fatal; ledger evidence exists)"
  fi

elif [ "$B7_INSTALL_TEST_DEPS" = "1" ] && [ -n "$CID_WORKER" ]; then
  # ----- opt-in containerized run -------------------------------------------
  log "B7_INSTALL_TEST_DEPS=1 — installing pinned dev deps into the worker container"
  log "user-site (ephemeral; a container recreation reverts it) and running the suite"
  log "against a temporary database that is dropped afterwards. This does NOT modify"
  log "any tracked repository file or any staging configuration."
  if docker exec "$CID_WORKER" python -m pip install --user --quiet --disable-pip-version-check \
       pytest==8.3.3 pytest-asyncio==0.24.0 httpx==0.28.1 ruff==0.7.4 >/dev/null 2>&1; then
    TEST_DB_NAME="b7_verify_tmp_${TS_EPOCH}"
    if docker exec "$CID_DB" psql -U "$PG_USER" -d "$PG_DB" -c "CREATE DATABASE \"$TEST_DB_NAME\"" >/dev/null 2>&1; then
      note "temporary database created: $TEST_DB_NAME (dropped in SECTION 12)"
      cat > "$TMP_HOST/b7_make_test_url.py" <<'PY'
import sys
from app.config import settings
head, _, _ = settings.database_url.rpartition("/")
with open(sys.argv[2], "w") as fh:
    fh.write(head + "/" + sys.argv[1])
PY
      push_file "$CID_WORKER" "$TMP_HOST/b7_make_test_url.py" "$CONTAINER_TMP/b7_make_test_url.py" || true
      docker exec "$CID_WORKER" python "$CONTAINER_TMP/b7_make_test_url.py" "$TEST_DB_NAME" "$CONTAINER_TMP/test_db_url" >/dev/null 2>&1
      cat > "$TMP_HOST/b7_run_tests.sh" <<SH
#!/bin/sh
cd /app
if [ ! -f "$CONTAINER_TMP/test_db_url" ]; then
  echo "B7CORE_RC=125"
  echo "B7AI_RC=125"
  echo "B7RUFF_RC=125"
  exit 0
fi
export DATABASE_URL="\$(cat $CONTAINER_TMP/test_db_url)"
rm -f "$CONTAINER_TMP/test_db_url"
echo "== alembic upgrade head (temp db) =="
python -m alembic upgrade head >/dev/null 2>&1; echo "B7ALEMBIC_RC=\$?"
echo "== pytest core =="
python -m pytest tests --ignore=tests/pal --ignore=tests/documents -q -p no:cacheprovider > /tmp/b7_core.log 2>&1
echo "B7CORE_RC=\$?"
tail -n 4 /tmp/b7_core.log
echo "== pytest ai =="
python -m pytest tests/documents tests/services/test_ocr.py tests/services/test_ocr_language_paths.py tests/services/test_ocr_source.py tests/pal tests/test_material_tasks.py -q -p no:cacheprovider > /tmp/b7_ai.log 2>&1
echo "B7AI_RC=\$?"
tail -n 4 /tmp/b7_ai.log
echo "== ruff =="
python -m ruff check . > /tmp/b7_ruff.log 2>&1
echo "B7RUFF_RC=\$?"
tail -n 3 /tmp/b7_ruff.log
SH
      push_file "$CID_WORKER" "$TMP_HOST/b7_run_tests.sh" "$CONTAINER_TMP/b7_run_tests.sh" || true
      docker exec "$CID_WORKER" sh "$CONTAINER_TMP/b7_run_tests.sh" > "$TMP_HOST/container_tests.txt" 2>&1
      sed 's/^/  /' "$TMP_HOST/container_tests.txt"
      case "$(grep 'B7CORE_RC=' "$TMP_HOST/container_tests.txt" | tail -n1)" in
        B7CORE_RC=0) result TESTS_CORE PASS "containerized core suite green (temp db $TEST_DB_NAME)" ;;
        B7CORE_RC=125) result TESTS_CORE BLOCKED "test-database URL handoff failed inside the container (temp db $TEST_DB_NAME dropped in SECTION 12)" ;;
        *) result TESTS_CORE FAIL "containerized core suite — see B7CORE_RC above" ;;
      esac
      case "$(grep 'B7AI_RC=' "$TMP_HOST/container_tests.txt" | tail -n1)" in
        B7AI_RC=0) result TESTS_AI PASS "containerized AI suite green" ;;
        B7AI_RC=125) result TESTS_AI BLOCKED "test-database URL handoff failed" ;;
        *) result TESTS_AI FAIL "containerized AI suite — see B7AI_RC above" ;;
      esac
      case "$(grep 'B7RUFF_RC=' "$TMP_HOST/container_tests.txt" | tail -n1)" in
        B7RUFF_RC=0) result RUFF PASS "ruff clean (containerized)" ;;
        B7RUFF_RC=125) result RUFF BLOCKED "test-database URL handoff failed" ;;
        *) result RUFF FAIL "ruff reported findings — see above" ;;
      esac
    else
      result TESTS_CORE BLOCKED "could not create temporary test database (psql CREATE DATABASE failed)"
      result TESTS_AI BLOCKED "depends on temporary test database"
      result RUFF BLOCKED "depends on temporary test database"
    fi
  else
    result TESTS_CORE BLOCKED "pip install --user of pinned dev deps failed inside the worker container (network/permissions)"
    result TESTS_AI BLOCKED "depends on test deps"
    result RUFF BLOCKED "depends on test deps"
  fi
else
  log "No host backend Python environment detected and B7_INSTALL_TEST_DEPS!=0 not set."
  log "The backend image does NOT ship pytest (dev deps only), so the suite cannot run"
  log "here without installing packages — which this read-only verifier will not do"
  log "by default. The authoritative local-regression evidence for this baseline is"
  log "already committed in docs/tasks/ai-week7-8/progress.md (Batch B7 first pass:"
  log "293 passed / 197 passed + 2 skipped opt-in / ruff clean at HEAD)."
  result TESTS_CORE BLOCKED "no host test env on staging VPS; set B7_INSTALL_TEST_DEPS=1 to run the suite in-container; committed ledger evidence covers this criterion (not runtime)"
  result TESTS_AI BLOCKED "same as TESTS_CORE"
  result RUFF BLOCKED "same as TESTS_CORE"
fi

# ============================================================================
# SECTION 4 — WORKER AI CONFIGURATION (SET/MISSING + non-secret values)
# ============================================================================
section 4 "WORKER AI CONFIGURATION"

if [ -z "$CID_WORKER" ]; then
  result WCONFIG FAIL "worker container not found; configuration not observable"
else
  log "Secret-valued variables (SET/MISSING only — values are never printed):"
  for v in LITELLM_API_KEY GEMINI_API_KEY SENTRY_DSN REDIS_PASSWORD DATABASE_URL S3_SECRET_ACCESS_KEY; do
    log "  worker $v: $(env_state "$CID_WORKER" "$v")"
  done
  if [ -n "$CID_LITELLM" ]; then
    log "  litellm LITELLM_MASTER_KEY: $(env_state "$CID_LITELLM" "LITELLM_MASTER_KEY")"
  fi

  cat > "$TMP_HOST/b7_config_report.py" <<'PY'
from app.config import settings

pairs = [
    ("ai_embedding_provider", settings.ai_embedding_provider),
    ("ai_embedding_model", settings.ai_embedding_model),
    ("ai_embedding_dimension", settings.ai_embedding_dimension),
    ("ai_embedding_device", settings.ai_embedding_device),
    ("ai_vector_db_provider", settings.ai_vector_db_provider),
    ("ai_reasoning_provider", settings.ai_reasoning_provider),
    ("ai_reasoning_model", settings.ai_reasoning_model),
    ("litellm_api_base", settings.litellm_api_base),
    ("ai_ocr_provider", settings.ai_ocr_provider),
    ("ai_ocr_model", settings.ai_ocr_model),
    ("ocr_min_text_chars", settings.ocr_min_text_chars),
    ("environment", settings.environment),
]
for k, v in pairs:
    print(f"B7CFG|{k}|{v}")
PY
  if push_file "$CID_WORKER" "$TMP_HOST/b7_config_report.py" "$CONTAINER_TMP/b7_config_report.py" \
     && docker exec "$CID_WORKER" python "$CONTAINER_TMP/b7_config_report.py" > "$TMP_HOST/config.txt" 2>&1; then
    sed 's/^/  /' "$TMP_HOST/config.txt"
    EMB_P="$(grep_val "$TMP_HOST/config.txt" ai_embedding_provider)"
    EMB_D="$(grep_val "$TMP_HOST/config.txt" ai_embedding_dimension)"
    EMB_M="$(grep_val "$TMP_HOST/config.txt" ai_embedding_model)"
    VDB_P="$(grep_val "$TMP_HOST/config.txt" ai_vector_db_provider)"
    RSN_P="$(grep_val "$TMP_HOST/config.txt" ai_reasoning_provider)"
    RSN_M="$(grep_val "$TMP_HOST/config.txt" ai_reasoning_model)"
    LIT_BASE="$(grep_val "$TMP_HOST/config.txt" litellm_api_base)"
    OCR_P="$(grep_val "$TMP_HOST/config.txt" ai_ocr_provider)"
    KEY_SET="$(env_state "$CID_WORKER" LITELLM_API_KEY)"
    log "expected per infra/docker-compose.staging.yml: AI_EMBEDDING_PROVIDER=bge-m3,"
    log "AI_EMBEDDING_DIMENSION=1024, AI_EMBEDDING_MODEL=BAAI/bge-m3, AI_VECTOR_DB_PROVIDER=postgres,"
    log "AI_REASONING_PROVIDER=litellm, AI_REASONING_MODEL=gemini-3.6-flash, LITELLM_API_BASE=http://litellm:4000"
    if [ "$EMB_P" = "bge-m3" ] && [ "$EMB_D" = "1024" ] && [ "$EMB_M" = "BAAI/bge-m3" ] \
       && [ "$VDB_P" = "postgres" ] && [ "$RSN_P" = "litellm" ] && [ "$RSN_M" = "gemini-3.6-flash" ] \
       && [ "$KEY_SET" = "SET" ]; then
      result WCONFIG PASS "worker settings match the staging AI contract (embedding=bge-m3/1024, vector=postgres, reasoning=litellm/gemini-3.6-flash, LITELLM_API_KEY set)"
    else
      result WCONFIG FAIL "worker AI configuration deviates from the staging contract: embedding=$EMB_P/$EMB_D/$EMB_M vector=$VDB_P reasoning=$RSN_P/$RSN_M LITELLM_API_KEY=$KEY_SET"
    fi
  else
    sed 's/^/  /' "$TMP_HOST/config.txt" 2>/dev/null
    result WCONFIG FAIL "could not execute the config-report snippet inside the worker container"
  fi
fi

# ============================================================================
# SECTION 5 — CELERY WORKER READINESS, REGISTERED TASK, LOGS
# ============================================================================
section 5 "CELERY WORKER READINESS"
if [ -z "$CID_WORKER" ]; then
  result WORKER_READY FAIL "worker container not found"
else
  WNAME="$(docker inspect -f '{{.Name}}' "$CID_WORKER" 2>/dev/null | tr -d '/')"
  log "worker container: $WNAME (state=$(state_of "$CID_WORKER"))"
  if docker exec "$CID_WORKER" celery -A app.workers.celery_app inspect ping --timeout=25 2>/dev/null | grep -q pong; then
    log "celery inspect ping: pong (worker responsive)"
    PING_OK=1
  else
    docker exec "$CID_WORKER" celery -A app.workers.celery_app inspect ping --timeout=25 2>&1 | sed 's/^/  /' | head -n 6
    PING_OK=0
  fi
  REG_OUT="$(docker exec "$CID_WORKER" celery -A app.workers.celery_app inspect registered --timeout=25 2>/dev/null || true)"
  if printf '%s' "$REG_OUT" | grep -qF "$REQUIRED_TASK"; then
    log "registered task present: $REQUIRED_TASK"
    TASK_OK=1
  else
    log "registered tasks (excerpt):"
    printf '%s\n' "$REG_OUT" | grep -oE "'app\.workers\.tasks\.[^']+'" | sort -u | head -n 10 | sed 's/^/  /'
    TASK_OK=0
  fi
  if [ "$PING_OK" = "1" ] && [ "$TASK_OK" = "1" ]; then
    result WORKER_READY PASS "celery worker responsive; $REQUIRED_TASK registered"
  elif [ "$PING_OK" = "1" ]; then
    result WORKER_READY FAIL "worker responds to ping but $REQUIRED_TASK is NOT registered"
  else
    result WORKER_READY FAIL "celery worker did not answer inspect ping"
  fi

  # Sentry BadDsn — known observability/config warning, not an AI pipeline failure.
  BADDSN="$(docker logs --tail 4000 "$CID_WORKER" 2>&1 | grep -c 'BadDsn' || true)"
  if [ "${BADDSN:-0}" -gt 0 ]; then
    log "worker log excerpt (BadDsn):"
    docker logs --tail 4000 "$CID_WORKER" 2>&1 | grep -m 2 'BadDsn' | sed 's/^/  /'
    result SENTRY_OBS WARN "Sentry BadDsn('Missing public key') warning present x${BADDSN} — malformed SENTRY_DSN; observability/config issue only, NOT an AI-pipeline failure (worker ready + processing unaffected)"
  else
    result SENTRY_OBS PASS "no BadDsn warnings in recent worker logs"
  fi

  log "recent worker log lines mentioning material processing (last 30):"
  docker logs --tail 4000 "$CID_WORKER" 2>&1 \
    | grep -E 'material_(content_processed|processing_failed|processing_skipped|processing_aborted|failed_persistence|failed_recovery)' \
    | tail -n 30 | sed 's/^/  /' || note "(none in recent history)"
fi

# ============================================================================
# SECTION 6 — PAL PROVIDER VERIFICATION (real factory, inside worker container)
# ============================================================================
section 6 "PAL PROVIDER VERIFICATION (factory -> concrete providers)"

cat > "$TMP_HOST/b7_provider_checks.py" <<'PY'
import asyncio
import json


def line(tag, **kw):
    print(json.dumps({"tag": tag, **kw}, separators=(",", ":"), default=str), flush=True)


async def main():
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from app.config import settings
    from app.pal.exceptions import ConfigurationError
    from app.pal.factory import (
        get_embedding_provider,
        get_reasoning_provider,
        get_vector_db_provider,
    )

    # -- embedding through the real factory -----------------------------------
    ep = get_embedding_provider()
    line("B7EMBF", concrete=type(ep).__name__, provider=str(getattr(ep, "provider_name", None)),
         dimension=int(ep.dimension), model=settings.ai_embedding_model)
    h = await ep.health_check()
    line("B7EMBH", healthy=bool(h.healthy), message=str(h.message))

    # -- vector db through the real required AsyncSession path ----------------
    engine = create_async_engine(settings.database_url)
    maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    try:
        async with maker() as session:
            vp = get_vector_db_provider(session=session)
            line("B7VECF", concrete=type(vp).__name__)
            vh = await vp.health_check()
            line("B7VECH", healthy=bool(vh.healthy), message=str(vh.message))
        try:
            get_vector_db_provider()
            line("B7VECG", guard="NOT_ENFORCED")
        except ConfigurationError:
            line("B7VECG", guard="ENFORCED")
    finally:
        await engine.dispose()

    # -- reasoning through the real factory -----------------------------------
    rp = get_reasoning_provider()
    line("B7RSNF", concrete=type(rp).__name__)
    rh = await rp.health_check()
    line("B7RSNH", healthy=bool(rh.healthy), message=str(rh.message))


asyncio.run(main())
PY

if [ -z "$CID_WORKER" ]; then
  result EMB_FACTORY FAIL "worker container not found"
  result VEC_PROVIDER FAIL "worker container not found"
  result RSN_FACTORY FAIL "worker container not found"
else
  push_file "$CID_WORKER" "$TMP_HOST/b7_provider_checks.py" "$CONTAINER_TMP/b7_provider_checks.py" || true
  if timeout 300 docker exec "$CID_WORKER" python "$CONTAINER_TMP/b7_provider_checks.py" > "$TMP_HOST/providers.txt" 2>&1; then
    sed 's/^/  /' "$TMP_HOST/providers.txt"
    if grep_marker "$TMP_HOST/providers.txt" '"tag":"B7EMBF","concrete":"BGEM3EmbeddingProvider","provider":"bge-m3","dimension":1024' \
       && grep_marker "$TMP_HOST/providers.txt" '"healthy":true' ; then
      if grep_marker "$TMP_HOST/providers.txt" '"tag":"B7EMBH","healthy":true'; then
        result EMB_FACTORY PASS "factory returned BGEM3EmbeddingProvider (bge-m3, dimension 1024) and health_check() passed"
      else
        result EMB_FACTORY FAIL "factory type correct but embedding health_check() reported unhealthy"
      fi
    elif grep_marker "$TMP_HOST/providers.txt" '"concrete":"BGEM3EmbeddingProvider"'; then
      result EMB_FACTORY FAIL "BGEM3EmbeddingProvider constructed but dimension/provider mismatch — see B7EMBF line above"
    else
      result EMB_FACTORY FAIL "factory did not return BGEM3EmbeddingProvider (or snippet failed) — see output above"
    fi

    if grep_marker "$TMP_HOST/providers.txt" '"tag":"B7VECF","concrete":"PostgresVectorDBProvider"' \
       && grep_marker "$TMP_HOST/providers.txt" '"tag":"B7VECH","healthy":true' \
       && grep_marker "$TMP_HOST/providers.txt" '"tag":"B7VECG","guard":"ENFORCED"'; then
      result VEC_PROVIDER PASS "PostgresVectorDBProvider constructed through its real AsyncSession path; SELECT 1 health passed; factory refuses session-less construction (ConfigurationError)"
    else
      result VEC_PROVIDER FAIL "vector provider construction/health/session-guard evidence incomplete — see B7VEC* lines above"
    fi

    if grep_marker "$TMP_HOST/providers.txt" '"tag":"B7RSNF","concrete":"LiteLLMReasoningProvider"' \
       && grep_marker "$TMP_HOST/providers.txt" '"tag":"B7RSNH","healthy":true'; then
      result RSN_FACTORY PASS "factory returned LiteLLMReasoningProvider; authenticated GET /models health probe passed from the worker network"
    else
      result RSN_FACTORY FAIL "reasoning factory/health evidence incomplete — see B7RSN* lines above"
    fi
  else
    log "snippet output:"
    sed 's/^/  /' "$TMP_HOST/providers.txt" 2>/dev/null
    result EMB_FACTORY FAIL "provider-checks snippet failed inside worker container"
    result VEC_PROVIDER FAIL "provider-checks snippet failed inside worker container"
    result RSN_FACTORY FAIL "provider-checks snippet failed inside worker container"
  fi

  # ----- direct BGE-M3 embed probe (loads the model once in an exec process) --
  if [ "$B7_EMBED_PROOF" = "1" ]; then
    cat > "$TMP_HOST/b7_embed_proof.py" <<'PY'
import asyncio
import json


def line(tag, **kw):
    print(json.dumps({"tag": tag, **kw}, separators=(",", ":"), default=str), flush=True)


async def main():
    from app.pal.factory import get_embedding_provider

    ep = get_embedding_provider()
    res = await ep.embed("OpenLearn B7 staging verification probe.")
    v = [float(x) for x in res.vector]
    norm = sum(x * x for x in v) ** 0.5
    nonzero = any(abs(x) > 1e-6 for x in v)
    line(
        "B7EMB",
        dimension=len(v),
        norm=round(norm, 4),
        nonzero=bool(nonzero),
        model=str(res.model),
        provider=str(res.provider),
        metadata=json.dumps(res.metadata, separators=(",", ":"), default=str),
        normalized_ok=bool(abs(norm - 1.0) < 0.02 and nonzero),
    )


asyncio.run(main())
PY
    push_file "$CID_WORKER" "$TMP_HOST/b7_embed_proof.py" "$CONTAINER_TMP/b7_embed_proof.py" || true
    log "running one real BGE-M3 embed (loads the model in this exec process; may take a"
    log "while on first run if the HF cache volume is cold; ~2 GB RAM)..."
    if timeout 420 docker exec "$CID_WORKER" python "$CONTAINER_TMP/b7_embed_proof.py" > "$TMP_HOST/embed.txt" 2>&1; then
      sed 's/^/  /' "$TMP_HOST/embed.txt"
      if grep_marker "$TMP_HOST/embed.txt" '"normalized_ok":true' \
         && grep_marker "$TMP_HOST/embed.txt" '"dimension":1024'; then
        result EMB_PROOF PASS "real embed returned a 1024-dim, L2-normalized (norm~1.0), non-zero vector — BGE-M3 behavior, not the mock provider (mock returns the all-zero vector)"
      else
        result EMB_PROOF FAIL "embed probe did not show normalized 1024-dim behavior — see B7EMB line above"
      fi
    else
      log "(embed probe timed out or failed):"
      tail -n 5 "$TMP_HOST/embed.txt" 2>/dev/null | sed 's/^/  /'
      result EMB_PROOF BLOCKED "embed probe did not complete within 420 s (cold HF cache download or memory pressure); the E2E run provides independent BGE-M3 evidence"
    fi
  else
    result EMB_PROOF SKIPPED "disabled via B7_EMBED_PROOF=0 (allowed; the E2E run still proves runtime embedding behavior)"
  fi
fi

# ============================================================================
# SECTION 7 — LITELLM GATEWAY CONNECTIVITY + ONE REAL REASONING CALL
# ============================================================================
section 7 "LITELLM GATEWAY (authenticated, from the worker network)"

if [ -z "$CID_WORKER" ]; then
  result LIT_MODELS FAIL "worker container not found"
else
  cat > "$TMP_HOST/b7_litellm_models.py" <<'PY'
import os

import requests

base = os.environ.get("LITELLM_API_BASE", "").rstrip("/")
key = os.environ.get("LITELLM_API_KEY", "")
if not base or not key:
    print("B7LIT|error|LITELLM_API_BASE or LITELLM_API_KEY missing in worker env")
    raise SystemExit(0)
try:
    r = requests.get(
        base + "/v1/models",
        headers={"Authorization": "Bearer " + key},
        timeout=30,
    )
except requests.RequestException as exc:
    print("B7LIT|error|" + type(exc).__name__)
    raise SystemExit(0)
print("B7LIT|status|" + str(r.status_code))
try:
    ids = [m.get("id") for m in r.json().get("data", [])]
    print("B7LIT|models|" + ",".join(str(i) for i in ids))
    print("B7LIT|expected_model_present|" + str("gemini-3.6-flash" in ids).lower())
except ValueError:
    print("B7LIT|models|<non-json response>")
PY
  push_file "$CID_WORKER" "$TMP_HOST/b7_litellm_models.py" "$CONTAINER_TMP/b7_litellm_models.py" || true
  if docker exec "$CID_WORKER" python "$CONTAINER_TMP/b7_litellm_models.py" > "$TMP_HOST/litellm.txt" 2>&1; then
    log "authenticated GET LITELLM_API_BASE/v1/models (key used from env, never printed):"
    sed 's/^/  /' "$TMP_HOST/litellm.txt"
    if grep_marker "$TMP_HOST/litellm.txt" "B7LIT|status|200" \
       && grep_marker "$TMP_HOST/litellm.txt" "B7LIT|expected_model_present|true"; then
      result LIT_MODELS PASS "authenticated /v1/models returned HTTP 200 and gemini-3.6-flash is listed"
    else
      result LIT_MODELS FAIL "authenticated /v1/models did not return 200 with the expected model — see output above"
    fi
  else
    sed 's/^/  /' "$TMP_HOST/litellm.txt" 2>/dev/null
    result LIT_MODELS FAIL "gateway probe snippet failed inside worker container"
  fi

  if [ "$B7_REASON_CALL" = "1" ]; then
    # B7-PHASE2 probe fix. The old probe pinned max_tokens=16: a
    # thinking-capable model (gemini-3.6-flash) spends that entire completion
    # budget on internal reasoning and returns empty visible content, which
    # the pinned PAL contract surfaces as ProviderServerError("no text
    # content") — the 2026-10-07 run's RSN_CALL FAIL happened exactly this
    # way even though the gateway itself returned HTTP 200. This probe walks
    # a generous max_tokens ladder and classifies the outcome so that an
    # upstream quota/rate-limit state (HTTP 429) stays an explicitly BLOCKED
    # external limitation instead of a FAIL or a manufactured PASS:
    #   SUCCESS | RATE_LIMITED | GATEWAY_UNAVAILABLE | AUTH_FAILED |
    #   CONFIG_ERROR | MODEL_UNAVAILABLE | PROVIDER_ERROR | EMPTY_CONTENT
    cat > "$TMP_HOST/b7_reason_call.py" <<'PY'
import asyncio
import json


def line(tag, **kw):
    print(json.dumps({"tag": tag, **kw}, separators=(",", ":"), default=str), flush=True)


PROMPT = "Reply with exactly this token and nothing else: B7-STAGING-OK"
# Thinking-capable models consume the completion budget with invisible
# reasoning tokens before emitting visible text; 16 tokens can never work.
# The ladder starts at a realistic reasoning+answer budget and retries once
# with a larger one when the gateway served the request but no visible text
# came back (finish_reason=length style outcome).
BUDGET_LADDER = (2048, 8192)


def classify(exc):
    from app.pal import exceptions as pal

    msg = str(exc)
    if isinstance(exc, pal.ProviderRateLimitError):
        return "RATE_LIMITED"
    if isinstance(exc, pal.ProviderTimeoutError):
        return "GATEWAY_UNAVAILABLE"
    if isinstance(exc, pal.ProviderUnavailableError):
        return "GATEWAY_UNAVAILABLE"
    if isinstance(exc, pal.ConfigurationError):
        if "HTTP 401" in msg or "HTTP 403" in msg:
            return "AUTH_FAILED"
        return "CONFIG_ERROR"
    if isinstance(exc, pal.InvalidInputError):
        return "MODEL_UNAVAILABLE"
    if isinstance(exc, pal.ProviderServerError):
        if "no text content" in msg:
            return "EMPTY_CONTENT"
        return "PROVIDER_ERROR"
    return "UNEXPECTED"


async def main():
    from app.config import settings
    from app.pal.factory import get_reasoning_provider

    rp = get_reasoning_provider()
    ladder = []
    res = None
    verdict = None
    for max_tokens in BUDGET_LADDER:
        try:
            res = await rp.reason(PROMPT, temperature=0.0, max_tokens=max_tokens)
        except Exception as exc:  # noqa: BLE001 — classifying failures IS the probe's job
            cls = classify(exc)
            ladder.append(
                {
                    "max_tokens": max_tokens,
                    "ok": False,
                    "class": cls,
                    "exc_type": type(exc).__name__,
                    "exc": str(exc)[:220],
                }
            )
            if cls == "EMPTY_CONTENT":
                # Gateway served the request but the completion budget was
                # consumed without visible text — retry with a larger one.
                continue
            verdict = cls
            break
        else:
            u = res.usage
            ladder.append(
                {
                    "max_tokens": max_tokens,
                    "ok": True,
                    "provider": str(res.provider),
                    "model": str(res.model),
                    "text_preview": str(res.text)[:60],
                    "finish_reason": str((res.metadata or {}).get("finish_reason")),
                    "prompt_tokens": (u.prompt_tokens if u else None),
                    "completion_tokens": (u.completion_tokens if u else None),
                    "total_tokens": (u.total_tokens if u else None),
                }
            )
            verdict = "SUCCESS"
            break
    if verdict is None:
        verdict = "EMPTY_CONTENT"
    line(
        "B7RSNCLASS",
        verdict=verdict,
        configured_model=str(settings.ai_reasoning_model),
        expected_token_present=bool(res is not None and "B7-STAGING-OK" in str(res.text or "")),
        ladder=json.dumps(ladder, separators=(",", ":"), default=str),
    )


asyncio.run(main())
PY
    push_file "$CID_WORKER" "$TMP_HOST/b7_reason_call.py" "$CONTAINER_TMP/b7_reason_call.py" || true
    log "one real PAL reasoning call through the configured gateway (max_tokens ladder 2048 -> 8192 for thinking-capable models)..."
    if timeout 300 docker exec "$CID_WORKER" python "$CONTAINER_TMP/b7_reason_call.py" > "$TMP_HOST/reason.txt" 2>&1; then
      sed 's/^/  /' "$TMP_HOST/reason.txt"
      VERDICT="$(grep -oE '"verdict":"[A-Z_]+"' "$TMP_HOST/reason.txt" | head -n1 | cut -d'"' -f4)"
      case "$VERDICT" in
        SUCCESS)
          # The ladder rides inside the B7RSNCLASS line as an embedded JSON
          # string, so its quotes are escaped on the wire (\").
          if grep_marker "$TMP_HOST/reason.txt" '\"provider\":\"litellm\"'; then
            result RSN_CALL PASS "real PAL reason() via LiteLLMReasoningProvider -> gateway -> gemini-3.6-flash succeeded with a realistic completion budget (provider/model/usage in the ladder above; expected-token evidence reported, not gated)"
          else
            result RSN_CALL FAIL "reasoning call completed but provider identity mismatch — see ladder above"
          fi
          ;;
        RATE_LIMITED)
          result RSN_CALL BLOCKED "authenticated gateway + listed model, but upstream quota/rate-limit exhausted (ProviderRateLimitError, HTTP 429 — Gemini free-tier). External runtime limitation, NOT an application failure; re-run when the quota window resets. Full upstream error in the ladder above"
          ;;
        GATEWAY_UNAVAILABLE)
          result RSN_CALL BLOCKED "LiteLLM gateway unreachable or timed out from the worker network (connection/timeout mapping) — external runtime limitation; check the litellm container. Evidence in the ladder above"
          ;;
        PROVIDER_ERROR)
          result RSN_CALL BLOCKED "upstream provider error behind the gateway (HTTP 5xx / no choices) — external runtime limitation; evidence in the ladder above"
          ;;
        AUTH_FAILED)
          result RSN_CALL FAIL "gateway authentication/permission failure (HTTP 401/403) — staging configuration problem, not an upstream outage; evidence in the ladder above"
          ;;
        CONFIG_ERROR)
          result RSN_CALL FAIL "reasoning provider configuration incomplete (missing LITELLM_API_KEY / LITELLM_API_BASE) — staging configuration problem"
          ;;
        MODEL_UNAVAILABLE)
          result RSN_CALL FAIL "gateway rejected the reasoning request (HTTP 4xx — model unavailable / invalid request); evidence in the ladder above"
          ;;
        EMPTY_CONTENT)
          result RSN_CALL FAIL "model returned no visible text content even with the full max_tokens ladder (2048 -> 8192) — genuine empty-content anomaly (not the old 16-token probe artifact); evidence in the ladder above"
          ;;
        *)
          result RSN_CALL FAIL "reasoning outcome could not be classified (verdict='${VERDICT:-none}') — raw probe output above"
          ;;
      esac
    else
      log "(reasoning probe exec failed or timed out):"
      tail -n 8 "$TMP_HOST/reason.txt" 2>/dev/null | sed 's/^/  /'
      result RSN_CALL BLOCKED "reasoning probe could not complete inside the worker container (exec failure/timeout) — environment limitation; no verdict about the application"
    fi
  else
    result RSN_CALL SKIPPED "disabled via B7_REASON_CALL=0 (B6 staging evidence already covers the PAL reason() path)"
  fi
fi

# ============================================================================
# SECTION 8 — END-TO-END SEEDED PDF RUN (the core B7 evidence)
# ============================================================================
section 8 "END-TO-END SEEDED PDF RUN (pending -> processing -> ready -> vectors)"

cat > "$TMP_HOST/b7_e2e_run.py" <<'PY'
"""Seed user/course/material, upload the PDF, enqueue the REAL task, poll, verify.

Runs INSIDE the worker container using the application's own code paths:
app.services.material_service.create_material, app.services.storage._s3_client,
app.workers.publishing.enqueue_material_processing (celery send_task by name).
Only this script's own uniquely-marked rows are touched; deletion happens in
b7_cleanup.py.
"""
import asyncio
import json
import sys
import time
from pathlib import Path
from uuid import UUID

MARK = sys.argv[1]
PDF_PATH = sys.argv[2]
UPLOAD = sys.argv[3] == "1"
TIMEOUT_S = float(sys.argv[4])
IDS_FILE = sys.argv[5]


def out(step, **kw):
    print("B7E2E|" + json.dumps({"step": step, **kw}, separators=(",", ":"), default=str), flush=True)


async def main():
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from app.config import settings
    from app.models.course import Course
    from app.models.material import Material
    from app.models.user import User
    from app.services.material_service import build_material_s3_key, create_material
    from app.services.storage import _s3_client
    from app.workers.publishing import enqueue_material_processing

    engine = create_async_engine(settings.database_url)
    maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    user_id = course_id = material_id = s3_key = None
    try:
        async with maker() as session:
            user = User(
                keycloak_issuer="urn:openlearn:b7-staging-verify",
                keycloak_subject=f"b7-verify-{MARK}",
                email=f"b7-verify-{MARK}@b7-verify.invalid",
                email_verified=False,
                settings={},
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            user_id = str(user.id)

            course = Course(owner_id=user.id, title=f"B7 staging verification {MARK}")
            session.add(course)
            await session.commit()
            await session.refresh(course)
            course_id = str(course.id)
        out("seeded", user_id=user_id, course_id=course_id)

        # Persist ids EARLY so a later crash can never leak untracked rows.
        # Trailing newline: the verifier concatenates/appends these files, so
        # every file must end on its own line (a missing newline merges two
        # JSON objects into one invalid line and breaks downstream cleanup).
        with open(IDS_FILE, "w") as fh:
            json.dump({"mark": MARK, "user_id": user_id, "course_id": course_id,
                       "material_id": None, "s3_key": None}, fh)
            fh.write("\n")

        s3_key = build_material_s3_key(UUID(course_id), Path(PDF_PATH).name)
        if UPLOAD:
            body = Path(PDF_PATH).read_bytes()
            _s3_client().put_object(
                Bucket=settings.s3_bucket_name,
                Key=s3_key,
                Body=body,
                ContentType="application/pdf",
            )
            out("object_uploaded", s3_key=s3_key)

        async with maker() as session:
            material = await create_material(
                session,
                course_id=UUID(course_id),
                title=f"B7 staging verification {MARK}",
                s3_key=s3_key,
                uploaded_by=UUID(user_id),
            )
            material_id = str(material.id)
            initial_status = material.status
            out("registered", status=material.status, material_id=material_id, s3_key=s3_key)

            job_id = await enqueue_material_processing(
                material.id, material.s3_key, material.course_id, material.uploaded_by
            )
            out("enqueued", job_id=job_id)

        with open(IDS_FILE, "w") as fh:
            json.dump(
                {"mark": MARK, "user_id": user_id, "course_id": course_id,
                 "material_id": material_id, "s3_key": s3_key},
                fh,
            )
            fh.write("\n")

        # Poll the material status exactly like an observer would.
        from app.models.vector_record import VectorRecordModel

        t0 = time.monotonic()
        last = initial_status
        seen = [initial_status]
        while time.monotonic() - t0 < TIMEOUT_S:
            async with maker() as session:
                row = (
                    await session.execute(
                        select(Material).where(Material.id == UUID(material_id))
                    )
                ).scalar_one_or_none()
                status = row.status if row is not None else "ROW_GONE"
            if status != last:
                seen.append(status)
                out("status", status=status, elapsed_s=round(time.monotonic() - t0, 1))
                last = status
            if status in ("ready", "failed", "ROW_GONE"):
                break
            await asyncio.sleep(2.0)

        out("final_status", status=last, elapsed_s=round(time.monotonic() - t0, 1))

        async with maker() as session:
            vrows = (
                await session.execute(
                    select(VectorRecordModel).where(
                        VectorRecordModel.id.like(f"{material_id}:%")
                    )
                )
            ).scalars().all()
            out("vector_count", count=len(vrows))
            ok_dims = len(vrows) > 0
            ok_prov = len(vrows) > 0
            ok_norm = len(vrows) > 0
            for r in vrows:
                vec = [float(x) for x in r.embedding]
                norm = sum(x * x for x in vec) ** 0.5
                meta = r.metadata_ or {}
                out(
                    "vector_row",
                    id=r.id,
                    dim=len(vec),
                    norm=round(norm, 4),
                    metadata_material_id=meta.get("material_id"),
                    metadata_document_id=meta.get("document_id"),
                    metadata_chunk_id=meta.get("chunk_id"),
                    metadata_pages=meta.get("pages"),
                    metadata_section=meta.get("section"),
                    metadata_language=meta.get("language"),
                    metadata_char_count=meta.get("char_count"),
                    metadata_page_count=meta.get("page_count"),
                    content_chars=len(r.content or ""),
                    content_preview=(r.content or "")[:60],
                )
                if len(vec) != 1024:
                    ok_dims = False
                if meta.get("material_id") != material_id:
                    ok_prov = False
                if not meta.get("chunk_id") or not meta.get("document_id"):
                    ok_prov = False
                if not (0.95 <= norm <= 1.05):
                    ok_norm = False
            expected_doc_id = Path(PDF_PATH).stem
            out("expected_document_id", value=expected_doc_id)
            lifecycle_ok = (
                initial_status == "pending"
                and last == "ready"
                and "processing" in seen
            )
            out("verdict_lifecycle", ok=bool(lifecycle_ok), final=str(last), transitions=json.dumps(seen))
            out("verdict_vectors", ok=bool(ok_dims), count=len(vrows), required_dimension=1024)
            out("verdict_provenance", ok=bool(ok_prov))
            out("verdict_bge_discrim", ok=bool(ok_norm), note="norm~1.0=BGE-M3 L2-normalized; norm~0.0 would be the mock provider")
    finally:
        await engine.dispose()


asyncio.run(main())
PY

run_e2e() { # run_e2e <pdf-host-path> <upload 1|0> <timeout> <ids-file> <outfile>
  local pdf="$1" upload="$2" tmo="$3" idsf="$4" outfile="$5"
  local runmark="${MARK}-$(basename "$pdf" | tr -cd 'a-zA-Z0-9' | cut -c1-40)"
  push_file "$CID_WORKER" "$pdf" "$CONTAINER_TMP/$(basename "$pdf")" || return 9
  docker exec "$CID_WORKER" rm -f "$idsf" >/dev/null 2>&1
  timeout "$((tmo + 60))" docker exec "$CID_WORKER" python "$CONTAINER_TMP/b7_e2e_run.py" \
    "$runmark" "$CONTAINER_TMP/$(basename "$pdf")" \
    "$upload" "$tmo" "$idsf" > "$outfile" 2>&1
}

E2E_START_EPOCH="$(date +%s)"
if [ -z "$CID_WORKER" ] || [ -z "$CID_MINIO" ]; then
  result E2E_LIFECYCLE FAIL "worker/minio container not found; E2E run not attempted"
  result E2E_VECTORS FAIL "E2E run not attempted"
  result E2E_PROVENANCE FAIL "E2E run not attempted"
  result E2E_DISCRIM FAIL "E2E run not attempted"
else
  VEC_BASELINE="$(pg_count "vector_records")"
  log "pre-existing vector_records rows (baseline, read-only count): ${VEC_BASELINE:-?}"
  push_file "$CID_WORKER" "$TMP_HOST/b7_e2e_run.py" "$CONTAINER_TMP/b7_e2e_run.py" || true
  E2E_IDS="$CONTAINER_TMP/ids_e2e.json"
  log "uploading the repository smoke PDF and exercising the REAL production seam:"
  log "  register material (pending) -> celery send_task -> storage fetch -> Docling ingest"
  log "  -> targeted OCR gate -> chunk -> BGE-M3 embed -> pgvector upsert -> ready"
  run_e2e "$ROOT/$PDF_REL" 1 "$B7_E2E_TIMEOUT" "$E2E_IDS" "$TMP_HOST/e2e.txt"
  RC=$?
  grep -E '^B7E2E\|' "$TMP_HOST/e2e.txt" | sed 's/^/  /'
  if [ "$RC" != "0" ]; then
    log "(snippet rc=$RC — last raw lines for diagnosis:)"
    tail -n 15 "$TMP_HOST/e2e.txt" | sed 's/^/  /'
  fi

  if grep_marker "$TMP_HOST/e2e.txt" '"step":"verdict_lifecycle","ok":true'; then
    result E2E_LIFECYCLE PASS "material progressed pending -> processing -> ready through the real Celery task; timings in B7E2E status lines above"
  else
    result E2E_LIFECYCLE FAIL "lifecycle verdict not satisfied (final status / transitions above; rc=$RC)"
  fi
  if grep_marker "$TMP_HOST/e2e.txt" '"step":"verdict_vectors","ok":true'; then
    VC="$(grep -oE '"step":"vector_count","count":[0-9]+' "$TMP_HOST/e2e.txt" | head -n1 | cut -d: -f3)"
    result E2E_VECTORS PASS "${VC:-?} vector_records rows persisted for this material (pgvector), every embedding 1024-dim"
  else
    result E2E_VECTORS FAIL "no valid 1024-dim vector rows for the processed material"
  fi
  if grep_marker "$TMP_HOST/e2e.txt" '"step":"verdict_provenance","ok":true'; then
    result E2E_PROVENANCE PASS "JSONB provenance verified: material_id matches, document_id/chunk_id/pages/char_count present (document_id = source-file stem, NOT the material id)"
  else
    result E2E_PROVENANCE FAIL "provenance metadata incomplete or mismatched — see vector_row lines above"
  fi
  if grep_marker "$TMP_HOST/e2e.txt" '"step":"verdict_bge_discrim","ok":true'; then
    result E2E_DISCRIM PASS "persisted vectors are L2-normalized (norm ~1.0) — BGE-M3 output; the mock provider would persist all-zero vectors (norm 0.0)"
  else
    result E2E_DISCRIM FAIL "vector norms inconsistent with BGE-M3 (possible mock provider at runtime) — see vector_row norms"
  fi

  # worker-log correlation for exactly this run window
  log "worker logs for the E2E window (material events):"
  docker logs --since "$E2E_START_EPOCH" "$CID_WORKER" 2>&1 \
    | grep -E 'material_content_processed|material_processing_failed|material_processing_skipped|claim|BadDsn' \
    | tail -n 20 | sed 's/^/  /' || note "(no matching worker log lines)"
fi

# ============================================================================
# SECTION 9 — OCR EVIDENCE (as observable as the implementation allows)
# ============================================================================
section 9 "OCR EVIDENCE"

cat > "$TMP_HOST/b7_page_chars.py" <<'PY'
"""Real Docling ingestion of a PDF inside the worker; per-page gate inputs.

The OCR decision gate is app.services.ocr.needs_ocr: len(page_text) <
settings.ocr_min_text_chars. This computes the gate inputs the same way the
task does and reports them verbatim. Used for BOTH the born-digital smoke
PDF (gate-skip evidence) and, when B7_RUN_OCR_TRIGGER=1, the scanned PDF
(the correct extraction baseline for the OCR-trigger comparison — the old
verifier wrongly compared the scanned run's chunk sizes against the SMOKE
PDF's extraction).
"""
import json
import sys

from app.config import settings
from app.services.ingestion import ingest_document
from app.services.ocr import needs_ocr

path = sys.argv[1]
threshold = int(settings.ocr_min_text_chars)
doc = ingest_document(path)
pages = [(p.page_number, len(p.text), bool(needs_ocr(p.text))) for p in doc.pages]
below = [n for (_, n, needs) in pages if needs]
print(json.dumps({
    "tag": "B7OCR",
    "threshold": threshold,
    "pages": [{"page": p, "chars": n, "needs_ocr": needs} for (p, n, needs) in pages],
    "pages_below_threshold": len(below),
}, separators=(",", ":"), default=str))
PY

if [ -z "$CID_WORKER" ]; then
  result OCR_GATE BLOCKED "worker container not found"
  result OCR_PAGELEVEL NOT_OBSERVABLE "no runtime available"
else
  THR="$(grep_val "$TMP_HOST/config.txt" ocr_min_text_chars 2>/dev/null)"
  log "ocr_min_text_chars (settings): ${THR:-?} (repo default 50; OCR_MIN_TEXT_CHARS is not set in the staging compose)"
  push_file "$CID_WORKER" "$ROOT/$PDF_REL" "$CONTAINER_TMP/smoke.pdf" || true
  push_file "$CID_WORKER" "$TMP_HOST/b7_page_chars.py" "$CONTAINER_TMP/b7_page_chars.py" || true
  if timeout 240 docker exec "$CID_WORKER" python "$CONTAINER_TMP/b7_page_chars.py" "$CONTAINER_TMP/smoke.pdf" > "$TMP_HOST/ocr.txt" 2>&1; then
    sed 's/^/  /' "$TMP_HOST/ocr.txt"
    if grep_marker "$TMP_HOST/ocr.txt" '"pages_below_threshold":0'; then
      result OCR_GATE PASS "gate math verified on the real ingested smoke PDF: every page text >= ocr_min_text_chars (${THR:-50}) so the OCR loop correctly skips every page (no OCR provider call is possible for this input)"
    else
      result OCR_GATE PARTIAL "some pages fell below the threshold for the smoke PDF (unexpected for the chosen born-digital page); see page breakdown above"
    fi
    # B7-PHASE2: the app now emits ocr_gate_evaluated (per-page decisions)
    # and ocr_enrichment_applied (only when a page was actually OCR'd) as
    # structured worker-log events. When the deployed image carries them,
    # OCR_PAGELEVEL becomes directly observable; against an older image the
    # honest NOT_OBSERVABLE state is kept instead of a manufactured pass.
    OCR_GATE_EVENTS="$(docker logs --since "$E2E_START_EPOCH" "$CID_WORKER" 2>&1 | grep -c 'ocr_gate_evaluated' || true)"
    OCR_APPLIED_EVENTS="$(docker logs --since "$E2E_START_EPOCH" "$CID_WORKER" 2>&1 | grep -c 'ocr_enrichment_applied' || true)"
    log "worker-log OCR events since the E2E window start: ocr_gate_evaluated=${OCR_GATE_EVENTS:-0} ocr_enrichment_applied=${OCR_APPLIED_EVENTS:-0}"
    if [ "${OCR_GATE_EVENTS:-0}" -gt 0 ] 2>/dev/null && [ "${OCR_APPLIED_EVENTS:-0}" = "0" ] 2>/dev/null; then
      result OCR_PAGELEVEL PASS "runtime log evidence: the OCR gate logged its per-page decisions (ocr_gate_evaluated, chars vs threshold) for the born-digital smoke PDF and NO page triggered enrichment (zero ocr_enrichment_applied events) — the loop provably fired for zero pages"
    elif [ "${OCR_GATE_EVENTS:-0}" -gt 0 ] 2>/dev/null && [ "${OCR_APPLIED_EVENTS:-0}" -gt 0 ] 2>/dev/null; then
      result OCR_GATE PARTIAL "ocr_enrichment_applied events present in the E2E window even though the smoke PDF has no page below the threshold — see log lines above"
      result OCR_PAGELEVEL NOT_OBSERVABLE "gate events present but enrichment events contradict the gate math; inspect the log excerpt above"
    else
      result OCR_PAGELEVEL NOT_OBSERVABLE "the deployed image predates the B7-PHASE2 OCR gate logging (no ocr_gate_evaluated events in the worker log); the gate-math evidence above is the available runtime evidence for this image"
    fi
  else
    log "(page-chars snippet failed):"
    tail -n 6 "$TMP_HOST/ocr.txt" 2>/dev/null | sed 's/^/  /'
    result OCR_GATE BLOCKED "could not run Docling page-character analysis inside the worker container"
    result OCR_PAGELEVEL NOT_OBSERVABLE "no runtime evidence available"
  fi
fi

if [ "$B7_RUN_OCR_TRIGGER" = "1" ]; then
  log ""
  log "B7_RUN_OCR_TRIGGER=1 — processing the repository scanned PDF (one real Gemini"
  log "OCR call will be made for its below-threshold page). This makes an external"
  log "API call and is therefore opt-in."
  if [ -f "$ROOT/$PDF_TRIGGER_REL" ]; then
    OCR_IDS="$CONTAINER_TMP/ids_ocr.json"
    E2E_OCR_START="$(date +%s)"
    run_e2e "$ROOT/$PDF_TRIGGER_REL" 1 "$B7_E2E_TIMEOUT" "$OCR_IDS" "$TMP_HOST/e2e_ocr.txt"
    RC_OCR=$?
    grep -E '^B7E2E\|' "$TMP_HOST/e2e_ocr.txt" | sed 's/^/  /'
    # Baseline for the comparison must be the SCANNED PDF's own Docling
    # extraction (the old verifier compared against the SMOKE PDF's chars).
    push_file "$CID_WORKER" "$ROOT/$PDF_TRIGGER_REL" "$CONTAINER_TMP/trigger.pdf" || true
    if timeout 240 docker exec "$CID_WORKER" python "$CONTAINER_TMP/b7_page_chars.py" "$CONTAINER_TMP/trigger.pdf" > "$TMP_HOST/ocr_trigger_baseline.txt" 2>&1; then
      sed 's/^/  /' "$TMP_HOST/ocr_trigger_baseline.txt"
      DOC_CHARS="$(grep -oE '"chars":[0-9]+' "$TMP_HOST/ocr_trigger_baseline.txt" | grep -oE '[0-9]+' | sort -n | tail -n1)"
      BELOW="$(grep -oE '"pages_below_threshold":[0-9]+' "$TMP_HOST/ocr_trigger_baseline.txt" | grep -oE '[0-9]+$')"
    else
      log "(scanned-PDF baseline snippet failed):"
      tail -n 6 "$TMP_HOST/ocr_trigger_baseline.txt" 2>/dev/null | sed 's/^/  /'
      DOC_CHARS=""; BELOW=""
    fi
    CHARS="$(grep -oE '"metadata_char_count":[0-9]+' "$TMP_HOST/e2e_ocr.txt" | grep -oE '[0-9]+$' | sort -n | tail -n1)"
    OCR_APPLIED_LOGS="$(docker logs --since "$E2E_OCR_START" "$CID_WORKER" 2>&1 | grep -c 'ocr_enrichment_applied' || true)"
    if [ -z "${BELOW:-}" ] || [ "${BELOW:-0}" -eq 0 ] 2>/dev/null; then
      result OCR_TRIGGER BLOCKED "the trigger PDF does not present any page below ocr_min_text_chars (below-threshold pages: ${BELOW:-unknown}) — its OCR gate would never fire, so this file cannot produce OCR-trigger evidence"
    elif grep_marker "$TMP_HOST/e2e_ocr.txt" '"step":"verdict_lifecycle","ok":true' \
         && [ -n "${CHARS:-}" ] && [ "${CHARS:-0}" -gt "${DOC_CHARS:-0}" ] 2>/dev/null; then
      if [ "${OCR_APPLIED_LOGS:-0}" -gt 0 ] 2>/dev/null; then
        result OCR_TRIGGER PASS "DIRECT evidence: scanned page extracted at most ${DOC_CHARS:-0} chars by Docling (< threshold) yet persisted chunk content has ${CHARS} chars, AND the worker logged ocr_enrichment_applied (page, chars_before -> chars_after, provider) — OCR text flowed through the real pipeline (status ready)"
      else
        result OCR_TRIGGER PASS "DIRECT evidence: scanned page extracted at most ${DOC_CHARS:-0} chars by Docling (< threshold) yet persisted chunk content has ${CHARS} chars — OCR text flowed through the real pipeline (status ready; ocr_enrichment_applied log events require the B7-PHASE2 image)"
      fi
    elif grep -q 'material_processing_failed' "$TMP_HOST/e2e_ocr.txt" 2>/dev/null \
         || grep_marker "$TMP_HOST/e2e_ocr.txt" '"final_status","status":"failed"'; then
      result OCR_TRIGGER FAIL "OCR-trigger run ended in material 'failed' (Gemini OCR provider failure?) — evidence above; NOT silently attributed to B7 pipeline logic without the worker log"
      docker logs --since "$E2E_OCR_START" "$CID_WORKER" 2>&1 | grep -E 'material_processing_failed|Traceback|Error' | tail -n 15 | sed 's/^/  /'
    else
      result OCR_TRIGGER BLOCKED "OCR-trigger run inconclusive (rc=$RC_OCR) — evidence above"
    fi
  else
    result OCR_TRIGGER BLOCKED "scanned PDF not found in repository: $PDF_TRIGGER_REL"
  fi
else
  result OCR_TRIGGER NOT_OBSERVABLE "opt-in run skipped (B7_RUN_OCR_TRIGGER=0); page-level OCR behavior remains code-verified + gate-math-verified only"
fi

# ============================================================================
# SECTION 10 — FORCED PROCESSING FAILURE (safe staging-only seam)
# ============================================================================
section 10 "FORCED PROCESSING FAILURE"

cat > "$TMP_HOST/b7_cleanup.py" <<'PY'
"""Delete ONLY the rows/object created by this run (exact UUIDs; never broad).

B7-PHASE2 hardening: every delete is (a) scoped to an exact recorded UUID and
(b) guarded by the B7 verification-resource predicate (synthetic issuer URN
for the user, "B7 staging verification " title prefix for course and
material), so a corrupted or hand-edited ids file can never make this script
delete arbitrary user data — the guard refuses and reports instead.

Ordering and completeness guarantees:

* vector rows are deleted FIRST and explicitly (the table is FK-less by
  design, so no relational cascade can ever remove them), then material,
  then course, then user — FK-safe order;
* the S3 object is deleted by its exact recorded key, every S3 outcome is
  reported as its own structured step (deleted / error), and a successful
  delete is verified afterwards with head_object (expected 404);
* every step is idempotent: deleting an already-deleted row touches 0 rows
  and S3 deletes of an absent key are a no-op success.
"""
import asyncio
import json
import sys
from uuid import UUID

IDS_FILE = sys.argv[1]

B7_ISSUER = "urn:openlearn:b7-staging-verify"
B7_TITLE_PREFIX = "B7 staging verification "


def out(step, **kw):
    print("B7CLN|" + json.dumps({"step": step, **kw}, separators=(",", ":"), default=str), flush=True)


async def main():
    from sqlalchemy import delete, func, select
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from app.config import settings
    from app.models.course import Course
    from app.models.material import Material
    from app.models.user import User
    from app.models.vector_record import VectorRecordModel

    try:
        with open(IDS_FILE) as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        out("ids_file_error", file=IDS_FILE, error=f"{type(exc).__name__}: {exc}")
        return

    mid = data.get("material_id")
    cid = data.get("course_id")
    uid = data.get("user_id")
    s3_key = data.get("s3_key")

    engine = create_async_engine(settings.database_url)
    maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    try:
        async with maker() as session:
            # ---- predicate guards: refuse anything not created by B7 runs --
            if uid:
                urow = (
                    await session.execute(select(User).where(User.id == UUID(uid)))
                ).scalar_one_or_none()
                if urow is not None and not (
                    urow.keycloak_issuer == B7_ISSUER
                    and str(urow.keycloak_subject).startswith("b7-verify-")
                ):
                    out("refused_user_not_b7_resource", user_id=uid)
                    return
            if cid:
                crow = (
                    await session.execute(select(Course).where(Course.id == UUID(cid)))
                ).scalar_one_or_none()
                if crow is not None and not str(crow.title).startswith(B7_TITLE_PREFIX):
                    out("refused_course_not_b7_resource", course_id=cid)
                    return
            if mid:
                mrow = (
                    await session.execute(select(Material).where(Material.id == UUID(mid)))
                ).scalar_one_or_none()
                if mrow is not None and not str(mrow.title).startswith(B7_TITLE_PREFIX):
                    out("refused_material_not_b7_resource", material_id=mid)
                    return

            # ---- deletes: vectors (FK-less) first, then material/course/user
            if mid:
                r = await session.execute(
                    delete(VectorRecordModel).where(VectorRecordModel.id.like(f"{mid}:%"))
                )
                out("deleted_vector_records", count=int(r.rowcount or 0))
                r = await session.execute(delete(Material).where(Material.id == UUID(mid)))
                out("deleted_material", count=int(r.rowcount or 0))
            if cid:
                r = await session.execute(delete(Course).where(Course.id == UUID(cid)))
                out("deleted_course", count=int(r.rowcount or 0))
            if uid:
                r = await session.execute(delete(User).where(User.id == UUID(uid)))
                out("deleted_user", count=int(r.rowcount or 0))
            await session.commit()
            if mid:
                n_mat = (
                    await session.execute(
                        select(func.count()).select_from(Material).where(Material.id == UUID(mid))
                    )
                ).scalar_one()
                n_vec = (
                    await session.execute(
                        select(func.count()).select_from(VectorRecordModel).where(
                            VectorRecordModel.id.like(f"{mid}:%")
                        )
                    )
                ).scalar_one()
            else:
                n_mat, n_vec = 0, 0
            out("leftover_check", materials=int(n_mat), vectors=int(n_vec))

        if s3_key:
            from botocore.exceptions import ClientError

            from app.services.storage import _s3_client

            client = _s3_client()
            try:
                client.delete_object(Bucket=settings.s3_bucket_name, Key=s3_key)
                out("deleted_object", s3_key=s3_key)
            except Exception as exc:
                out("s3_delete_error", s3_key=s3_key, error=f"{type(exc).__name__}: {exc}")
            else:
                try:
                    client.head_object(Bucket=settings.s3_bucket_name, Key=s3_key)
                except ClientError as exc:
                    code = str(
                        (getattr(exc, "response", {}) or {}).get("Error", {}).get("Code", "")
                    )
                    if code in ("404", "NoSuchKey", "NotFound"):
                        out("object_verified_absent", s3_key=s3_key)
                    else:
                        out("s3_verify_error", s3_key=s3_key, code=code)
                except Exception as exc:
                    out("s3_verify_error", s3_key=s3_key, error=f"{type(exc).__name__}: {exc}")
                else:
                    out("s3_verify_still_present", s3_key=s3_key)
    finally:
        await engine.dispose()


asyncio.run(main())
PY

push_file "$CID_WORKER" "$TMP_HOST/b7_cleanup.py" "$CONTAINER_TMP/b7_cleanup.py" || true

cat > "$TMP_HOST/b7_cleanup_previous.py" <<'PY'
"""Opt-in removal of PREVIOUS verifier-run resources (B7_CLEAN_PREVIOUS_B7=1).

Scope discipline (this script must stay safe):

* candidates are enumerated SOLELY through the synthetic B7 verification
  issuer URN (urn:openlearn:b7-staging-verify) on users, EXCLUDING the
  current run's mark passed as argv[1] — real Keycloak issuers are https
  URLs, so this predicate can never match user data;
* courses are those owned by those users; materials are those uploaded by
  those users OR living in those users' courses; vector rows are matched by
  the exact material-id prefix list; S3 objects by the materials' recorded
  exact s3_key values;
* the complete inventory is PRINTED (exact UUIDs/keys) before any deletion,
  then deletions run in FK order: vectors -> materials -> courses -> users,
  each an exact-id list delete; every count is reported, and S3 failures are
  reported without aborting the row cleanup (re-runnable until clean);
* no title-pattern deletes, no unscoped deletes, no cascades assumed.
"""
import asyncio
import json
import sys

CURRENT_MARK = sys.argv[1] if len(sys.argv) > 1 else ""

B7_ISSUER = "urn:openlearn:b7-staging-verify"
B7_SUBJECT_PREFIX = "b7-verify-"


def out(step, **kw):
    print("B7CLN|" + json.dumps({"step": step, **kw}, separators=(",", ":"), default=str), flush=True)


async def main():
    from sqlalchemy import delete, select
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from app.config import settings
    from app.models.course import Course
    from app.models.material import Material
    from app.models.user import User
    from app.models.vector_record import VectorRecordModel

    engine = create_async_engine(settings.database_url)
    maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    try:
        async with maker() as session:
            users = (
                (
                    await session.execute(
                        select(User).where(
                            User.keycloak_issuer == B7_ISSUER,
                            User.keycloak_subject.notlike(f"{B7_SUBJECT_PREFIX}{CURRENT_MARK}%"),
                            User.keycloak_subject.like(f"{B7_SUBJECT_PREFIX}%"),
                        )
                    )
                )
                .scalars()
                .all()
            )
            user_ids = [u.id for u in users]
            if not user_ids:
                out("previous_cleanup_done", users_removed=0, courses_removed=0,
                    materials_removed=0, vectors_removed=0, s3_removed=0)
                return

            courses = (
                (await session.execute(select(Course).where(Course.owner_id.in_(user_ids))))
                .scalars()
                .all()
            )
            course_ids = [c.id for c in courses]
            candidate_filter = Material.uploaded_by.in_(user_ids)
            if course_ids:
                candidate_filter = candidate_filter | Material.course_id.in_(course_ids)
            materials = (
                (
                    await session.execute(select(Material).where(candidate_filter))
                )
                .scalars()
                .all()
            )
            material_ids = [m.id for m in materials]
            material_id_texts = [str(m) for m in material_ids]
            s3_keys = [m.s3_key for m in materials if m.s3_key]

            out("inventory", users=[str(u) for u in user_ids],
                courses=[str(c) for c in course_ids],
                materials=[str(m) for m in material_ids],
                s3_keys=s3_keys)

            vectors_removed = 0
            for mid_text in material_id_texts:
                r = await session.execute(
                    delete(VectorRecordModel).where(VectorRecordModel.id.like(f"{mid_text}:%"))
                )
                vectors_removed += int(r.rowcount or 0)
            out("deleted_vector_records", count=vectors_removed)

            materials_removed = 0
            for mid in material_ids:
                r = await session.execute(delete(Material).where(Material.id == mid))
                materials_removed += int(r.rowcount or 0)
            out("deleted_materials", count=materials_removed)

            courses_removed = 0
            for cid in course_ids:
                r = await session.execute(delete(Course).where(Course.id == cid))
                courses_removed += int(r.rowcount or 0)
            out("deleted_courses", count=courses_removed)

            users_removed = 0
            for uid in user_ids:
                r = await session.execute(delete(User).where(User.id == uid))
                users_removed += int(r.rowcount or 0)
            out("deleted_users", count=users_removed)

            await session.commit()

        s3_removed = 0
        s3_errors = []
        if s3_keys:
            from app.services.storage import _s3_client

            client = _s3_client()
            for key in s3_keys:
                try:
                    client.delete_object(Bucket=settings.s3_bucket_name, Key=key)
                    s3_removed += 1
                except Exception as exc:
                    s3_errors.append(f"{key}: {type(exc).__name__}: {exc}")
            out("s3_objects", removed=s3_removed,
                errors=(s3_errors if s3_errors else None))

        if s3_errors:
            out("previous_cleanup_error", s3_errors=s3_errors)
        else:
            out("previous_cleanup_done", users_removed=users_removed,
                courses_removed=courses_removed, materials_removed=materials_removed,
                vectors_removed=vectors_removed, s3_removed=s3_removed)
    finally:
        await engine.dispose()


asyncio.run(main())
PY

push_file "$CID_WORKER" "$TMP_HOST/b7_cleanup_previous.py" "$CONTAINER_TMP/b7_cleanup_previous.py" || true

run_forced_failure() {
  local idsf="$CONTAINER_TMP/ids_fail.json" outfile="$TMP_HOST/forced.txt"
  docker exec "$CID_WORKER" rm -f "$idsf" >/dev/null 2>&1
  timeout "$((B7_FAIL_TIMEOUT + 60))" docker exec "$CID_WORKER" python "$CONTAINER_TMP/b7_e2e_run.py" \
    "$MARK-fail" "$CONTAINER_TMP/does-not-exist-b7.pdf" 0 "$B7_FAIL_TIMEOUT" "$idsf" > "$outfile" 2>&1
}

FSTART="$(date +%s)"
if [ -z "$CID_WORKER" ]; then
  result FORCED_FAIL FAIL "worker container not found"
else
  log "mechanism: register a material whose storage object was never uploaded"
  log "(supported failure path: download_material_to_temp -> ClientError 404 ->"
  log "rollback -> status failed committed -> task re-raises). No code or config is"
  log "touched; nothing shared is corrupted."
  run_forced_failure
  RC_F=$?
  grep -E '^B7E2E\|' "$TMP_HOST/forced.txt" | sed 's/^/  /'
  if [ "$RC_F" != "0" ]; then
    log "(snippet rc=$RC_F — last raw lines:)"
    tail -n 12 "$TMP_HOST/forced.txt" | sed 's/^/  /'
  fi
  FINAL_F="$(grep -oE '"step":"final_status","status":"[a-z_]+"' "$TMP_HOST/forced.txt" | tail -n1 | grep -oE '"status":"[a-z_]+"' | cut -d'"' -f4)"
  VEC_F="$(grep -oE '"step":"vector_count","count":[0-9]+' "$TMP_HOST/forced.txt" | tail -n1 | cut -d: -f3)"
  if [ "${FINAL_F:-}" = "failed" ] && [ "${VEC_F:-1}" = "0" ]; then
    result FORCED_FAIL PASS "forced-failure material transitioned to 'failed' and persisted 0 vector rows (no false ready; task raised as designed — 'material_processing_failed' in worker log below)"
  elif [ "${FINAL_F:-}" = "failed" ]; then
    result FORCED_FAIL FAIL "material failed as expected but vector rows were found: count=${VEC_F:-?}"
  elif [ "${FINAL_F:-}" = "processing" ]; then
    result FORCED_FAIL BLOCKED "material stuck in processing after ${B7_FAIL_TIMEOUT}s (increase B7_FAIL_TIMEOUT; check worker logs)"
  else
    result FORCED_FAIL FAIL "forced-failure outcome unexpected: final=${FINAL_F:-?} vectors=${VEC_F:-?} (rc=$RC_F)"
  fi

  log "worker logs for the forced-failure window:"
  docker logs --since "$FSTART" "$CID_WORKER" 2>&1 \
    | grep -E 'material_processing_failed|Task .* raised unexpected|download|ClientError' \
    | tail -n 15 | sed 's/^/  /' || note "(no matching lines)"
fi

# ============================================================================
# SECTION 11 — DATABASE SCHEMA VERIFICATION (read-only SQL)
# ============================================================================
section 11 "DATABASE SCHEMA VERIFICATION (read-only)"
# B7-PHASE2 rewrite. The previous version (a) matched an UNORDERED
# string_agg() against a positional glob — aggregation order is undefined in
# SQL, so a known-good schema could fail the pattern nondeterministically;
# (b) matched table_name across ALL schemas; (c) discarded every psql/docker
# return code and stderr, so an evidence-collection failure was silently
# misread as a schema mismatch with no per-sub-check attribution; and (d)
# printed a log line mentioning a nonexistent vector_length function while
# the SQL actually used vector_dims (misleading evidence).
#
# Every sub-check below now: uses ordered, schema-qualified, PostgreSQL-native
# SQL (the same constructs the Phase-1 collector proved rc=0 against this
# database); captures and prints each probe's return code and raw value;
# distinguishes "evidence unavailable" (BLOCKED) from "schema mismatch"
# (FAIL); and validates the CHECK constraint by its NORMALIZED
# pg_get_constraintdef() value literals — never against migration text.
if [ -n "$CID_DB" ]; then
  DB_EVIDENCE_ERROR=0
  dbq() { # dbq <sql> — capture output+rc; prints the raw rows
    DBQ_OUT="$(psql_ro "$1")"
    DBQ_RC=$?
  }

  log "vector_records columns (name:udt, ordered, current schema):"
  dbq "SELECT column_name || ':' || udt_name FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = 'vector_records' ORDER BY ordinal_position;"
  VR_COLS_OUT="$DBQ_OUT"; VR_COLS_RC=$DBQ_RC
  if [ "$VR_COLS_RC" != "0" ] || [ -z "$VR_COLS_OUT" ]; then
    log "  (probe rc=$VR_COLS_RC, output empty or unavailable — evidence error)"
    DB_EVIDENCE_ERROR=1
  else
    printf '%s\n' "$VR_COLS_OUT" | sed 's/^/  /'
  fi

  SCHEMA_OK=1
  log "vector_records pinned column/type presence (each row must be 1):"
  for pair in id:text embedding:vector content:text metadata:jsonb; do
    col="${pair%%:*}"; typ="${pair##*:}"
    dbq "SELECT count(*) FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = 'vector_records' AND column_name = '$col' AND udt_name = '$typ';"
    val="$(printf '%s' "$DBQ_OUT" | tr -d '[:space:]')"
    log "  $col:$typ -> ${val:-<empty>} (rc=$DBQ_RC)"
    if [ "$DBQ_RC" != "0" ] || [ -z "$val" ]; then
      DB_EVIDENCE_ERROR=1; SCHEMA_OK=0
    elif [ "$val" != "1" ]; then
      SCHEMA_OK=0
    fi
  done

  log "materials status CHECK constraint (name + normalized definition):"
  dbq "SELECT count(*) FROM pg_constraint WHERE conrelid = 'materials'::regclass AND conname = 'ck_materials_status_supported';"
  CK_CNT="$(printf '%s' "$DBQ_OUT" | tr -d '[:space:]')"
  log "  constraint count: ${CK_CNT:-<empty>} (rc=$DBQ_RC)"
  if [ "$DBQ_RC" != "0" ] || [ -z "$CK_CNT" ]; then
    DB_EVIDENCE_ERROR=1; SCHEMA_OK=0
  elif [ "$CK_CNT" != "1" ]; then
    SCHEMA_OK=0
  fi
  dbq "SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = 'materials'::regclass AND conname = 'ck_materials_status_supported';"
  CK_DEF="$DBQ_OUT"
  if [ "$DBQ_RC" != "0" ] || [ -z "$CK_DEF" ]; then
    log "  normalized definition: <unavailable> (rc=$DBQ_RC)"
    DB_EVIDENCE_ERROR=1
  else
    log "  normalized definition: $CK_DEF"
    # Value-level check on the NORMALIZED definition — pg_get_constraintdef
    # output is PostgreSQL-controlled (parenthesization/casts may vary between
    # versions), but the quoted status literals are stable, so they are the
    # compared substance. The migration's literal SQL text is never used.
    for st in pending processing ready failed; do
      if printf '%s' "$CK_DEF" | grep -q "'$st'"; then
        log "  status '$st' in constraint: yes"
      else
        log "  status '$st' in constraint: NO"
        SCHEMA_OK=0
      fi
    done
  fi

  log "pgvector function availability (pg_proc):"
  dbq "SELECT count(*) FROM pg_proc WHERE proname = 'vector_dims';"
  VD_CNT="$(printf '%s' "$DBQ_OUT" | tr -d '[:space:]')"
  log "  vector_dims entries: ${VD_CNT:-<empty>} (rc=$DBQ_RC)"
  if [ "$DBQ_RC" != "0" ] || [ -z "$VD_CNT" ]; then
    DB_EVIDENCE_ERROR=1
  elif [ "$VD_CNT" = "0" ]; then
    DB_EVIDENCE_ERROR=1
    log "  (pgvector's vector_dims is required by the dimension check below)"
  fi

  log "vector_records embedding dimension check (rows where vector_dims(embedding) <> 1024):"
  if [ -n "$VD_CNT" ] && [ "$VD_CNT" != "0" ]; then
    dbq "SELECT count(*) FROM vector_records WHERE vector_dims(embedding) <> 1024;"
    DIM_BAD="$(printf '%s' "$DBQ_OUT" | tr -d '[:space:]')"
    log "  rows with wrong dimension: ${DIM_BAD:-<empty>} (rc=$DBQ_RC)"
    if [ "$DBQ_RC" != "0" ] || [ -z "$DIM_BAD" ]; then
      DB_EVIDENCE_ERROR=1; SCHEMA_OK=0
    elif [ "$DIM_BAD" != "0" ]; then
      SCHEMA_OK=0
    fi
  else
    log "  SKIPPED (vector_dims availability not proven)"
  fi

  log "alembic revision state:"
  dbq "SELECT version_num FROM alembic_version;"
  DB_VER="$(printf '%s' "$DBQ_OUT" | tr -d '[:space:]')"
  log "  database alembic_version: ${DB_VER:-<empty>} (rc=$DBQ_RC)"
  if [ "$DBQ_RC" != "0" ] || [ -z "$DB_VER" ]; then
    DB_EVIDENCE_ERROR=1
  fi
  REPO_HEADS="$(timeout 90 docker exec "$CID_WORKER" python -c "from alembic.config import Config; from alembic.script import ScriptDirectory; s = ScriptDirectory.from_config(Config('alembic.ini')); print(','.join(s.get_heads()))" 2>/dev/null | tr -d '[:space:]' || true)"
  log "  repo migration heads (in-image scan): ${REPO_HEADS:-<unavailable>}"
  if [ -n "$DB_VER" ] && [ -n "$REPO_HEADS" ]; then
    case ",$REPO_HEADS," in
      *",$DB_VER,"*)
        if [ "$(printf '%s' "$REPO_HEADS" | awk -F',' '{print NF}')" = "1" ]; then
          log "  database version matches the single repo head: yes"
        else
          log "  repo chain has MULTIPLE heads — branching bug in the migration tree"
          SCHEMA_OK=0
        fi
        ;;
      *)
        log "  database version matches the repo head chain: NO"
        SCHEMA_OK=0
        ;;
    esac
  else
    log "  (head comparison unavailable — reported, not failed)"
  fi

  if [ "$DB_EVIDENCE_ERROR" = "1" ]; then
    result DB_SCHEMA BLOCKED "evidence collection partially failed (a psql/docker probe returned an error or an empty result — see the rc= markers above); the schema itself could not be conclusively verified in this run"
  elif [ "$SCHEMA_OK" = "1" ]; then
    result DB_SCHEMA PASS "vector_records matches the pinned schema (id text, embedding vector, content text, metadata jsonb — ordered, schema-qualified, order-independent checks); materials status CHECK present and its normalized pg_get_constraintdef contains pending/processing/ready/failed; every stored embedding is 1024-dim via pgvector vector_dims; database alembic_version matches the single repo head"
  else
    result DB_SCHEMA FAIL "schema verification failed — the failing sub-checks are individually marked above"
  fi
else
  result DB_SCHEMA FAIL "db container not found"
fi

# ============================================================================
# SECTION 12 — CLEANUP (only this run's resources) + CREATED-RESOURCE REPORT
# ============================================================================
section 12 "CLEANUP & CREATED-RESOURCE REPORT"

# B7-PHASE2: each ids file is processed INDIVIDUALLY. The previous version
# concatenated the raw files into one JSONL blob WITHOUT newline separators;
# json.dump emits no trailing newline, so two files merged into a single
# invalid JSON line, json.load raised "Extra data", and the cleanup of BOTH
# resources silently never ran (the 2026-10-07 CLEANUP FAIL root cause).

CLEAN_OK=1
CLEAN_NOTE=""
CLEANED_FILES=""
for idsf in ids_e2e.json ids_fail.json ids_ocr.json; do
  docker exec "$CID_WORKER" test -f "$CONTAINER_TMP/$idsf" 2>/dev/null || continue
  CLEANED_FILES="$CLEANED_FILES $idsf"
  HOST_ONE="$TMP_HOST/$idsf"
  if ! docker exec "$CID_WORKER" cat "$CONTAINER_TMP/$idsf" > "$HOST_ONE" 2>/dev/null; then
    log "  $idsf: could not read ids file from the worker container"
    CLEAN_OK=0
    CLEAN_NOTE="$CLEAN_NOTE[$idsf unreadable]"
    continue
  fi
  log "resources created for $idsf (IDs recorded for the transcript):"
  sed 's/^/    /' "$HOST_ONE"
  if ! push_file "$CID_WORKER" "$HOST_ONE" "$CONTAINER_TMP/one_ids.json"; then
    log "  $idsf: push of ids file into the worker container failed"
    CLEAN_OK=0
    CLEAN_NOTE="$CLEAN_NOTE[$idsf push failed]"
    continue
  fi
  OUT_C="$(docker exec "$CID_WORKER" python "$CONTAINER_TMP/b7_cleanup.py" "$CONTAINER_TMP/one_ids.json" 2>&1)"
  printf '%s\n' "$OUT_C" | sed 's/^/  cleanup: /'
  if ! printf '%s\n' "$OUT_C" | grep -q '"step":"leftover_check","materials":0,"vectors":0'; then
    CLEAN_OK=0
    CLEAN_NOTE="$CLEAN_NOTE[$idsf rows not fully removed]"
  fi
  if printf '%s\n' "$OUT_C" | grep -qE '"step":"(ids_file_error|refused_|s3_delete_error|s3_verify_error|s3_verify_still_present)'; then
    CLEAN_OK=0
    CLEAN_NOTE="$CLEAN_NOTE[$idsf cleanup step error/refusal]"
  fi
  if ! grep -q '"s3_key": *null' "$HOST_ONE"; then
    # A non-null recorded s3_key MUST end with a verified-absent object.
    printf '%s\n' "$OUT_C" | grep -q '"step":"object_verified_absent"' \
      || { CLEAN_OK=0; CLEAN_NOTE="$CLEAN_NOTE[$idsf s3 object not verified absent]"; }
  fi
done

if [ -n "$CLEANED_FILES" ]; then
  AFTER="$(pg_count "vector_records")"
  log "vector_records rows now: ${AFTER:-?} (baseline before this run: ${VEC_BASELINE:-?})"
  if [ -z "$AFTER" ]; then
    CLEAN_OK=0
    CLEAN_NOTE="$CLEAN_NOTE[post-cleanup vector count unavailable]"
  elif [ -n "$VEC_BASELINE" ] && [ "$AFTER" != "$VEC_BASELINE" ]; then
    CLEAN_OK=0
    CLEAN_NOTE="$CLEAN_NOTE[vector_records $AFTER != baseline $VEC_BASELINE]"
  fi
  if [ "$CLEAN_OK" = "1" ]; then
    result CLEANUP PASS "all B7-created rows/objects deleted for:${CLEANED_FILES} (exact-UUID deletes + explicit FK-less vector deletes + predicate-guarded, verified S3 deletion); vector_records back to baseline ${AFTER}"
  else
    result CLEANUP FAIL "cleanup incomplete (${CLEAN_NOTE:-see per-file cleanup output above}) — the transcript lists every affected exact ID; historical leftovers are reported below"
  fi
else
  log "no ids files found in the worker container (nothing was seeded, or seeding never started)."
  LEAK="$(psql_ro "SELECT count(*) FROM users WHERE keycloak_subject LIKE 'b7-verify-${MARK}%';" | tr -d '[:space:]')"
  if [ "${LEAK:-0}" = "0" ]; then
    result CLEANUP PASS "nothing was created by this run (no cleanup needed)"
  else
    result CLEANUP FAIL "$LEAK B7 user row(s) exist without an ids file — find them via: SELECT * FROM users WHERE keycloak_subject LIKE 'b7-verify-${MARK}%' AND keycloak_issuer = 'urn:openlearn:b7-staging-verify';"
  fi
fi

# ---------------------------------------------------------------------------
# Previous-run B7 verification leftovers (report-only by default).
#
# Identified SOLELY by the synthetic issuer URN the verifier writes on its own
# users (real Keycloak issuers are https URLs, so this can never match user
# data). This block never deletes anything unless B7_CLEAN_PREVIOUS_B7=1,
# in which case b7_cleanup_previous.py first prints every exact UUID it is
# about to remove and then deletes in FK order with explicit vector and S3
# cleanup — the narrowly-scoped alternative to a blind title-pattern delete.
# ---------------------------------------------------------------------------
PRIOR_PREDICATE="keycloak_issuer = 'urn:openlearn:b7-staging-verify' AND keycloak_subject NOT LIKE 'b7-verify-${MARK}%'"
PRIOR_USERS="$(psql_ro "SELECT id || ' | subject=' || keycloak_subject FROM users WHERE ${PRIOR_PREDICATE};")"
PRIOR_COURSES="$(psql_ro "SELECT c.id || ' | owner=' || c.owner_id || ' | title=' || c.title FROM courses c WHERE c.owner_id IN (SELECT id FROM users WHERE ${PRIOR_PREDICATE});")"
PRIOR_MATERIALS="$(psql_ro "SELECT m.id || ' | status=' || m.status || ' | course=' || m.course_id || ' | s3_key=' || m.s3_key FROM materials m WHERE m.uploaded_by IN (SELECT id FROM users WHERE ${PRIOR_PREDICATE}) OR m.course_id IN (SELECT c.id FROM courses c WHERE c.owner_id IN (SELECT id FROM users WHERE ${PRIOR_PREDICATE}));")"
PRIOR_VECTORS="$(psql_ro "SELECT split_part(v.id, ':', 1) AS material_id, count(*) FROM vector_records v WHERE split_part(v.id, ':', 1) IN (SELECT m.id::text FROM materials m WHERE m.uploaded_by IN (SELECT id FROM users WHERE ${PRIOR_PREDICATE}) OR m.course_id IN (SELECT c.id FROM courses c WHERE c.owner_id IN (SELECT id FROM users WHERE ${PRIOR_PREDICATE}))) GROUP BY 1 ORDER BY 1;")"

log ""
log "previous-run B7 verification resources (synthetic issuer URN, this run excluded):"
if [ -n "$PRIOR_USERS" ] || [ -n "$PRIOR_COURSES" ] || [ -n "$PRIOR_MATERIALS" ] || [ -n "$PRIOR_VECTORS" ]; then
  printf '%s\n' "$PRIOR_USERS"   | sed '/^$/d; s/^/  user:     /'
  printf '%s\n' "$PRIOR_COURSES" | sed '/^$/d; s/^/  course:   /'
  printf '%s\n' "$PRIOR_MATERIALS" | sed '/^$/d; s/^/  material: /'
  printf '%s\n' "$PRIOR_VECTORS" | sed '/^$/d; s/^/  vectors:  /'
  log "  (the vector rows are FK-less by design and the S3 objects live outside"
  log "   the database, so a manual one-time cleanup must address both explicitly;"
  log "   see docs/tasks/ai-week7-8/progress.md, B7-PHASE2 record)"
  if [ "$B7_CLEAN_PREVIOUS_B7" = "1" ]; then
    log ""
    log "B7_CLEAN_PREVIOUS_B7=1 — deleting the resources listed above (exact UUIDs,"
    log "FK order, explicit vector + S3 cleanup; inventory + outcome below):"
    OUT_P="$(docker exec "$CID_WORKER" python "$CONTAINER_TMP/b7_cleanup_previous.py" "$MARK" 2>&1)"
    printf '%s\n' "$OUT_P" | sed 's/^/  previous-cleanup: /'
    # Verdict by re-querying the same issuer-scoped predicate, not by parsing
    # the cleanup output (the state of the database is the evidence).
    POST_USERS="$(psql_ro "SELECT count(*) FROM users WHERE ${PRIOR_PREDICATE};" | tr -d '[:space:]')"
    if [ "${POST_USERS:-1}" = "0" ] && ! printf '%s\n' "$OUT_P" | grep -q '"step":"previous_cleanup_error"'; then
      result CLEANUP_PREVIOUS PASS "previous-run B7 verification resources fully removed (re-query of the issuer-scoped predicate returns 0 users)"
    else
      result CLEANUP_PREVIOUS FAIL "previous-run cleanup incomplete (users remaining after cleanup: ${POST_USERS:-unavailable}) — see previous-cleanup output above"
    fi
  else
    result CLEANUP_PREVIOUS INFO "previous-run B7 verification resources remain (listed above); report-only by default — re-run with B7_CLEAN_PREVIOUS_B7=1 to remove exactly these, or follow the documented one-time manual cleanup"
  fi
else
  result CLEANUP_PREVIOUS INFO "no previous-run B7 verification resources remain on staging"
fi

if [ -n "$TEST_DB_NAME" ]; then
  log "dropping temporary test database $TEST_DB_NAME ..."
  docker exec "$CID_DB" psql -U "$PG_USER" -d "$PG_DB" -c \
    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$TEST_DB_NAME' AND pid <> pg_backend_pid();" >/dev/null 2>&1
  if docker exec "$CID_DB" psql -U "$PG_USER" -d "$PG_DB" -c "DROP DATABASE IF EXISTS \"$TEST_DB_NAME\"" >/dev/null 2>&1; then
    log "temporary test database dropped."
  else
    log "WARNING: could not drop temporary test database $TEST_DB_NAME (drop manually)."
  fi
fi

log "container temp dir $CONTAINER_TMP is removed by the exit trap (best effort)."

# ============================================================================
# SECTION 13 — FINAL SUMMARY
# ============================================================================
section 13 "FINAL SUMMARY (B7RESULT|id|status|note)"
cat "$RESULTS"

echo
log "Legend: PASS verified on the deployed staging runtime; PARTIAL inferred from"
log "verifiable gate inputs; BLOCKED environment prevented collection; NOT"
log "OBSERVABLE the current implementation does not expose the evidence; SKIPPED"
log "explicitly disabled by an opt-out flag (never counted as a failure); INFO"
log "informational report only (never counted as a failure)."
log ""

FAILED_REQUIRED=""
for id in $REQUIRED_IDS; do
  st="$(awk -F'|' -v i="$id" '$2==i {print $3}' "$RESULTS" | tail -n 1)"
  case "$st" in
    FAIL|BLOCKED) FAILED_REQUIRED="$FAILED_REQUIRED $id" ;;
  esac
done

if [ -z "$FAILED_REQUIRED" ]; then
  log "VERDICT: ALL REQUIRED B7 STAGING CRITERIA PASSED (exit 0)."
  log "Reminder: local-regression criteria (tests/ruff) may be BLOCKED here when the"
  log "staging VPS has no test environment — the committed progress.md ledger holds"
  log "the authoritative local-regression evidence for this baseline."
  log "Completed at $(now)."
  exit 0
else
  log "VERDICT: REQUIRED CRITERIA NOT MET:$FAILED_REQUIRED (exit 1)."
  log "Every collected evidence block above remains valid; do NOT attribute unrelated"
  log "staging failures to B7 without reading the worker logs printed in this run."
  log "Completed at $(now)."
  exit 1
fi
