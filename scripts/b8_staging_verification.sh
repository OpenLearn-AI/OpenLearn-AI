#!/usr/bin/env bash
# =============================================================================
# b8_staging_verification.sh
#
# OpenLearn-AI Week 7-8 / Batch B8 — Multi-PDF ingestion smoke (Week 8
# deliverable W3) — staging evidence collector and per-file results table.
#
# Authoritative B8 contract (roadmap Section 8, "B8 — Multi-PDF ingestion
# smoke", verified against the repository at implementation time):
#   * push 4-6 PDFs (born-digital + scanned; English + Arabic) through
#     upload -> worker on staging, using the experiments/OCR custom corpus;
#   * record PER FILE: final status, chunk count, vector rows, whether OCR
#     fired and on which pages;
#   * acceptance: all smoke PDFs reach `ready`, or each failure is explained;
#     the results table is complete;
#   * stop condition: a systematically failing category (e.g. all scanned
#     Arabic) is reported loudly for human analysis — the verifier never
#     tunes config and never retries mid-smoke;
#   * explicitly OUT of scope (W9+ / other batches): retrieval, RAG,
#     similarity search, quiz generation, graph generation, admin
#     reprocessing, chunk-QUALITY judgment (that is B9's review; B8 only
#     records the machine-verifiable evidence B9 feeds on), reasoning
#     gateway calls (B6/B7 scope), schema/migration changes.
#
# Fixture set (deterministic, from experiments/OCR/ocr-benchmark/data/raw/
# custom — characteristics per the corpus manifest.json):
#   en_born   1. English born-digital/  custom_custom_english_born_digital_001_p001.pdf   (en, born-digital)
#   ar_born   2. Arabic born-digital/   custom_custom_arabic_born_digital_001_p001.pdf    (ar, born-digital)
#   en_scan   3.English scanned/        custom_custom_english_scanned_004_p001.pdf        (en, scanned)
#   ar_mix    5. Arabic + English mixed/custom_custom_mixed_arabic_english_002_p001.pdf   (ar+en, scanned, multi-column)
#   B8_EXTRA_FIXTURES=1 additionally runs:
#   multicol  6. Multi-column/          custom_custom_multi_column_002_p001.pdf           (ar+en, scanned, multi-column)
#   tables    7. Tables/                custom_custom_tables_005_p001.pdf                 (en, scanned, tables)
# Corpus limitation recorded honestly (never silently substituted): the
# custom corpus contains NO Arabic-scanned PDFs (category "4. Arabic scanned"
# ships standalone images only, and the pipeline ingests PDFs), so the
# Arabic-scanned quadrant is covered by ar_mix, whose manifest categories
# include arabic_scanned.
#
# B7 verifier lessons deliberately carried forward (each one exists because
# the 2026-10-07 B7 staging runs hit the failure for real):
#   1. EXECUTION CONTEXT: every application-importing Python probe runs
#      through ONE helper (worker_py) that re-establishes the runtime-
#      equivalent import context inside the worker container (exec CWD =
#      detected image WORKDIR, PYTHONPATH = that directory, both PROVEN via
#      a side-effect-free `import app` check before any probe). A bare
#      `docker exec <worker> python /tmp/x.py` starts the interpreter with
#      the snippet's OWN directory at sys.path[0] — the CWD is never
#      searched — so `app` (not pip-installed, no ENV PYTHONPATH in the
#      image; the worker only resolves it because `celery -A` inserts its
#      process CWD) was unimportable and 12 probe sections died with
#      ModuleNotFoundError before any application check could run. When the
#      context cannot be established the helper REFUSES (rc=125) and the
#      affected checks are classified as verifier-execution failures, never
#      as application verdicts.
#   2. VERDICT SEMANTICS: PASS / FAIL / BLOCKED / NOT_OBSERVABLE / SKIPPED /
#      INFO are distinct. External provider conditions (HTTP 429 quota,
#      5xx upstream, timeouts) are BLOCKED, not FAIL; opt-in runs not taken
#      are NOT_OBSERVABLE/SKIPPED, never FAIL; the final exit code is
#      derived mechanically from the REQUIRED criteria only.
#   3. DATABASE CHECKS: ordered, schema-qualified (current_schema()) SQL,
#      per-probe return-code + stderr capture, per-sub-check attribution,
#      value-level checks on normalized PostgreSQL output only — no
#      unordered string_agg globs, no cross-schema matching, no discarded
#      psql exit codes.
#   4. CLEANUP: one ids file PER FIXTURE (single JSON object + trailing
#      newline — the B7 failure was two json.dump outputs concatenated
#      without a newline, merging into one invalid JSON line so cleanup
#      silently never ran); every delete is scoped to an exact recorded
#      UUID AND guarded by the B8 verification-resource predicate; FK-less
#      vector rows are deleted explicitly first; S3 deletion is verified
#      with head_object; the whole path is idempotent and safe to re-run.
#   5. NO SILENT INSTALLS: the staging VPS may have no backend test
#      environment. B8 requires NO test dependencies at all (no pytest, no
#      ruff — B8 is a runtime smoke, the local-regression evidence lives in
#      the committed progress.md ledger), so there is nothing to install
#      and no BLOCKED test section to fake. The verifier never pip-installs
#      anything.
#   6. SECRET HYGIENE: secret-valued env vars are reported SET/MISSING only;
#      the config report prints non-secret settings values only; the
#      evidence bundle is self-scanned for secret-shaped strings before it
#      is packed, and the scan result is part of the bundle.
#
# What THIS verifier creates on staging (nothing else):
#   * per fixture: one user, one course, one material, one MinIO object,
#     one Celery task — every resource carries the synthetic B8 verification
#     issuer URN / title prefix, is recorded in a per-fixture ids file, and
#     is deleted by the cleanup section (vectors first, then material,
#     course, user, then the verified S3 delete);
#   * /tmp/b8-staging-verify-<TS> on the host (working files + evidence dir)
#     and /tmp/b8-verify-<TS> inside the worker container (probe scripts,
#     fixture PDFs, ids files) — the container tmp is removed by the exit
#     trap; the host evidence dir and its tarball are KEPT for the ledger.
#
# Evidence bundle (kept, not deleted): $TMP_HOST/evidence/ holds the run
# metadata, repo/container/config snapshots (secrets redacted), the
# per-fixture smoke transcripts, the per-fixture worker-log windows (incl.
# the ocr_gate_evaluated / ocr_enrichment_applied events), DB probe
# outputs, the chunk samples + distribution artifact that feeds the B9
# chunk-quality review, the cleanup transcripts and the final verdict. At
# exit it is packed to /tmp/b8-verifier-evidence-<TS>.tar.gz whose SHA-256
# is printed; a secret-pattern self-scan runs before packing.
#
# Optional environment switches (defaults are the conservative values):
#   B8_SMOKE_TIMEOUT=480      seconds to wait per fixture for ready/failed
#   B8_EXTRA_FIXTURES=0       1 adds the multicol + tables fixtures (6 total,
#                             still inside the roadmap's 4-6 band)
#   B8_FIXTURES=              space-separated override of the fixture list
#                             (ids only: en_born ar_born en_scan ar_mix
#                             multicol tables); validated against the
#                             registry, never silently extended
#   B8_CLEAN_PREVIOUS_B8=0    1 additionally deletes resources left behind by
#                             PREVIOUS B8 verifier runs (identified solely by
#                             the synthetic B8 issuer URN, exact UUIDs
#                             printed before every delete). Default 0:
#                             previous leftovers are reported only.
#
# Run:   cd /path/to/OpenLearn-AI   &&   bash scripts/b8_staging_verification.sh
# (also works when copied elsewhere — it walks up to find the repo root)
# Exit codes: 0 = every REQUIRED B8 criterion PASS; 1 = at least one
# REQUIRED criterion FAIL/BLOCKED; 2 = preflight fatal (no docker/compose/
# repo root / invalid fixture override).
# =============================================================================

set -u

# ------------------------------------------------------------------ globals --
TS_EPOCH="$(date +%s)"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
TMP_HOST="/tmp/b8-staging-verify-${TS}"
EVID_DIR="${TMP_HOST}/evidence"
RESULTS="${TMP_HOST}/results.txt"
ROWS="${TMP_HOST}/rows.txt"
CONTAINER_TMP="/tmp/b8-verify-${TS}"
MARK="b8v${TS_EPOCH}"

B8_SMOKE_TIMEOUT="${B8_SMOKE_TIMEOUT:-480}"
B8_EXTRA_FIXTURES="${B8_EXTRA_FIXTURES:-0}"
B8_FIXTURES="${B8_FIXTURES:-}"
B8_CLEAN_PREVIOUS_B8="${B8_CLEAN_PREVIOUS_B8:-0}"

REQUIRED_TASK="app.workers.tasks.material_tasks.process_material"

ROOT=""
DOCKER_COMPOSE=""
CID_BACKEND="" CID_WORKER="" CID_DB="" CID_REDIS="" CID_LITELLM="" CID_MINIO=""
PG_USER="" PG_DB=""
VEC_BASELINE=""
WORKER_APPDIR=""        # application root inside the worker container (proven)
WORKER_PYPATH_BASE=""   # pre-existing container PYTHONPATH (prepended-to, never overwritten)
APP_CONTEXT_OK=0         # 1 once 'import app' is proven with the corrected context
CHUNK_SIZE_CFG="" CHUNK_OVERLAP_CFG=""

# ------------------------------------------------------------- fixture registry
# Paths are relative to the repository root; labels come from the corpus
# manifest (experiments/OCR/ocr-benchmark/data/raw/custom/manifest.json).
fix_path() {
  case "$1" in
    en_born)  printf '%s' "experiments/OCR/ocr-benchmark/data/raw/custom/1. English born-digital/custom_custom_english_born_digital_001_p001.pdf" ;;
    ar_born)  printf '%s' "experiments/OCR/ocr-benchmark/data/raw/custom/2. Arabic born-digital/custom_custom_arabic_born_digital_001_p001.pdf" ;;
    en_scan)  printf '%s' "experiments/OCR/ocr-benchmark/data/raw/custom/3.English scanned/custom_custom_english_scanned_004_p001.pdf" ;;
    ar_mix)   printf '%s' "experiments/OCR/ocr-benchmark/data/raw/custom/5. Arabic + English mixed/custom_custom_mixed_arabic_english_002_p001.pdf" ;;
    multicol) printf '%s' "experiments/OCR/ocr-benchmark/data/raw/custom/6. Multi-column/custom_custom_multi_column_002_p001.pdf" ;;
    tables)   printf '%s' "experiments/OCR/ocr-benchmark/data/raw/custom/7. Tables/custom_custom_tables_005_p001.pdf" ;;
    *) return 1 ;;
  esac
}
fix_cat() {
  case "$1" in
    en_born)  printf '%s' "English born-digital (slides-style page)" ;;
    ar_born)  printf '%s' "Arabic born-digital" ;;
    en_scan)  printf '%s' "English scanned" ;;
    ar_mix)   printf '%s' "Arabic+English mixed, multi-column, scanned" ;;
    multicol) printf '%s' "Arabic+English multi-column scanned slides" ;;
    tables)   printf '%s' "English scanned tables" ;;
    *) return 1 ;;
  esac
}
fix_lang() {
  case "$1" in
    en_born)            printf '%s' "en" ;;
    ar_born)            printf '%s' "ar" ;;
    en_scan)            printf '%s' "en" ;;
    ar_mix|multicol)    printf '%s' "ar+en" ;;
    tables)             printf '%s' "en" ;;
    *) return 1 ;;
  esac
}

# Resolve the fixture list: explicit override (validated) or default set.
FIX_LIST=""
if [ -n "$B8_FIXTURES" ]; then
  for f in $B8_FIXTURES; do
    if ! fix_path "$f" >/dev/null 2>&1; then
      printf '%s\n' "FATAL: unknown fixture id '$f' in B8_FIXTURES (valid: en_born ar_born en_scan ar_mix multicol tables)"
      exit 2
    fi
    FIX_LIST="$FIX_LIST $f"
  done
  FIX_LIST="${FIX_LIST# }"
else
  FIX_LIST="en_born ar_born en_scan ar_mix"
  [ "$B8_EXTRA_FIXTURES" = "1" ] && FIX_LIST="$FIX_LIST multicol tables"
fi

# REQUIRED verdict ids: the per-fixture ids are built from the resolved list,
# so the exit-code contract adapts to the run's fixture set mechanically.
SMOKE_IDS=""
for f in $FIX_LIST; do
  SMOKE_IDS="$SMOKE_IDS SMOKE_$(printf '%s' "$f" | tr '[:lower:]' '[:upper:]')"
done
REQUIRED_IDS="REPO_FIXTURES CONTAINERS WCONFIG WORKER_READY DB_READY$SMOKE_IDS CLEANUP"

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
  printf 'B8RESULT|%s|%s|%s\n' "$id" "$st" "$note" >> "$RESULTS"
  printf '[%s] %s — %s\n' "$st" "$id" "$note"
}
note() { printf '       %s\n' "$*"; }
evfile() { # evfile <name-under-evidence-dir>  (stdin -> evidence file + optional echo)
  cat > "${EVID_DIR}/$1"
}

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

worker_py() { # worker_py <timeout-seconds|0> <python-args...>
  # THE single execution path for Python probes that import application
  # modules inside the worker container (B7 lesson 1 — see header). Refuses
  # (rc=125) when the import context was not established so a doomed
  # ModuleNotFoundError can never masquerade as an application verdict.
  local tmo="${1:-0}"; shift
  if [ -z "$CID_WORKER" ] || [ -z "$WORKER_APPDIR" ]; then
    printf 'worker_py: application import context not established — probe NOT executed: python %s\n' "$*" >&2
    return 125
  fi
  local pyenv="$WORKER_APPDIR"
  [ -n "$WORKER_PYPATH_BASE" ] && pyenv="$WORKER_APPDIR:$WORKER_PYPATH_BASE"
  if [ "$tmo" -gt 0 ] 2>/dev/null; then
    timeout "$tmo" docker exec -w "$WORKER_APPDIR" -e PYTHONPATH="$pyenv" "$CID_WORKER" python "$@"
  else
    docker exec -w "$WORKER_APPDIR" -e PYTHONPATH="$pyenv" "$CID_WORKER" python "$@"
  fi
}

env_state() { # env_state <cid> <VARNAME> -> prints SET or MISSING (never the value)
  local cid="$1" var="$2"
  docker exec "$cid" sh -c "if [ -n \"\${${var}:-}\" ]; then echo SET; else echo MISSING; fi" 2>/dev/null || printf 'UNKNOWN'
}

grep_val() { # grep_val <file> <marker>  -> third pipe-field of "B8CFG|key|value"
  awk -F'|' -v k="$2" '$1=="B8CFG" && $2==k {print $3}' "$1" 2>/dev/null | head -n 1
}

grep_marker() { # grep_marker <file> <literal> -> 0 when present
  grep -qF -- "$2" "$1" 2>/dev/null
}

psql_ro() { # psql_ro <sql> (read-only usage only; runs inside the db container)
  docker exec "$CID_DB" psql -U "$PG_USER" -d "$PG_DB" -Atc "$1" 2>/dev/null
}

pg_count() { psql_ro "SELECT count(*) FROM ${1};" | tr -d '[:space:]'; }

dbq() { # dbq <sql> — capture output+rc into DBQ_OUT/DBQ_RC (B7 lesson 3: never discard)
  DBQ_OUT="$(psql_ro "$1")"
  DBQ_RC=$?
}

on_exit() {
  local rc=$?
  # Container temp dir: best-effort removal.
  if [ -n "${CID_WORKER:-}" ]; then
    docker exec "$CID_WORKER" rm -rf "$CONTAINER_TMP" >/dev/null 2>&1 || true
  fi
  # Evidence bundle: secret-pattern self-scan, tar, sha256. The bundle and
  # its tarball are KEPT (they are the deliverable this batch exists for).
  if [ -d "${EVID_DIR:-}" ]; then
    {
      echo "run_mark: $MARK"
      echo "completed_at_utc: $(now)"
      echo "exit_code: $rc"
      echo "results:"; cat "${RESULTS:-/dev/null}" 2>/dev/null
    } > "$EVID_DIR/final_verdict.txt" 2>/dev/null || true
    local hits hits_file
    hits_file="${TMP_HOST:-/tmp}/secret_scan.txt"
    { grep -rInE 'sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|BEGIN [A-Z ]*PRIVATE KEY|postgres(ql)?://[^[:space:]]*:[^[:space:]]*@|xox[baprs]-[A-Za-z0-9-]{10,}' "$EVID_DIR" 2>/dev/null || true; } > "$hits_file"
    hits="$(wc -l < "$hits_file" 2>/dev/null | tr -d ' ')"
    if [ "${hits:-0}" != "0" ]; then
      log "WARNING: $hits secret-shaped string(s) found in the evidence bundle — review before sharing:"
      sed 's/^/  SCAN: /' "$hits_file"
    else
      log "secret self-scan of the evidence bundle: 0 hits"
    fi
    cp "$hits_file" "$EVID_DIR/secret_scan_result.txt" 2>/dev/null || true
    local tarball="/tmp/b8-verifier-evidence-${TS}.tar.gz"
    if tar -czf "$tarball" -C "$TMP_HOST" evidence 2>/dev/null; then
      log "evidence bundle: $tarball (sha256 $(sha256sum "$tarball" 2>/dev/null | cut -d' ' -f1))"
    else
      log "WARNING: evidence tarball could not be created; the raw evidence dir remains at $EVID_DIR"
    fi
    log "raw evidence dir (kept): $EVID_DIR"
  fi
  exit "$rc"
}
trap on_exit EXIT

# ============================================================================
# SECTION 0 — PREFLIGHT
# ============================================================================
section 0 "PREFLIGHT"
mkdir -p "$TMP_HOST" "$EVID_DIR" "$EVID_DIR/fixtures"
: > "$RESULTS"
: > "$ROWS"

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
log "verifier: scripts/b8_staging_verification.sh (tracked, B8 multi-PDF ingestion smoke — Week 8 deliverable W3)"
log "host working dir: $TMP_HOST (evidence dir + tarball are KEPT)"
log "fixtures for this run:$FIX_LIST"
log "per-fixture ready/failed wait: ${B8_SMOKE_TIMEOUT}s"

{
  echo "run_mark: $MARK"
  echo "started_at_utc: $(now)"
  echo "verifier: scripts/b8_staging_verification.sh (B8 multi-PDF ingestion smoke)"
  echo "fixtures:$FIX_LIST"
  echo "B8_SMOKE_TIMEOUT: $B8_SMOKE_TIMEOUT"
  echo "B8_EXTRA_FIXTURES: $B8_EXTRA_FIXTURES"
  echo "B8_CLEAN_PREVIOUS_B8: $B8_CLEAN_PREVIOUS_B8"
} > "$EVID_DIR/run_meta.txt"

# ============================================================================
# SECTION 1 — REPOSITORY STATE + FIXTURE MANIFEST (read-only)
# ============================================================================
section 1 "REPOSITORY STATE + FIXTURE MANIFEST"
HEAD_SHA="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo 'not-a-git-worktree')"
BRANCH="$(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')"
SUBJECT="$(git -C "$ROOT" log -1 --format=%s 2>/dev/null || echo '?')"
DIRTY="$(git -C "$ROOT" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
log "branch:    $BRANCH"
log "HEAD:      $HEAD_SHA"
log "subject:   $SUBJECT"
log "dirty entries in worktree: $DIRTY (reported only; never touched by this script)"
{
  echo "branch: $BRANCH"
  echo "HEAD: $HEAD_SHA"
  echo "subject: $SUBJECT"
  echo "dirty_entries: $DIRTY"
} > "$EVID_DIR/repo_state.txt"

FIXTURES_OK=1
MISSING_FIXTURES=""
: > "$EVID_DIR/fixtures_manifest.txt"
log "fixture inventory (existence + content hash, read-only):"
for f in $FIX_LIST; do
  REL="$(fix_path "$f")"
  if [ -f "$ROOT/$REL" ] && [ -s "$ROOT/$REL" ]; then
    SZ="$(wc -c < "$ROOT/$REL" | tr -d ' ')"
    SHA="$(sha256sum "$ROOT/$REL" 2>/dev/null | cut -d' ' -f1)"
    log "  $f  ($(fix_lang "$f"))  ${SZ}B  sha256=${SHA:0:12}…  $REL"
    printf '%s|%s|%s|%s\n' "$f" "$(fix_lang "$f")" "$SZ" "$SHA" >> "$EVID_DIR/fixtures_manifest.txt"
  else
    log "  $f  MISSING: $REL"
    MISSING_FIXTURES="$MISSING_FIXTURES $f"
    FIXTURES_OK=0
  fi
done
log "corpus note: the experiments/OCR custom corpus ships NO Arabic-scanned PDFs"
log "(category '4. Arabic scanned' contains standalone images only); the Arabic-"
log "scanned quadrant is covered by ar_mix, whose manifest categories include"
log "arabic_scanned. Recorded as a corpus limitation — never silently substituted."

if [ "$FIXTURES_OK" = "1" ]; then
  result REPO_FIXTURES PASS "branch=$BRANCH HEAD=$HEAD_SHA; all $(printf '%s' "$FIX_LIST" | wc -w | tr -d ' ') smoke fixtures present with content hashes recorded (manifest in the evidence bundle)"
else
  result REPO_FIXTURES FAIL "missing/empty fixture(s):$MISSING_FIXTURES — the multi-PDF smoke cannot run as specified; no silent substitution is performed"
fi

# ============================================================================
# SECTION 2 — CONTAINER DISCOVERY & HEALTH + APPLICATION IMPORT CONTEXT
# ============================================================================
section 2 "CONTAINER DISCOVERY & HEALTH + APPLICATION IMPORT CONTEXT"
log "compose ps (as deployed):"
dcompose ps 2>/dev/null | sed 's/^/  /' || note "(compose ps produced no output)"
dcompose ps 2>/dev/null > "$EVID_DIR/compose_ps.txt" || true

for svc in backend celery_worker celery_beat db redis litellm minio; do
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

if [ -n "$MISSING" ]; then
  result CONTAINERS FAIL "required containers not found:$MISSING (compose project discovery failed)"
else
  WS="$(state_of "$CID_WORKER")"; BS="$(state_of "$CID_BACKEND")"
  if [ "$WS" = "running" ] && [ "$BS" = "running" ]; then
    result CONTAINERS PASS "worker=$WS backend=$BS db/redis/minio present (worker container: $(docker inspect -f '{{.Name}}' "$CID_WORKER" 2>/dev/null | tr -d '/'))"
  else
    result CONTAINERS FAIL "worker state=$WS backend state=$BS (expected running)"
  fi
fi

if [ -n "$CID_DB" ]; then
  PG_USER="$(docker exec "$CID_DB" printenv POSTGRES_USER 2>/dev/null || printf 'postgres')"
  PG_DB="$(docker exec "$CID_DB" printenv POSTGRES_DB 2>/dev/null || printf 'postgres')"
  log "db user/database (non-secret): $PG_USER / $PG_DB"
fi

# ---- Application import context (worker_py) — B7 lesson 1 -------------------
# Detect — never guess — the application root inside the worker container,
# prove that it holds the app package, and prove that `import app` works with
# the runtime-equivalent context BEFORE any probe runs. The proof probe is
# side-effect free: backend/app/__init__.py is empty.
if [ -n "$CID_WORKER" ]; then
  DEFDIR="$(docker exec "$CID_WORKER" sh -c 'pwd' 2>/dev/null | tr -d '[:space:]' || true)"
  CAND=""
  for d in "$DEFDIR" /app; do
    [ -n "$d" ] || continue
    if docker exec -w "$d" "$CID_WORKER" test -f ./app/__init__.py >/dev/null 2>&1; then
      CAND="$d"; break
    fi
  done
  if [ -n "$CAND" ]; then
    WORKER_APPDIR="$CAND"
    WORKER_PYPATH_BASE="$(docker exec "$CID_WORKER" sh -c 'printf %s "${PYTHONPATH:-}"' 2>/dev/null || true)"
    if APP_IMPORT_ERR="$(worker_py 0 -c 'import app' 2>&1)"; then
      APP_CONTEXT_OK=1
      log "application import context: OK (exec CWD=$WORKER_APPDIR; base container PYTHONPATH: ${WORKER_PYPATH_BASE:-<none>}; 'import app' proven — probes below run in the runtime-equivalent context)"
      result APP_CONTEXT PASS "verifier established the application import context inside the worker container (exec CWD=$WORKER_APPDIR + PYTHONPATH; 'import app' proven before any probe) — application-level results below are real runtime verdicts"
    else
      log "WARNING: 'import app' failed even with the corrected execution context (CWD=$WORKER_APPDIR, PYTHONPATH=$WORKER_APPDIR):"
      printf '%s\n' "$APP_IMPORT_ERR" | tail -n 5 | sed 's/^/  /'
      log "This is an image-level import problem (the deployed image cannot import its own app package), NOT a verifier execution defect and NOT a probe verdict."
    fi
  else
    log "WARNING: no directory holding the app package was found in the worker container (default exec CWD=${DEFDIR:-<unavailable>}; the /app fallback failed as well)."
    log "Every application-importing probe will REFUSE to execute (rc=125) instead of failing with a misleading ModuleNotFoundError."
  fi
  if [ "$APP_CONTEXT_OK" != "1" ]; then
    result APP_CONTEXT WARN "application import context NOT established — every application-importing probe result in this run is a VERIFIER-EXECUTION failure, not an application verdict"
  fi
fi

# ============================================================================
# SECTION 3 — PIPELINE CONFIGURATION (non-secret values; B8-relevant subset)
# ============================================================================
section 3 "PIPELINE CONFIGURATION (non-secret values)"

if [ -z "$CID_WORKER" ]; then
  result WCONFIG FAIL "worker container not found; configuration not observable"
else
  log "Secret-valued variables (SET/MISSING only — values are never printed):"
  for v in GEMINI_API_KEY SENTRY_DSN REDIS_PASSWORD DATABASE_URL S3_SECRET_ACCESS_KEY; do
    log "  worker $v: $(env_state "$CID_WORKER" "$v")"
  done

  cat > "$TMP_HOST/b8_config_report.py" <<'PY'
from app.config import settings

pairs = [
    ("ai_embedding_provider", settings.ai_embedding_provider),
    ("ai_embedding_model", settings.ai_embedding_model),
    ("ai_embedding_dimension", settings.ai_embedding_dimension),
    ("ai_embedding_device", settings.ai_embedding_device),
    ("ai_vector_db_provider", settings.ai_vector_db_provider),
    ("ai_ocr_provider", settings.ai_ocr_provider),
    ("ai_ocr_model", settings.ai_ocr_model),
    ("ocr_min_text_chars", settings.ocr_min_text_chars),
    ("chunk_size", settings.chunk_size),
    ("chunk_overlap", settings.chunk_overlap),
    ("environment", settings.environment),
]
for k, v in pairs:
    print(f"B8CFG|{k}|{v}")
PY
  if push_file "$CID_WORKER" "$TMP_HOST/b8_config_report.py" "$CONTAINER_TMP/b8_config_report.py" \
     && worker_py 0 "$CONTAINER_TMP/b8_config_report.py" > "$TMP_HOST/config.txt" 2>&1; then
    sed 's/^/  /' "$TMP_HOST/config.txt"
    cp "$TMP_HOST/config.txt" "$EVID_DIR/config_report.txt"
    EMB_P="$(grep_val "$TMP_HOST/config.txt" ai_embedding_provider)"
    EMB_D="$(grep_val "$TMP_HOST/config.txt" ai_embedding_dimension)"
    EMB_M="$(grep_val "$TMP_HOST/config.txt" ai_embedding_model)"
    VDB_P="$(grep_val "$TMP_HOST/config.txt" ai_vector_db_provider)"
    OCR_P="$(grep_val "$TMP_HOST/config.txt" ai_ocr_provider)"
    OCR_M="$(grep_val "$TMP_HOST/config.txt" ai_ocr_model)"
    OCR_THR="$(grep_val "$TMP_HOST/config.txt" ocr_min_text_chars)"
    CHUNK_SIZE_CFG="$(grep_val "$TMP_HOST/config.txt" chunk_size)"
    CHUNK_OVERLAP_CFG="$(grep_val "$TMP_HOST/config.txt" chunk_overlap)"
    GKEY_SET="$(env_state "$CID_WORKER" GEMINI_API_KEY)"
    log "B8 contract relevance: the smoke exercises ingest -> targeted OCR gate ->"
    log "chunk -> BGE-M3 embed -> pgvector persist; the reasoning gateway (litellm)"
    log "is B6/B7 scope and is deliberately NOT exercised by B8. Expected per"
    log "infra/docker-compose.staging.yml: embedding=bge-m3/1024/BAAI-bge-m3,"
    log "vector=postgres, ocr=gemini, GEMINI_API_KEY set; chunk/ocr thresholds are"
    log "recorded (repo defaults 1200/150/50) for the per-fixture table."
    if [ "$EMB_P" = "bge-m3" ] && [ "$EMB_D" = "1024" ] && [ "$EMB_M" = "BAAI/bge-m3" ] \
       && [ "$VDB_P" = "postgres" ] && [ "$OCR_P" = "gemini" ] \
       && [ "$GKEY_SET" = "SET" ] && [ -n "$OCR_THR" ] && [ "$OCR_THR" -gt 0 ] 2>/dev/null; then
      result WCONFIG PASS "worker pipeline configuration matches the B8 smoke contract (embedding=bge-m3/1024, vector=postgres, ocr=gemini/${OCR_M:-?} with GEMINI_API_KEY set, ocr_min_text_chars=${OCR_THR}); chunk_size=${CHUNK_SIZE_CFG:-?} chunk_overlap=${CHUNK_OVERLAP_CFG:-?} recorded for the results table"
    else
      result WCONFIG FAIL "worker pipeline configuration deviates from the B8 smoke contract: embedding=$EMB_P/$EMB_D/$EMB_M vector=$VDB_P ocr=$OCR_P GEMINI_API_KEY=$GKEY_SET ocr_min_text_chars=${OCR_THR:-?}"
    fi
  else
    sed 's/^/  /' "$TMP_HOST/config.txt" 2>/dev/null
    if grep -q 'probe NOT executed' "$TMP_HOST/config.txt" 2>/dev/null; then
      result WCONFIG BLOCKED "config probe REFUSED (rc=125): application import context not established — verifier-execution limitation, NOT an application verdict"
    else
      result WCONFIG FAIL "could not execute the config-report snippet inside the worker container"
    fi
  fi
fi

# ============================================================================
# SECTION 4 — CELERY WORKER READINESS, REGISTERED TASK
# ============================================================================
section 4 "CELERY WORKER READINESS"
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
fi

# ============================================================================
# SECTION 5 — DATABASE PREREQUISITES (read-only; B7 DB lessons applied)
# ============================================================================
section 5 "DATABASE PREREQUISITES (read-only)"
# Compact prerequisite for the per-fixture vector evidence: the vector_records
# table (current schema, ordered, per-column rc-captured) and pgvector's
# vector_dims. The FULL B7 schema verification (constraint, alembic head
# match, wrong-dimension scan) already passed on this staging baseline and
# stays B7's criterion — this section only guards B8's own evidence path.
if [ -z "$CID_DB" ]; then
  result DB_READY FAIL "db container not found"
else
  DB_PREREQ_OK=1
  DB_EVIDENCE_ERROR=0
  log "vector_records pinned column/type presence (current_schema, each row must be 1):"
  for pair in id:text embedding:vector content:text metadata:jsonb; do
    col="${pair%%:*}"; typ="${pair##*:}"
    dbq "SELECT count(*) FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = 'vector_records' AND column_name = '$col' AND udt_name = '$typ';"
    val="$(printf '%s' "$DBQ_OUT" | tr -d '[:space:]')"
    log "  $col:$typ -> ${val:-<empty>} (rc=$DBQ_RC)"
    if [ "$DBQ_RC" != "0" ] || [ -z "$val" ]; then
      DB_EVIDENCE_ERROR=1; DB_PREREQ_OK=0
    elif [ "$val" != "1" ]; then
      DB_PREREQ_OK=0
    fi
  done
  log "pgvector vector_dims availability (pg_proc):"
  dbq "SELECT count(*) FROM pg_proc WHERE proname = 'vector_dims';"
  VD_CNT="$(printf '%s' "$DBQ_OUT" | tr -d '[:space:]')"
  log "  vector_dims entries: ${VD_CNT:-<empty>} (rc=$DBQ_RC)"
  if [ "$DBQ_RC" != "0" ] || [ -z "$VD_CNT" ]; then
    DB_EVIDENCE_ERROR=1; DB_PREREQ_OK=0
  elif [ "$VD_CNT" = "0" ]; then
    DB_PREREQ_OK=0
  fi
  if [ "$DB_EVIDENCE_ERROR" = "1" ]; then
    result DB_READY BLOCKED "evidence collection failed (a psql probe returned an error or empty result — see rc= markers above); per-fixture vector evidence would be unverifiable"
  elif [ "$DB_PREREQ_OK" = "1" ]; then
    result DB_READY PASS "vector_records present in the current schema with the pinned column/types; pgvector vector_dims available (prerequisite for per-fixture vector evidence)"
  else
    result DB_READY FAIL "vector_records/vector_dims prerequisite not satisfied — the failing sub-checks are individually marked above"
  fi
fi

# ============================================================================
# SECTION 6 — MULTI-PDF SMOKE (the core B8 evidence; one fixture at a time)
# ============================================================================
section 6 "MULTI-PDF SMOKE (sequential, one fixture at a time)"
log "Each fixture runs the REAL production seam exactly like B7's E2E did:"
log "  seed user/course -> upload object -> register material (pending) ->"
log "  celery send_task -> storage fetch -> Docling ingest -> targeted OCR gate"
log "  -> chunk -> BGE-M3 embed -> pgvector upsert -> ready"
log "Fixtures run SEQUENTIALLY (never concurrent): worker-log evidence stays"
log "attributable per fixture and no configuration is touched mid-smoke."

cat > "$TMP_HOST/b8_smoke_run.py" <<'PY'
"""Seed user/course/material, upload ONE fixture PDF, enqueue, poll, verify.

Runs INSIDE the worker container using the application's own code paths
(app.services.material_service, app.services.storage._s3_client,
app.workers.publishing.enqueue_material_processing) — the same proven seam
the B7 E2E used. Only this script's own uniquely-marked rows are touched;
deletion happens in b8_cleanup.py.

The ids file is written EARLY (user+course) and rewritten after
registration, so a later crash can never leak untracked rows. It ends with
a trailing newline (the B7 cleanup failure was concatenated JSON without
newline separators); the shell processes ONE file PER FIXTURE — files are
never concatenated.
"""
import asyncio
import json
import sys
import time
from pathlib import Path
from uuid import UUID

MARK = sys.argv[1]
FIXTURE_ID = sys.argv[2]
PDF_PATH = sys.argv[3]
TIMEOUT_S = float(sys.argv[4])
IDS_FILE = sys.argv[5]

B8_ISSUER = "urn:openlearn:b8-staging-verify"


def out(step, **kw):
    print("B8E2E|" + json.dumps({"step": step, **kw}, separators=(",", ":"), default=str, ensure_ascii=False), flush=True)


async def main():
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from app.config import settings
    from app.models.course import Course
    from app.models.material import Material
    from app.models.user import User
    from app.models.vector_record import VectorRecordModel
    from app.services.material_service import build_material_s3_key, create_material
    from app.services.storage import _s3_client
    from app.workers.publishing import enqueue_material_processing

    engine = create_async_engine(settings.database_url)
    maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    subject = f"b8-verify-{MARK}-{FIXTURE_ID}"
    title = f"B8 staging verification {MARK}-{FIXTURE_ID}"

    user_id = course_id = material_id = s3_key = job_id = None
    try:
        async with maker() as session:
            user = User(
                keycloak_issuer=B8_ISSUER,
                keycloak_subject=subject,
                email=f"{subject}@b8-verify.invalid",
                email_verified=False,
                settings={},
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            user_id = str(user.id)

            course = Course(owner_id=user.id, title=title)
            session.add(course)
            await session.commit()
            await session.refresh(course)
            course_id = str(course.id)
        out("seeded", fixture=FIXTURE_ID, user_id=user_id, course_id=course_id)

        # Persist ids EARLY so a later crash can never leak untracked rows.
        with open(IDS_FILE, "w") as fh:
            json.dump({"fixture": FIXTURE_ID, "mark": MARK, "user_id": user_id,
                       "course_id": course_id, "material_id": None,
                       "s3_key": None, "job_id": None}, fh, ensure_ascii=False)
            fh.write("\n")

        s3_key = build_material_s3_key(UUID(course_id), Path(PDF_PATH).name)
        body = Path(PDF_PATH).read_bytes()
        _s3_client().put_object(
            Bucket=settings.s3_bucket_name,
            Key=s3_key,
            Body=body,
            ContentType="application/pdf",
        )
        out("object_uploaded", s3_key=s3_key, bytes=len(body))

        async with maker() as session:
            material = await create_material(
                session,
                course_id=UUID(course_id),
                title=title,
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
            json.dump({"fixture": FIXTURE_ID, "mark": MARK, "user_id": user_id,
                       "course_id": course_id, "material_id": material_id,
                       "s3_key": s3_key, "job_id": job_id}, fh, ensure_ascii=False)
            fh.write("\n")

        # Poll the material status exactly like an observer would.
        from app.models.vector_record import VectorRecordModel as VRM

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
                    select(VRM).where(VRM.id.like(f"{material_id}:%"))
                )
            ).scalars().all()
            out("vector_count", count=len(vrows))
            expected_dim = int(settings.ai_embedding_dimension)
            expected_doc_id = Path(PDF_PATH).stem  # pushed under its ORIGINAL basename
            ok_dims = len(vrows) > 0
            ok_prov = len(vrows) > 0
            ok_norm = len(vrows) > 0
            ok_content = len(vrows) > 0
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
                    content_preview=(r.content or "")[:80],
                )
                if len(vec) != expected_dim:
                    ok_dims = False
                if not any(abs(x) > 1e-6 for x in vec):
                    ok_dims = False
                if len(r.content or "") == 0:
                    ok_content = False
                if meta.get("material_id") != material_id:
                    ok_prov = False
                # document_id is derived from the DOWNLOADED object's basename,
                # which is the s3 key's basename: "<uuid4>-<original-stem>".
                # The stable, machine-verifiable invariant is the suffix: the
                # recorded document_id must end with the original fixture stem.
                if not str(meta.get("document_id") or "").endswith(expected_doc_id):
                    ok_prov = False
                if not meta.get("chunk_id") or meta.get("pages") is None:
                    ok_prov = False
                if not (0.95 <= norm <= 1.05):
                    ok_norm = False
            out("expected_document_id", value=expected_doc_id)
            lifecycle_ok = (
                initial_status == "pending"
                and last == "ready"
                and "processing" in seen
            )
            out("verdict_lifecycle", ok=bool(lifecycle_ok), final=str(last), transitions=json.dumps(seen))
            out("verdict_vectors", ok=bool(ok_dims and ok_content), count=len(vrows), required_dimension=expected_dim)
            out("verdict_provenance", ok=bool(ok_prov))
            out("verdict_bge_discrim", ok=bool(ok_norm), note="norm~1.0=BGE-M3 L2-normalized; norm~0.0 would be the mock provider")
    finally:
        await engine.dispose()


asyncio.run(main())
PY

push_file "$CID_WORKER" "$TMP_HOST/b8_smoke_run.py" "$CONTAINER_TMP/b8_smoke_run.py" || true

if [ -z "$CID_WORKER" ] || [ -z "$CID_MINIO" ]; then
  for f in $FIX_LIST; do
    result "SMOKE_$(printf '%s' "$f" | tr '[:lower:]' '[:upper:]')" FAIL "worker/minio container not found; smoke not attempted for $f"
  done
else
  VEC_BASELINE="$(pg_count "vector_records")"
  log "pre-existing vector_records rows (baseline, read-only count): ${VEC_BASELINE:-?}"
fi

for f in $FIX_LIST; do
  [ -n "$CID_WORKER" ] && [ -n "$CID_MINIO" ] || break
  REL="$(fix_path "$f")"
  FIXSTEM="$(basename "$REL" .pdf)"
  FID_UP="$(printf '%s' "$f" | tr '[:lower:]' '[:upper:]')"
  RID="SMOKE_${FID_UP}"
  TR="$TMP_HOST/smoke_${f}.txt"

  echo
  log "---- fixture $f [$(fix_cat "$f")] lang=$(fix_lang "$f") ----"
  log "  source: $REL"

  if [ "$APP_CONTEXT_OK" != "1" ]; then
    result "$RID" BLOCKED "application import context not established — the smoke probe was REFUSED (rc=125) before touching the pipeline; this is a verifier-execution limitation, NOT an application verdict (see APP_CONTEXT above)"
    continue
  fi

  if ! push_file "$CID_WORKER" "$ROOT/$REL" "$CONTAINER_TMP/$(basename "$REL")"; then
    result "$RID" BLOCKED "could not push the fixture PDF into the worker container (docker exec failure) — environment limitation, no application verdict"
    continue
  fi

  IDSF="$CONTAINER_TMP/ids_${f}.json"
  docker exec "$CID_WORKER" rm -f "$IDSF" >/dev/null 2>&1
  WSTART="$(date +%s)"

  worker_py "$((B8_SMOKE_TIMEOUT + 90))" "$CONTAINER_TMP/b8_smoke_run.py" \
    "$MARK" "$f" "$CONTAINER_TMP/$(basename "$REL")" "$B8_SMOKE_TIMEOUT" "$IDSF" > "$TR" 2>&1
  RC=$?
  grep -E '^B8E2E\|' "$TR" | sed 's/^/  /'
  cp "$TR" "$EVID_DIR/fixtures/smoke_${f}.txt" 2>/dev/null || true

  if [ "$RC" = "125" ]; then
    result "$RID" BLOCKED "smoke probe REFUSED (rc=125): application import context lost mid-run — verifier-execution limitation, NOT an application verdict"
    continue
  fi
  if [ "$RC" = "124" ]; then
    result "$RID" BLOCKED "smoke probe exceeded the verifier timeout (${B8_SMOKE_TIMEOUT}s + overhead) — environment/worker limitation; increase B8_SMOKE_TIMEOUT and re-run; no application verdict"
    continue
  fi
  if [ "$RC" != "0" ]; then
    log "(probe rc=$RC — last raw lines for diagnosis:)"
    tail -n 12 "$TR" | sed 's/^/  /'
    result "$RID" BLOCKED "smoke probe failed to complete (rc=$RC, e.g. database/redis/storage unreachable) — environment/verifier limitation, NOT an application verdict; evidence above"
    continue
  fi

  FINAL="$(sed -n 's/.*"step":"final_status","status":"\([a-z_]*\)".*/\1/p' "$TR" | tail -n1)"
  VEC_N="$(grep -oE '"step":"vector_count","count":[0-9]+' "$TR" | tail -n1 | grep -oE '[0-9]+$')"
  MID="$(sed -n 's/.*"step":"registered","status":"pending","material_id":"\([^"]*\)".*/\1/p' "$TR" | head -n1)"
  JOB="$(sed -n 's/.*"step":"enqueued","job_id":"\([^"]*\)".*/\1/p' "$TR" | head -n1)"
  LIFECYCLE_OK=0; VEC_OK=0; PROV_OK=0; NORM_OK=0
  grep_marker "$TR" '"step":"verdict_lifecycle","ok":true'        && LIFECYCLE_OK=1
  grep_marker "$TR" '"step":"verdict_vectors","ok":true'          && VEC_OK=1
  grep_marker "$TR" '"step":"verdict_provenance","ok":true'       && PROV_OK=1
  grep_marker "$TR" '"step":"verdict_bge_discrim","ok":true'      && NORM_OK=1

  # Worker-log window for exactly this fixture (filtered, bounded) — saved
  # BEFORE verdict classification so evidence and verdict always agree.
  WLOG="$EVID_DIR/fixtures/workerlog_${f}.txt"
  docker logs --since "$WSTART" "$CID_WORKER" 2>&1 \
    | grep -E "material_id=${MID:-__none__}|document_id=${FIXSTEM}|ocr_gate_evaluated|ocr_enrichment_applied|material_processing_failed|raised unexpected|Task .*${JOB:-__none__}" \
    > "$WLOG" 2>/dev/null || true
  tail -n 60 "$WLOG" | sed 's/^/  log| /'

  CHUNK_N="$(grep -F 'material_content_processed' "$WLOG" 2>/dev/null | grep -F "$MID" | grep -oE 'chunk_count=[0-9]+' | head -n1 | grep -oE '[0-9]+$')"
  GATE_N="$(grep -F "$FIXSTEM" "$WLOG" 2>/dev/null | grep -cF 'ocr_gate_evaluated' || true)"
  APPLIED_N="$(grep -F "$FIXSTEM" "$WLOG" 2>/dev/null | grep -cF 'ocr_enrichment_applied' || true)"
  OCR_PAGES="$(grep -F "$FIXSTEM" "$WLOG" 2>/dev/null | grep -F 'ocr_enrichment_applied' | grep -oE "'page': [0-9]+" | grep -oE '[0-9]+' | sort -un | tr '\n' ',' | sed 's/,$//')"
  if [ "${GATE_N:-0}" -gt 0 ] 2>/dev/null; then
    log "  OCR gate events for this fixture: ${GATE_N}; enrichment events: ${APPLIED_N}; OCR-fired pages: ${OCR_PAGES:-none}"
  else
    log "  OCR gate events: none found in this fixture's worker-log window — the deployed image may predate the B7-PHASE2 OCR logging; per-fixture OCR firing is recorded as not observable"
  fi

  VERDICT=""; VNOTE=""
  if [ "$FINAL" = "ready" ] && [ "$LIFECYCLE_OK" = "1" ] && [ "$VEC_OK" = "1" ] && [ "$PROV_OK" = "1" ] && [ "$NORM_OK" = "1" ]; then
    VERDICT="PASS"
    VNOTE="fixture '$f' reached ready through the real Celery task (lifecycle+1024-dim non-zero non-empty vectors+provenance with document_id ending in '${FIXSTEM}'+BGE-M3 norms all ok); chunks=${CHUNK_N:-?} vectors=${VEC_N:-?}; OCR fired on pages: ${OCR_PAGES:-none}${APPLIED_N:+ ($APPLIED_N enrichment event(s))}"
  elif [ "$FINAL" = "failed" ]; then
    if [ -n "$(grep -Ei 'ProviderRateLimitError|Error code: 429|RateLimit|quota|ProviderServerError|ServiceUnavailable|Error code: 503|GeminiException|ProviderTimeoutError|ProviderUnavailableError' "$WLOG" 2>/dev/null)" ]; then
      VERDICT="BLOCKED"
      VNOTE="fixture '$f' ended 'failed' with an EXTERNAL provider failure in this window (upstream OCR/embedding quota or availability — marker lines in the evidence above); external runtime limitation, NOT an application failure; re-run this fixture when the upstream recovers"
    elif [ -n "$(grep -F 'material_processing_failed' "$WLOG" 2>/dev/null)" ]; then
      VERDICT="FAIL"
      VNOTE="fixture '$f' ended 'failed' with a NON-external cause (no upstream provider marker in the window) — application/deployment defect suspected; worker-log window saved for analysis"
    else
      VERDICT="BLOCKED"
      VNOTE="fixture '$f' ended 'failed' but the worker-log window has no attributable failure line — inconclusive; treated as environment-limited (full transcript + window saved)"
    fi
  elif [ "$FINAL" = "processing" ] || [ "$FINAL" = "pending" ]; then
    VERDICT="BLOCKED"
    VNOTE="fixture '$f' still '${FINAL}' after ${B8_SMOKE_TIMEOUT}s (worker may be slow or wedged — check the evidence window; increase B8_SMOKE_TIMEOUT and re-run); no application verdict"
  elif [ "$FINAL" = "ready" ]; then
    VERDICT="FAIL"
    VNOTE="fixture '$f' reached ready but machine-verifiable evidence is incomplete: lifecycle=$LIFECYCLE_OK vectors=$VEC_OK provenance=$PROV_OK norms=$NORM_OK — see B8E2E verdict lines above"
  else
    VERDICT="FAIL"
    VNOTE="fixture '$f' ended in unexpected state final='${FINAL:-<none>}' (rc=$RC) — see transcript above"
  fi
  result "$RID" "$VERDICT" "$VNOTE"

  printf 'B8ROW|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n' \
    "$f" "$(fix_lang "$f")" "${FINAL:-?}" "${CHUNK_N:-?}" "${VEC_N:-?}" \
    "$([ "$VEC_OK" = "1" ] && printf ok || printf NO)" \
    "$([ "$NORM_OK" = "1" ] && printf ok || printf NO)" \
    "$([ "$PROV_OK" = "1" ] && printf ok || printf NO)" \
    "$([ "${GATE_N:-0}" -gt 0 ] 2>/dev/null && { [ "${APPLIED_N:-0}" -gt 0 ] 2>/dev/null && printf 'fired:%s' "${OCR_PAGES:-?}" || printf 'skipped'; } || printf '?')" \
    "$OCR_PAGES" "$VERDICT" >> "$ROWS"
done

# ============================================================================
# SECTION 7 — RESULTS TABLE + CHUNK EVIDENCE (feeds the B9 chunk-quality review)
# ============================================================================
section 7 "RESULTS TABLE + CHUNK EVIDENCE (B9 feed)"

if [ -s "$ROWS" ]; then
  log "Per-file smoke results table (B8 deliverable — the authoritative copy is"
  log "in the evidence bundle; paste this into docs/tasks/ai-week7-8/progress.md):"
  log ""
  printf '  %-9s %-6s %-10s %-7s %-7s %-5s %-5s %-5s %-10s %-9s\n' FIXTURE LANG STATUS CHUNKS VECTORS VEC NORM PROV OCR VERDICT
  printf '  %-9s %-6s %-10s %-7s %-7s %-5s %-5s %-5s %-10s %-9s\n' ------- ------ ---------- ------- ------- ----- ----- ----- ---------- ---------
  while IFS='|' read -r _tag r_f r_l r_s r_c r_v r_vec r_norm r_prov r_ocr r_pages r_ver; do
    printf '  %-9s %-6s %-10s %-7s %-7s %-5s %-5s %-5s %-10s %-9s\n' \
      "$r_f" "$r_l" "$r_s" "$r_c" "$r_v" "$r_vec" "$r_norm" "$r_prov" "$r_ocr" "$r_ver"
  done < "$ROWS"
  log ""
  log "machine-readable rows (B8ROW|fixture|lang|final_status|chunks|vectors|vec|norm|prov|ocr|ocr_pages|verdict):"
  cat "$ROWS"
  { printf 'B8 per-file smoke results — run %s (%s)\n' "$MARK" "$(now)"
    printf 'fixture|lang|final_status|chunks|vectors|vec_ok|norm_ok|prov_ok|ocr|ocr_pages|verdict\n'
    cat "$ROWS"; } > "$EVID_DIR/results_table.txt"
else
  log "(no per-fixture rows were produced — smoke did not run)"
fi

# ---- chunk samples + distribution (B9 feed; machine-verifiable facts only) --
# B8 records the evidence; the QUALITY judgment is B9's human review. The
# chunker's own invariant (every chunk <= chunk_size by construction) means a
# char_count above chunk_size would indicate a real defect and is counted
# here; no semantic quality claim is made either way.
CHUNK_SAMPLES="$EVID_DIR/chunk_samples.txt"
: > "$CHUNK_SAMPLES"
{
  printf 'B8 chunk samples + per-fixture char_count distribution — run %s (%s)\n' "$MARK" "$(now)"
  printf 'Purpose: input for the B9 chunk-quality review. Samples are representative,\n'
  printf 'NOT a quality score. Distribution numbers are machine-verifiable facts.\n'
} > "$CHUNK_SAMPLES"
log ""
log "chunk evidence per fixture (samples + char_count distribution; full text in vector content):"
for f in $FIX_LIST; do
  TR="$TMP_HOST/smoke_${f}.txt"
  [ -f "$TR" ] || continue
  COUNTS="$(grep -oE '"metadata_char_count":[0-9]+' "$TR" 2>/dev/null | grep -oE '[0-9]+$')"
  [ -n "$COUNTS" ] || continue
  N="$(printf '%s\n' "$COUNTS" | wc -l | tr -d ' ')"
  MIN="$(printf '%s\n' "$COUNTS" | sort -n | head -n1)"
  MAX="$(printf '%s\n' "$COUNTS" | sort -n | tail -n1)"
  GIANTS=0
  if [ -n "${CHUNK_SIZE_CFG:-}" ] && [ "$CHUNK_SIZE_CFG" -gt 0 ] 2>/dev/null; then
    GIANTS="$(printf '%s\n' "$COUNTS" | awk -v m="$CHUNK_SIZE_CFG" '$1 > m {c++} END {print c+0}')"
  fi
  log "  $f: chunks=$N char_count min=${MIN} max=${MAX} over-chunk_size(${CHUNK_SIZE_CFG:-?})=${GIANTS}"
  {
    printf '\n== fixture %s ==\n' "$f"
    printf 'chunks=%s char_count_min=%s char_count_max=%s over_chunk_size=%s (chunk_size=%s chunk_overlap=%s)\n' \
      "$N" "$MIN" "$MAX" "$GIANTS" "${CHUNK_SIZE_CFG:-?}" "${CHUNK_OVERLAP_CFG:-?}"
    grep -E '"step":"vector_row"' "$TR" | head -n 6 | while IFS= read -r line; do
      CID_="$(printf '%s' "$line" | sed -n 's/.*"metadata_chunk_id":"\([^"]*\)".*/\1/p')"
      PAGES_="$(printf '%s' "$line" | sed -n 's/.*"metadata_pages":\(\[[^]]*\]\).*/\1/p')"
      LANG_="$(printf '%s' "$line" | sed -n 's/.*"metadata_language":\("[^"]*"\|null\).*/\1/p')"
      CHARS_="$(printf '%s' "$line" | grep -oE '"metadata_char_count":[0-9]+' | grep -oE '[0-9]+$')"
      PREV_="$(printf '%s' "$line" | sed -n 's/.*"content_preview":"\(.*\)".*/\1/p')"
      printf '  chunk_id=%s pages=%s lang=%s chars=%s\n    preview: %s\n' \
        "${CID_:-?}" "${PAGES_:-?}" "${LANG_:-?}" "${CHARS_:-?}" "${PREV_:-<empty>}"
    done
  } >> "$CHUNK_SAMPLES"
done
log "chunk samples artifact (B9 input): $CHUNK_SAMPLES"
result CHUNK_EVIDENCE INFO "per-fixture chunk char_count distributions + representative samples (with page provenance and raw text previews, Arabic included verbatim) written to the evidence bundle for the B9 human review — no quality judgment is made here by design"

# ---- systematic-failure advisory (roadmap B8 stop condition) ----------------
NONPASS=0; AR_NONPASS=0; EN_NONPASS=0
if [ -s "$ROWS" ]; then
  while IFS='|' read -r _tag r_f r_l r_rest; do
    case "$(printf '%s' "$r_rest" | awk -F'|' '{print $NF}')" in
      PASS) : ;;
      *)
        NONPASS=$((NONPASS+1))
        case "$r_l" in *ar*) AR_NONPASS=$((AR_NONPASS+1)) ;; *) EN_NONPASS=$((EN_NONPASS+1)) ;; esac
        ;;
    esac
  done < "$ROWS"
fi
if [ "$NONPASS" -gt 0 ] 2>/dev/null; then
  log ""
  log "STOP-CONDITION ADVISORY (roadmap B8): $NONPASS fixture(s) did not reach a PASS verdict."
  if [ "$AR_NONPASS" -ge 2 ] 2>/dev/null && [ "$EN_NONPASS" = "0" ] 2>/dev/null; then
    log "  The failing fixtures are ALL Arabic-language while every English fixture passed —"
    log "  this looks like a SYSTEMATICALLY FAILING CATEGORY (e.g. all scanned Arabic)."
    log "  Per the roadmap: record it, STOP, and analyze before any further uploads;"
    log "  do NOT tune chunking/OCR configuration mid-smoke."
  else
    log "  Analyze each failing fixture's evidence window before any further uploads;"
    log "  do NOT tune configuration mid-smoke."
  fi
fi

# ============================================================================
# SECTION 8 — CLEANUP (only this run's resources; safe to re-run)
# ============================================================================
section 8 "CLEANUP (only this run's resources)"

# B7 lesson: each ids file is processed INDIVIDUALLY (single JSON object per
# file, trailing newline preserved — files are NEVER concatenated). Every
# delete is (a) scoped to an exact recorded UUID and (b) guarded by the B8
# verification-resource predicate, so a corrupted ids file can never make
# this script delete arbitrary user data. Vector rows are deleted FIRST and
# explicitly (the table is FK-less by design), then material, course, user —
# FK-safe order — and every S3 delete is verified with head_object.

cat > "$TMP_HOST/b8_cleanup.py" <<'PY'
"""Delete ONLY the rows/object created by this B8 run (exact UUIDs; never broad).

Every delete is (a) scoped to an exact recorded UUID and (b) guarded by the
B8 verification-resource predicate (synthetic issuer URN for the user,
"B8 staging verification " title prefix for course and material), so a
corrupted or hand-edited ids file can never make this script delete
arbitrary user data — the guard refuses and reports instead.

Ordering and completeness: vector rows first (FK-less by design), then
material, course, user; the S3 object is deleted by its exact recorded key
and a successful delete is verified afterwards with head_object (expected
404). Every step is idempotent.
"""
import asyncio
import json
import sys
from uuid import UUID

IDS_FILE = sys.argv[1]

B8_ISSUER = "urn:openlearn:b8-staging-verify"
B8_TITLE_PREFIX = "B8 staging verification "
B8_SUBJECT_PREFIX = "b8-verify-"


def out(step, **kw):
    print("B8CLN|" + json.dumps({"step": step, **kw}, separators=(",", ":"), default=str), flush=True)


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
            # ---- predicate guards: refuse anything not created by B8 runs --
            if uid:
                urow = (
                    await session.execute(select(User).where(User.id == UUID(uid)))
                ).scalar_one_or_none()
                if urow is not None and not (
                    urow.keycloak_issuer == B8_ISSUER
                    and str(urow.keycloak_subject).startswith(B8_SUBJECT_PREFIX)
                ):
                    out("refused_user_not_b8_resource", user_id=uid)
                    return
            if cid:
                crow = (
                    await session.execute(select(Course).where(Course.id == UUID(cid)))
                ).scalar_one_or_none()
                if crow is not None and not str(crow.title).startswith(B8_TITLE_PREFIX):
                    out("refused_course_not_b8_resource", course_id=cid)
                    return
            if mid:
                mrow = (
                    await session.execute(select(Material).where(Material.id == UUID(mid)))
                ).scalar_one_or_none()
                if mrow is not None and not str(mrow.title).startswith(B8_TITLE_PREFIX):
                    out("refused_material_not_b8_resource", material_id=mid)
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

if [ -n "$CID_WORKER" ]; then
  push_file "$CID_WORKER" "$TMP_HOST/b8_cleanup.py" "$CONTAINER_TMP/b8_cleanup.py" || true
fi

CLEAN_OK=1
CLEAN_NOTE=""
CLEANED_FILES=""
if [ -n "$CID_WORKER" ]; then
  for f in $FIX_LIST; do
    idsf="ids_${f}.json"
    docker exec "$CID_WORKER" test -f "$CONTAINER_TMP/$idsf" 2>/dev/null || continue
    CLEANED_FILES="$CLEANED_FILES $idsf"
    HOST_ONE="$TMP_HOST/one_${idsf}"
    if ! docker exec "$CID_WORKER" cat "$CONTAINER_TMP/$idsf" > "$HOST_ONE" 2>/dev/null; then
      log "  $idsf: could not read ids file from the worker container"
      CLEAN_OK=0
      CLEAN_NOTE="$CLEAN_NOTE[$idsf unreadable]"
      continue
    fi
    log "resources created for fixture '$f' (ids file $idsf, recorded for the transcript):"
    sed 's/^/    /' "$HOST_ONE"
    cp "$HOST_ONE" "$EVID_DIR/fixtures/${idsf}" 2>/dev/null || true
    if ! push_file "$CID_WORKER" "$HOST_ONE" "$CONTAINER_TMP/one_ids.json"; then
      log "  $idsf: push of ids file into the worker container failed"
      CLEAN_OK=0
      CLEAN_NOTE="$CLEAN_NOTE[$idsf push failed]"
      continue
    fi
    OUT_C="$(worker_py 0 "$CONTAINER_TMP/b8_cleanup.py" "$CONTAINER_TMP/one_ids.json" 2>&1)"
    printf '%s\n' "$OUT_C" | sed 's/^/  cleanup: /'
    printf '%s\n' "$OUT_C" > "$EVID_DIR/fixtures/cleanup_${f}.txt" 2>/dev/null || true
    if ! printf '%s\n' "$OUT_C" | grep -q '"step":"leftover_check","materials":0,"vectors":0'; then
      CLEAN_OK=0
      CLEAN_NOTE="$CLEAN_NOTE[$f rows not fully removed]"
    fi
    if printf '%s\n' "$OUT_C" | grep -qE '"step":"(ids_file_error|refused_|s3_delete_error|s3_verify_error|s3_verify_still_present)'; then
      CLEAN_OK=0
      CLEAN_NOTE="$CLEAN_NOTE[$f cleanup step error/refusal]"
    fi
    if ! grep -q '"s3_key": *null' "$HOST_ONE"; then
      # A non-null recorded s3_key MUST end with a verified-absent object.
      printf '%s\n' "$OUT_C" | grep -q '"step":"object_verified_absent"' \
        || { CLEAN_OK=0; CLEAN_NOTE="$CLEAN_NOTE[$f s3 object not verified absent]"; }
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
      result CLEANUP PASS "all B8-created rows/objects deleted for:${CLEANED_FILES} (exact-UUID deletes + explicit FK-less vector deletes + predicate-guarded, verified S3 deletion); vector_records back to baseline ${AFTER}"
    else
      result CLEANUP FAIL "cleanup incomplete (${CLEAN_NOTE:-see per-fixture cleanup output above}) — the transcript lists every affected exact ID; historical leftovers are reported below"
    fi
  else
    log "no ids files found in the worker container (nothing was seeded, or seeding never started)."
    LEAK="$(psql_ro "SELECT count(*) FROM users WHERE keycloak_subject LIKE 'b8-verify-${MARK}%' AND keycloak_issuer = 'urn:openlearn:b8-staging-verify';" | tr -d '[:space:]')"
    if [ "${LEAK:-0}" = "0" ]; then
      result CLEANUP PASS "nothing was created by this run (no cleanup needed)"
    else
      result CLEANUP FAIL "$LEAK B8 user row(s) exist without an ids file — find them via: SELECT * FROM users WHERE keycloak_subject LIKE 'b8-verify-${MARK}%' AND keycloak_issuer = 'urn:openlearn:b8-staging-verify';"
    fi
  fi
else
  result CLEANUP FAIL "worker container not found; cleanup could not run — any resources this run created are recorded in the transcripts above"
fi

# ---------------------------------------------------------------------------
# Previous-run B8 verification leftovers (report-only by default).
#
# Identified SOLELY by the synthetic issuer URN the verifier writes on its own
# users (real Keycloak issuers are https URLs, so this can never match user
# data). This block never deletes anything unless B8_CLEAN_PREVIOUS_B8=1, in
# which case b8_cleanup_previous.py first prints every exact UUID it is about
# to remove and then deletes in FK order with explicit vector and S3 cleanup.
# ---------------------------------------------------------------------------
PRIOR_PREDICATE="keycloak_issuer = 'urn:openlearn:b8-staging-verify' AND keycloak_subject NOT LIKE 'b8-verify-${MARK}%'"
PRIOR_USERS="$(psql_ro "SELECT id || ' | subject=' || keycloak_subject FROM users WHERE ${PRIOR_PREDICATE};")"
PRIOR_COURSES="$(psql_ro "SELECT c.id || ' | owner=' || c.owner_id || ' | title=' || c.title FROM courses c WHERE c.owner_id IN (SELECT id FROM users WHERE ${PRIOR_PREDICATE});")"
PRIOR_MATERIALS="$(psql_ro "SELECT m.id || ' | status=' || m.status || ' | course=' || m.course_id || ' | s3_key=' || m.s3_key FROM materials m WHERE m.uploaded_by IN (SELECT id FROM users WHERE ${PRIOR_PREDICATE}) OR m.course_id IN (SELECT c.id FROM courses c WHERE c.owner_id IN (SELECT id FROM users WHERE ${PRIOR_PREDICATE}));")"
PRIOR_VECTORS="$(psql_ro "SELECT split_part(v.id, ':', 1) AS material_id, count(*) FROM vector_records v WHERE split_part(v.id, ':', 1) IN (SELECT m.id::text FROM materials m WHERE m.uploaded_by IN (SELECT id FROM users WHERE ${PRIOR_PREDICATE}) OR m.course_id IN (SELECT c.id FROM courses c WHERE c.owner_id IN (SELECT id FROM users WHERE ${PRIOR_PREDICATE}))) GROUP BY 1 ORDER BY 1;")"

log ""
log "previous-run B8 verification resources (synthetic issuer URN, this run excluded):"
if [ -n "$PRIOR_USERS" ] || [ -n "$PRIOR_COURSES" ] || [ -n "$PRIOR_MATERIALS" ] || [ -n "$PRIOR_VECTORS" ]; then
  printf '%s\n' "$PRIOR_USERS"   | sed '/^$/d; s/^/  user:     /'
  printf '%s\n' "$PRIOR_COURSES" | sed '/^$/d; s/^/  course:   /'
  printf '%s\n' "$PRIOR_MATERIALS" | sed '/^$/d; s/^/  material: /'
  printf '%s\n' "$PRIOR_VECTORS" | sed '/^$/d; s/^/  vectors:  /'
  if [ "$B8_CLEAN_PREVIOUS_B8" = "1" ] && [ -n "$CID_WORKER" ]; then
    log ""
    log "B8_CLEAN_PREVIOUS_B8=1 — deleting the resources listed above (exact UUIDs,"
    log "FK order, explicit vector + S3 cleanup; inventory + outcome below):"
    cat > "$TMP_HOST/b8_cleanup_previous.py" <<'PY'
"""Opt-in removal of PREVIOUS B8 verifier-run resources (B8_CLEAN_PREVIOUS_B8=1).

Candidates are enumerated SOLELY through the synthetic B8 verification issuer
URN on users, EXCLUDING the current run's mark; courses are those owned by
those users; materials are those uploaded by those users OR living in those
courses; vector rows are matched by the exact material-id prefix list; S3
objects by the materials' recorded exact s3_key values. The complete
inventory is PRINTED before any deletion, then deletions run in FK order.
No title-pattern deletes, no unscoped deletes, no cascades assumed.
"""
import asyncio
import json
import sys

CURRENT_MARK = sys.argv[1] if len(sys.argv) > 1 else ""

B8_ISSUER = "urn:openlearn:b8-staging-verify"
B8_SUBJECT_PREFIX = "b8-verify-"


def out(step, **kw):
    print("B8CLN|" + json.dumps({"step": step, **kw}, separators=(",", ":"), default=str), flush=True)


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
                            User.keycloak_issuer == B8_ISSUER,
                            User.keycloak_subject.notlike(f"{B8_SUBJECT_PREFIX}{CURRENT_MARK}%"),
                            User.keycloak_subject.like(f"{B8_SUBJECT_PREFIX}%"),
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
    push_file "$CID_WORKER" "$TMP_HOST/b8_cleanup_previous.py" "$CONTAINER_TMP/b8_cleanup_previous.py" || true
    OUT_P="$(worker_py 0 "$CONTAINER_TMP/b8_cleanup_previous.py" "$MARK" 2>&1)"
    printf '%s\n' "$OUT_P" | sed 's/^/  previous-cleanup: /'
    printf '%s\n' "$OUT_P" > "$EVID_DIR/previous_cleanup.txt" 2>/dev/null || true
    # Verdict by re-querying the same issuer-scoped predicate, not by parsing
    # the cleanup output (the state of the database is the evidence).
    POST_USERS="$(psql_ro "SELECT count(*) FROM users WHERE ${PRIOR_PREDICATE};" | tr -d '[:space:]')"
    if [ "${POST_USERS:-1}" = "0" ] && ! printf '%s\n' "$OUT_P" | grep -q '"step":"previous_cleanup_error"'; then
      result CLEANUP_PREVIOUS PASS "previous-run B8 verification resources fully removed (re-query of the issuer-scoped predicate returns 0 users)"
    else
      result CLEANUP_PREVIOUS FAIL "previous-run cleanup incomplete (users remaining after cleanup: ${POST_USERS:-unavailable}) — see previous-cleanup output above"
    fi
  else
    result CLEANUP_PREVIOUS INFO "previous-run B8 verification resources remain (listed above); report-only by default — re-run with B8_CLEAN_PREVIOUS_B8=1 to remove exactly these"
  fi
else
  result CLEANUP_PREVIOUS INFO "no previous-run B8 verification resources remain on staging"
fi

# ============================================================================
# SECTION 9 — EVIDENCE BUNDLE MANIFEST
# ============================================================================
section 9 "EVIDENCE BUNDLE MANIFEST"
cp "$RESULTS" "$EVID_DIR/results.txt" 2>/dev/null || true
cp "$ROWS" "$EVID_DIR/per_fixture_rows.txt" 2>/dev/null || true
log "evidence dir: $EVID_DIR (KEPT; also packed at exit):"
find "$EVID_DIR" -type f | sort | sed "s|^${EVID_DIR}/|  |"
result EVIDENCE INFO "evidence bundle directory + tarball (sha256 printed at exit) — run metadata, repo/container/config snapshots (secrets as SET/MISSING), per-fixture smoke transcripts + worker-log windows + ids files + cleanup transcripts, chunk samples/distribution (B9 feed), results table, final verdict"

# ============================================================================
# SECTION 10 — FINAL SUMMARY (mechanical verdict; no manual conclusion)
# ============================================================================
section 10 "FINAL SUMMARY (B8RESULT|id|status|note)"
cat "$RESULTS"

echo
log "Legend: PASS verified on the deployed staging runtime; BLOCKED environment"
log "or external provider prevented collection (NEVER converted to FAIL);"
log "NOT OBSERVABLE the behavior was not exercised by this run by design;"
log "SKIPPED explicitly disabled by an opt-out flag; INFO informational only;"
log "FAIL the acceptance criterion is violated with sufficient evidence."
log ""

FAILED_REQUIRED=""
for id in $REQUIRED_IDS; do
  st="$(awk -F'|' -v i="$id" '$2==i {print $3}' "$RESULTS" | tail -n 1)"
  case "$st" in
    FAIL|BLOCKED) FAILED_REQUIRED="$FAILED_REQUIRED $id" ;;
  esac
done

if [ -z "$FAILED_REQUIRED" ]; then
  log "VERDICT: ALL REQUIRED B8 CRITERIA PASSED (exit 0)."
  log "The per-file smoke results table above is the W3 deliverable; record it in"
  log "docs/tasks/ai-week7-8/progress.md together with the evidence bundle."
  log "Reminder: B8 deliberately exercises NO reasoning-gateway call (B6/B7 scope)"
  log "and makes NO chunk-quality judgment (B9 scope — feed artifact in the bundle)."
  log "Completed at $(now)."
  exit 0
else
  log "VERDICT: REQUIRED B8 CRITERIA NOT MET:$FAILED_REQUIRED (exit 1)."
  log "Every collected evidence block above remains valid; do NOT attribute"
  log "unrelated staging failures to B8 without reading the per-fixture worker-log"
  log "windows in this transcript and the evidence bundle."
  log "Completed at $(now)."
  exit 1
fi
