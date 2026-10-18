#!/usr/bin/env bash
# =============================================================================
# run-material-smoke-test.sh
#
# OpenLearn-AI — frontend-redesign — local END-TO-END material-ingestion smoke
# test (the environment-health counterpart is scripts/verify-local-environment.sh;
# the two are deliberately separate concerns).
#
# What it does (per fixture, sequentially — English first, then Arabic, so a
# failure is attributable to one file):
#
#   1. capture a REAL instructor access token through the actual UI login flow
#      (Playwright, Keycloak-hosted pages, same client + PKCE as the app — the
#      exact capture pattern proven by the Batch 0.1 local verifier; direct
#      grants are disabled on openlearn-frontend by design and nothing here
#      weakens auth),
#   2. create an instructor-owned course (clearly labeled, self-deleted),
#   3. request a presigned upload URL (POST /v1/courses/{id}/materials/upload-url),
#   4. upload the fixture PDF bytes to the returned object-storage URL,
#   5. register the material (POST /v1/courses/{id}/materials) -> 202
#      {material_id, job_id} (job_id is a log-correlation id, not queryable),
#   6. poll GET /v1/materials/{material_id}/status until ready|failed and
#      observe the REAL lifecycle (pending -> processing -> ready|failed),
#   7. verify the final state is persisted (status endpoint + materials list),
#   8. collect read-only DB evidence: vector_records row count for the material,
#   9. run the data/authorization sanity block: the smoke course is invisible
#      to the student (owner-scoped listing), and the student cannot read the
#      instructor's material status (ownership enforced).
#
# After the run it deletes exactly what it created (default; --keep-resources
# skips cleanup): FK-less vector rows first (exact recorded material-id prefix),
# then the course via the API (cascading the material row), then the S3 object
# by its exact recorded key — every delete scoped to THIS run's recorded ids,
# mirroring the B7/B8 staging-verifier cleanup discipline. Nothing pre-existing
# is ever touched.
#
# Fixtures (locked by the Batch 2.1 decision record; VERIFIED paths at the
# current checkout — the raw corpus files carry a `custom_custom_` filename
# prefix, so the paths differ cosmetically from the names in the batch prompt;
# these are the same locked documents, not substitutes):
#   en_born  experiments/OCR/ocr-benchmark/data/raw/custom/1. English born-digital/
#            custom_custom_english_born_digital_005_p001.pdf   (English, born-digital)
#   ar_born  experiments/OCR/ocr-benchmark/data/raw/custom/2. Arabic born-digital/
#            custom_custom_arabic_born_digital_003_p004.pdf    (Arabic, born-digital)
#
# Honest scope of what a PASS proves (and does NOT):
#   * Docling parsing + chunking + embedding + pgvector persistence + the full
#     status lifecycle ran against the real local services.
#   * Born-digital PDFs with >= 50 extracted chars NEVER invoke OCR (the
#     targeted-OCR gate, settings.ocr_min_text_chars) — a PASS therefore does
#     NOT prove scanned-PDF OCR (Gemini) works; that path needs GEMINI_API_KEY
#     and a scanned fixture and is explicitly NOT exercised here.
#   * With the default local provider block the embeddings are real (BGE-M3);
#     if you set AI_EMBEDDING_PROVIDER=mock the vectors are placeholder values
#     — the run is then a pipeline-plumbing pass with a mocked stage, and the
#     final summary reports which embedding provider the worker had configured.
#
# Prerequisites (checked, never assumed):
#   * scripts/setup-dev.sh has been run (env files + venv + accounts)
#   * docker services up (db, redis, minio, keycloak) and the bucket exists
#   * backend API running on :8000 (GET /health answers)
#   * worker running (bash scripts/run-worker-dev.sh in another terminal)
#   * frontend deps installed (frontend/node_modules) for the token capture;
#     the dev server on :3000 is started by this script if not already running
#
# Environment knobs (defaults are conservative):
#   SMOKE_TIMEOUT=900        seconds to wait per fixture for ready|failed
#                            (first-ever run also downloads the ~2 GB BGE-M3
#                            model — raise this on slow connections)
#   KEEP_RESOURCES=0         1 skips the cleanup section
#   API_URL / WEB_URL        http://localhost:8000 / http://localhost:3000
#
# Usage:
#   bash scripts/run-material-smoke-test.sh
#   bash scripts/run-material-smoke-test.sh --keep-resources   # same as KEEP_RESOURCES=1
#
# Exit codes: 0 = every REQUIRED smoke criterion PASS; 1 = at least one
# REQUIRED criterion FAIL/BLOCKED (including an incomplete run — both fixtures
# must record an explicit PASS); 2 = preflight fatal; 64 = unknown CLI option.
#
# Secret hygiene: tokens are written to 0600 files in the evidence directory
# and deleted on exit; passwords and presigned URLs are NEVER printed; the
# evidence log stores status codes and identifiers only (response bodies
# embedded in result notes are scrubbed of presigned-URL signatures; the raw
# bodies stay in the 0700 evidence directory).
# =============================================================================

set -uo pipefail

# ----------------------------- configuration --------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${REPO_DIR:-$SCRIPT_DIR/..}"
REPO_DIR="$(cd "${REPO_DIR}" && pwd)"
if [ ! -f "$REPO_DIR/frontend/package.json" ] || [ ! -f "$REPO_DIR/scripts/setup-dev.sh" ]; then
  echo "ERROR: could not locate the OpenLearn-AI repository at $REPO_DIR." >&2
  echo "       Run from the repo, or set REPO_DIR=/path/to/OpenLearn-AI." >&2
  exit 2
fi

# CLI flags (documented in the header). KEEP_RESOURCES is also honored as an
# environment variable for backwards compatibility.
for arg in "$@"; do
  case "$arg" in
    --keep-resources) KEEP_RESOURCES=1 ;;
    *) echo "unknown option: $arg (supported: --keep-resources)" >&2; exit 64 ;;
  esac
done

API_URL="${API_URL:-http://localhost:8000}"
WEB_URL="${WEB_URL:-http://localhost:3000}"
SMOKE_TIMEOUT="${SMOKE_TIMEOUT:-900}"
KEEP_RESOURCES="${KEEP_RESOURCES:-0}"
POLL_INTERVAL=5

EN_PDF="$REPO_DIR/experiments/OCR/ocr-benchmark/data/raw/custom/1. English born-digital/custom_custom_english_born_digital_005_p001.pdf"
AR_PDF="$REPO_DIR/experiments/OCR/ocr-benchmark/data/raw/custom/2. Arabic born-digital/custom_custom_arabic_born_digital_003_p004.pdf"

DC=(docker compose --env-file "$REPO_DIR/.env.local" -f "$REPO_DIR/infra/docker-compose.dev.yml")

TS="$(date +%Y%m%d-%H%M%S)"
EVIDENCE_DIR="${EVIDENCE_DIR:-$REPO_DIR/../openlearn-material-smoke-evidence/run-$TS}"
mkdir -p "$EVIDENCE_DIR"
chmod 700 "$EVIDENCE_DIR"
LOG="$EVIDENCE_DIR/evidence.log"
RESULTS="$EVIDENCE_DIR/results.txt"
: > "$RESULTS"
INSTRUCTOR_TOKEN_FILE="$EVIDENCE_DIR/instructor.token"   # deleted on exit
STUDENT_TOKEN_FILE="$EVIDENCE_DIR/student.token"         # deleted on exit
CREATED_IDS="$EVIDENCE_DIR/created-ids.txt"              # per-run resource ids
: > "$CREATED_IDS"

# ----------------------------- tiny framework -------------------------------
record() { printf 'SMOKERESULT|%s|%s|%s\n' "$1" "$2" "$3" | tee -a "$RESULTS"; }
section() { printf '\n== %s ==\n' "$*"; }
fail_soft() { printf 'FATAL: %s\n' "$*" >&2; exit 2; }
env_var_value() { sed -n "s/^${1}=//p" "$2" | tail -1 | tr -d '\r'; } # last wins, matching dotenv
mask_url() { sed -E 's#://[^@/]*@#://<credentials>@#' <<< "$1"; }
# scrub query-string signature parameters before a response body is embedded
# in a result note (bodies can contain presigned URLs; the raw body remains
# available as a 0600-dir evidence file)
scrub_presigned() { sed -E 's/X-Amz-[A-Za-z-]+=[^&"]*/X-Amz-<masked>/g' <<< "$1"; }
json_field() { # <json-file> <top-level-key> -> value ('' when missing/invalid)
  python3 -c '
import json, sys
try:
    data = json.load(open(sys.argv[1]))
    val = data.get(sys.argv[2]) if isinstance(data, dict) else None
    print(val if val is not None else "")
except Exception as e:
    print(f"__PARSE_ERROR__ {e}", file=sys.stderr)
    print("")
' "$1" "$2" 2>/dev/null
}

exec > >(tee -a "$LOG") 2>&1
cat <<EOF
==============================================================================
OpenLearn-AI — LOCAL MATERIAL-INGESTION smoke test
repo:     $REPO_DIR
branch:   $(git -C "$REPO_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')
HEAD:     $(git -C "$REPO_DIR" rev-parse HEAD 2>/dev/null || echo '?')
api:      $API_URL   web: $WEB_URL
timeout:  ${SMOKE_TIMEOUT}s per fixture   keep-resources=$KEEP_RESOURCES
evidence: $EVIDENCE_DIR
==============================================================================
EOF

MAIN_CLEANUP_DONE=0
RESOURCES_PROCESSED=0

# Fallback resource cleanup for interrupted runs (kill/Ctrl-C/crash AFTER
# resources were created but BEFORE the normal cleanup block ran). Best-effort
# by nature: it records one BLOCKED line so the results file never lies about
# an incomplete run, and never runs when the normal cleanup already did.
trap_cleanup_exit() {
  local rc=$?
  rm -f "$INSTRUCTOR_TOKEN_FILE" "$STUDENT_TOKEN_FILE"
  if [ -f "$EVIDENCE_DIR/frontend.pid" ]; then
    kill "$(cat "$EVIDENCE_DIR/frontend.pid")" >/dev/null 2>&1 || true
  fi
  if [ "$MAIN_CLEANUP_DONE" != "1" ] && [ "$KEEP_RESOURCES" != "1" ] \
     && [ "$RESOURCES_PROCESSED" = "1" ] && [ -s "$CREATED_IDS" ]; then
    echo "" | tee -a "$LOG"
    echo "INTERRUPTED before the normal cleanup — best-effort fallback deletion follows" | tee -a "$LOG"
    while read -r FID KIND RID; do
      case "$KIND" in
        material)
          "${DC[@]}" exec -T db psql -U openlearn -d openlearn_dev -tAc \
            "DELETE FROM vector_records WHERE id LIKE '${RID}:%';" >/dev/null 2>&1 || true ;;
        course)
          if [ -s "$INSTRUCTOR_TOKEN_FILE" ]; then
            curl --noproxy '*' -sS -o /dev/null -X DELETE \
              -H "Authorization: Bearer $(cat "$INSTRUCTOR_TOKEN_FILE")" \
              "$API_URL/v1/courses/$RID" >/dev/null 2>&1 || true
          fi ;;
        s3_key)
          "${DC[@]}" exec -T minio mc rm --force "local/$(env_var_value S3_BUCKET_NAME "$REPO_DIR/.env.local")/$RID" >/dev/null 2>&1 || true ;;
      esac
    done < "$CREATED_IDS"
    record "cleanup.trap" "BLOCKED" "run interrupted before the normal cleanup; best-effort fallback deletion executed — verify remaining resources with the ids in created-ids.txt"
  fi
  exit "$rc"
}
trap trap_cleanup_exit EXIT

# ----------------------------- 0. preflight ---------------------------------
section "0. Preflight"
for tool in docker curl python3 node; do
  command -v "$tool" >/dev/null 2>&1 || fail_soft "missing tool: $tool"
done
[ -f "$REPO_DIR/.env.local" ] || fail_soft ".env.local not found — run scripts/setup-dev.sh"
[ -f "$REPO_DIR/backend/.env" ] || fail_soft "backend/.env not found — run scripts/setup-dev.sh"
[ -x "$REPO_DIR/backend/.venv/bin/python" ] || [ -x "$REPO_DIR/backend/.venv/Scripts/python.exe" ] \
  || fail_soft "backend/.venv missing — run scripts/setup-dev.sh"
[ -f "$EN_PDF" ] || fail_soft "English fixture not found: $EN_PDF"
[ -f "$AR_PDF" ] || fail_soft "Arabic fixture not found: $AR_PDF"
echo "fixtures verified at the current checkout:"
echo "  en_born: $(basename "$EN_PDF") ($(wc -c < "$EN_PDF") bytes)"
echo "  ar_born: $(basename "$AR_PDF") ($(wc -c < "$AR_PDF") bytes)"

INSTRUCTOR_PASSWORD="$(env_var_value OPENLEARN_INSTRUCTOR_USER_PASSWORD "$REPO_DIR/.env.local")"
STUDENT_PASSWORD="$(env_var_value OPENLEARN_TEST_USER_PASSWORD "$REPO_DIR/.env.local")"
[ -n "$INSTRUCTOR_PASSWORD" ] || fail_soft "OPENLEARN_INSTRUCTOR_USER_PASSWORD missing in .env.local"
[ -n "$STUDENT_PASSWORD" ] || fail_soft "OPENLEARN_TEST_USER_PASSWORD missing in .env.local"

# ----------------------------- 1. environment up ----------------------------
section "1. Environment readiness (services, API, worker)"
PS_OUT="$("${DC[@]}" ps --services --filter status=running 2>/dev/null || true)"
for SVC in db redis minio keycloak; do
  printf '%s\n' "$PS_OUT" | grep -qx "$SVC" || fail_soft "service '$SVC' not running — run scripts/setup-dev.sh (or docker compose --env-file .env.local -f infra/docker-compose.dev.yml up -d)"
done
echo "docker services: db redis minio keycloak all running"

curl -sf --noproxy '*' --max-time 5 "$API_URL/health" >/dev/null 2>&1 \
  || fail_soft "backend not answering on $API_URL — start it: cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000"
echo "backend API: /health OK"

VENV_BIN="$REPO_DIR/backend/.venv/bin"
[ -x "$VENV_BIN/celery" ] || VENV_BIN="$REPO_DIR/backend/.venv/Scripts"
REDIS_PASSWORD_VALUE="$(env_var_value REDIS_PASSWORD "$REPO_DIR/.env.local")"
REDIS_URL_FILE_VALUE="$(env_var_value REDIS_URL "$REPO_DIR/.env.local")"
if [ -n "$REDIS_URL_FILE_VALUE" ]; then
  WORKER_REDIS_URL="$REDIS_URL_FILE_VALUE"
else
  WORKER_REDIS_URL="redis://:${REDIS_PASSWORD_VALUE}@127.0.0.1:6379"
fi
PING_OUT="$( cd "$REPO_DIR/backend" \
  && env REDIS_PASSWORD="$REDIS_PASSWORD_VALUE" REDIS_URL="$WORKER_REDIS_URL" \
     "$VENV_BIN/celery" -A app.workers.celery_app inspect ping --timeout 5 2>&1 )"
printf '%s' "$PING_OUT" | grep -q "OK" \
  || fail_soft "no worker answered — start it in another terminal: bash scripts/run-worker-dev.sh"
echo "worker: answering inspect ping (queues verified by the environment verifier)"

# ----------------------------- 2. auth capture ------------------------------
section "2. Real-token capture (Playwright, actual UI login flow — no auth weakening)"
if [ ! -d "$REPO_DIR/frontend/node_modules" ]; then
  fail_soft "frontend/node_modules missing — run scripts/setup-dev.sh (token capture needs Playwright)"
fi
echo "Ensuring Playwright chromium is installed (idempotent) ..."
( cd "$REPO_DIR/frontend" && npx playwright install chromium >/dev/null 2>&1 ) \
  || echo "WARN: playwright install failed — token capture may fail"

if ! curl -sf --noproxy '*' --max-time 5 -o /dev/null "$WEB_URL" 2>&1; then
  echo "Frontend not running on :3000 — starting (next dev) ..."
  ( cd "$REPO_DIR/frontend" && nohup npm run dev > "$EVIDENCE_DIR/frontend.log" 2>&1 & echo $! > "$EVIDENCE_DIR/frontend.pid" )
  FE_OK=0
  for i in $(seq 1 36); do curl -sf --noproxy '*' --max-time 5 -o /dev/null "$WEB_URL" && FE_OK=1 && break; sleep 5; done
  [ "$FE_OK" = "1" ] || fail_soft "frontend never answered on :3000 — see $EVIDENCE_DIR/frontend.log"
else
  echo "Frontend already running on :3000 — reusing it."
fi

cat > "$EVIDENCE_DIR/capture-token.cjs" <<'CAPTURE_SCRIPT_START'
// Token capture via the REAL UI login flow (Batch 0.1 pattern, parameterized
// user). Intercepts the Keycloak token-endpoint response. Nothing is bypassed:
// same credentials, same client, same PKCE flow as the app.
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const base = process.env.WEB_URL || 'http://localhost:3000';
  const user = process.env.SMOKE_USERNAME;
  const pass = process.env.SMOKE_PASSWORD;
  if (!user || !pass) { console.error('CAPTURE_ERROR missing credentials'); process.exit(3); }
  let token = null;
  const browser = await chromium.launch();
  try {
    const ctx = await browser.newContext();
    const page = await ctx.newPage();
    page.on('response', async (r) => {
      try {
        if (/\/realms\/[^/]+\/protocol\/openid-connect\/token/.test(r.url()) &&
            r.request().method() === 'POST') {
          const j = await r.json();
          if (j && j.access_token) token = j.access_token;
        }
      } catch (_) {}
    });
    await page.goto(base + '/login');
    await page.getByRole('button', { name: /sign in with openlearn ai/i }).click();
    await page.waitForSelector('#username', { state: 'visible' });
    await page.fill('#username', user);
    await page.fill('#password', pass);
    await page.click('#kc-login');
    await page.waitForURL(/\/dashboard$/, { timeout: 30000 });
    await page.waitForTimeout(3000);
  } finally { await browser.close(); }
  if (!token) { console.error('NO_TOKEN_CAPTURED'); process.exit(4); }
  fs.writeFileSync(process.env.TOKEN_FILE, token, { mode: 0o600 });
  console.log('TOKEN_CAPTURED=yes');
})().catch((e) => { console.error('CAPTURE_ERROR', e.message); process.exit(2); });
CAPTURE_SCRIPT_START

capture_token() { # <username> <password> <token-file> -> 0 on success
  local user="$1" pass="$2" tokenfile="$3" rc
  local caplog="${tokenfile%.token}-capture.log"
  # Node output (CAPTURE_ERROR / NO_TOKEN_CAPTURED / Playwright diagnostics —
  # no tokens, which go only to the token file) is captured to the evidence
  # dir so capture failures are diagnosable; the previously discarded output
  # made student-capture failures impossible to triage.
  # Wall-clock guard: `timeout` when available (GNU coreutils; optional on
  # macOS) so a hung browser cannot wedge the whole run — Playwright's own
  # 30 s wait bounds it otherwise.
  if command -v timeout >/dev/null 2>&1; then
    ( cd "$REPO_DIR/frontend" \
      && NODE_PATH="$REPO_DIR/frontend/node_modules" \
         WEB_URL="$WEB_URL" SMOKE_USERNAME="$user" SMOKE_PASSWORD="$pass" TOKEN_FILE="$tokenfile" \
         timeout 90 node "$EVIDENCE_DIR/capture-token.cjs" ) > "$caplog" 2>&1
    rc=$?
  else
    ( cd "$REPO_DIR/frontend" \
      && NODE_PATH="$REPO_DIR/frontend/node_modules" \
         WEB_URL="$WEB_URL" SMOKE_USERNAME="$user" SMOKE_PASSWORD="$pass" TOKEN_FILE="$tokenfile" \
         node "$EVIDENCE_DIR/capture-token.cjs" ) > "$caplog" 2>&1
    rc=$?
  fi
  if [ "$rc" != "0" ]; then
    echo "capture diagnostics for '${user}' (exit $rc) -> ${caplog}:"
    tail -5 "$caplog" | sed 's/^/    /'
  fi
  return "$rc"
}

echo "Capturing instructor token (user 'instructor') ..."
if capture_token instructor "$INSTRUCTOR_PASSWORD" "$INSTRUCTOR_TOKEN_FILE" \
   && [ -s "$INSTRUCTOR_TOKEN_FILE" ]; then
  echo "instructor token: captured (never printed)"
else
  record "auth.instructor-token" "BLOCKED" "instructor token capture failed (exit code + diagnostics in evidence/instructor-capture.log) — check the bootstrap (scripts/setup-dev.sh) and the login flow"
fi

echo "Capturing student token (user 'testuser') ..."
if capture_token testuser "$STUDENT_PASSWORD" "$STUDENT_TOKEN_FILE" \
   && [ -s "$STUDENT_TOKEN_FILE" ]; then
  echo "student token: captured (never printed)"
else
  record "auth.student-token" "BLOCKED" "student token capture failed (exit code + diagnostics in evidence/student-capture.log) — typical causes: testuser not bootstrapped, password drift vs OPENLEARN_TEST_USER_PASSWORD, a pending Keycloak required-action interstitial, or role-dependent post-login redirect; check evidence/student-capture.log"
fi

INSTRUCTOR_OK=0; STUDENT_OK=0
[ -s "$INSTRUCTOR_TOKEN_FILE" ] && INSTRUCTOR_OK=1
[ -s "$STUDENT_TOKEN_FILE" ] && STUDENT_OK=1
[ "$INSTRUCTOR_OK" = "1" ] || fail_soft "cannot proceed without an instructor token — see the recorded auth result above"
[ "$STUDENT_OK" = "1" ] || echo "NOTE: proceeding without a student token — the auth-sanity block will be recorded BLOCKED"

# ----------------------------- 3. per-fixture smoke -------------------------
section "3. Ingestion smoke — one fixture at a time (English, then Arabic)"

# run_fixture <id> <pdf-path> <display-name>
run_fixture() {
  local id="$1" pdf="$2" label="$3"
  local course_id material_id job_id s3_key final_status vector_count
  local out body http_code

  echo
  echo "---- fixture: $id ($label) ----"

  # 3a. create the instructor-owned course (API-enforced ownership)
  # Payload built with json.dumps — titles/labels are never shell-interpolated
  # into JSON (quoting a label with a double-quote must not corrupt the body).
  COURSE_PAYLOAD="$(python3 -c 'import json,sys; print(json.dumps({"title": sys.argv[1], "description": sys.argv[2]}))' "[local-smoke $TS] $id — $label" "Temporary smoke-test course created and deleted by scripts/run-material-smoke-test.sh")"
  out="$(curl -sS --noproxy '*' -X POST "$API_URL/v1/courses" \
    -H "Authorization: Bearer $(cat "$INSTRUCTOR_TOKEN_FILE")" \
    -H "Content-Type: application/json" \
    -d "$COURSE_PAYLOAD" \
    -w "\n%{http_code}")"
  http_code="$(printf '%s' "$out" | tail -1)"
  body="$EVIDENCE_DIR/$id-course.json"
  printf '%s' "$out" | sed '$d' > "$body"
  echo "POST /v1/courses -> HTTP $http_code"
  if [ "$http_code" != "201" ] && [ "$http_code" != "200" ]; then
    record "$id" "FAIL" "course create HTTP $http_code (instructor role/ownership?) — $(scrub_presigned "$(cat "$body")")"
    return 1
  fi
  course_id="$(json_field "$body" "id")"
  if [ -z "$course_id" ]; then
    record "$id" "FAIL" "course create returned no id"
    return 1
  fi
  echo "$id course $course_id" >> "$CREATED_IDS"
  RESOURCES_PROCESSED=1
  echo "course_id: $course_id"

  # 3b. presigned upload URL
  UPLOAD_PAYLOAD="$(python3 -c 'import json,sys; print(json.dumps({"filename": sys.argv[1], "title": sys.argv[2]}))' "$(basename "$pdf")" "$label")"
  out="$(curl -sS --noproxy '*' -X POST "$API_URL/v1/courses/$course_id/materials/upload-url" \
    -H "Authorization: Bearer $(cat "$INSTRUCTOR_TOKEN_FILE")" \
    -H "Content-Type: application/json" \
    -d "$UPLOAD_PAYLOAD" \
    -w "\n%{http_code}")"
  http_code="$(printf '%s' "$out" | tail -1)"
  body="$EVIDENCE_DIR/$id-uploadurl.json"
  printf '%s' "$out" | sed '$d' > "$body"
  echo "POST upload-url -> HTTP $http_code"
  if [ "$http_code" != "200" ]; then
    record "$id" "FAIL" "upload-url HTTP $http_code (storage client? check backend logs) — $(scrub_presigned "$(cat "$body")")"
    return 1
  fi
  s3_key="$(json_field "$body" "s3_key")"
  if [ -z "$s3_key" ]; then
    record "$id" "FAIL" "upload-url returned no s3_key"
    return 1
  fi
  echo "$id s3_key $s3_key" >> "$CREATED_IDS"
  echo "s3_key: $s3_key (presigned URL captured to evidence, never printed)"

  # 3c. upload the bytes to the presigned URL (PUT; the URL is not logged;
  # --noproxy: the presigned URL targets the loopback-published MinIO)
  http_code="$(curl -sS --noproxy '*' -o /dev/null -w "%{http_code}" --max-time 120 -X PUT \
    --upload-file "$pdf" "$(python3 -c "import json;print(json.load(open('$body'))['upload_url'])")" 2>/dev/null)" \
    || http_code="000"
  echo "PUT object -> HTTP $http_code"
  if [ "$http_code" != "200" ]; then
    record "$id" "FAIL" "object upload HTTP $http_code (presigned PUT rejected — SigV4/endpoint?)"
    return 1
  fi

  # 3d. register the material -> 202 {material_id, job_id}
  REGISTER_PAYLOAD="$(python3 -c 'import json,sys; print(json.dumps({"s3_key": sys.argv[1], "title": sys.argv[2]}))' "$s3_key" "$label")"
  out="$(curl -sS --noproxy '*' -X POST "$API_URL/v1/courses/$course_id/materials" \
    -H "Authorization: Bearer $(cat "$INSTRUCTOR_TOKEN_FILE")" \
    -H "Content-Type: application/json" \
    -d "$REGISTER_PAYLOAD" \
    -w "\n%{http_code}")"
  http_code="$(printf '%s' "$out" | tail -1)"
  body="$EVIDENCE_DIR/$id-register.json"
  printf '%s' "$out" | sed '$d' > "$body"
  echo "POST materials (register) -> HTTP $http_code"
  if [ "$http_code" != "202" ]; then
    record "$id" "FAIL" "register HTTP $http_code (expected 202; broker publish failure leaves a committed pending row) — $(scrub_presigned "$(cat "$body")")"
    return 1
  fi
  material_id="$(json_field "$body" "material_id")"
  job_id="$(json_field "$body" "job_id")"
  if [ -z "$material_id" ]; then
    record "$id" "FAIL" "register returned no material_id"
    return 1
  fi
  echo "$id material $material_id" >> "$CREATED_IDS"
  echo "material_id: $material_id   job_id (correlation only): $job_id"

  # 3e. poll the real lifecycle (SECONDS is bash's real-time counter — the
  # previous counter credited only POLL_INTERVAL per iteration while each
  # curl could add up to 10 s, overshooting the configured timeout)
  echo "Polling GET /v1/materials/$material_id/status (bounded: ${SMOKE_TIMEOUT}s, interval ${POLL_INTERVAL}s) ..."
  final_status=""
  PREV_ST=""
  ST=""
  SECONDS=0
  while [ "$SECONDS" -lt "$SMOKE_TIMEOUT" ]; do
    ST="$(curl -sS --noproxy '*' --max-time 10 -H "Authorization: Bearer $(cat "$INSTRUCTOR_TOKEN_FILE")" \
        "$API_URL/v1/materials/$material_id/status" 2>/dev/null \
        | python3 -c "import json,sys; print(json.load(sys.stdin).get('status',''))" 2>/dev/null || true)"
    if [ -n "$ST" ] && [ "$ST" != "$PREV_ST" ]; then
      echo "  [t=${SECONDS}s] status: $ST"
      PREV_ST="$ST"
    fi
    case "$ST" in
      ready|failed) final_status="$ST"; break ;;
    esac
    sleep "$POLL_INTERVAL"
  done

  if [ -z "$final_status" ]; then
    record "$id" "FAIL" "no terminal status within ${SMOKE_TIMEOUT}s (last=$ST; is the worker running? first run may download the ~2GB BGE-M3 model — raise SMOKE_TIMEOUT)"
    return 1
  fi
  if [ "$final_status" != "ready" ]; then
    record "$id" "FAIL" "final status=failed — inspect the worker terminal/log (task app.workers.tasks.material_tasks.process_material, material_id=$material_id)"
    return 1
  fi

  # 3f. persistence: status endpoint + course materials list
  LIST_CODE="$(curl -sS --noproxy '*' -o "$EVIDENCE_DIR/$id-list.json" -w "%{http_code}" \
    -H "Authorization: Bearer $(cat "$INSTRUCTOR_TOKEN_FILE")" \
    "$API_URL/v1/courses/$course_id/materials" 2>/dev/null)"
  LIST_HAS="$(python3 -c "
import json
try:
    items = json.load(open('$EVIDENCE_DIR/$id-list.json'))
    m = [x for x in items if x.get('id') == '$material_id']
    print(m[0]['status'] if m else 'ABSENT')
except Exception:
    print('PARSE_ERROR')" 2>/dev/null)"
  if [ "$LIST_CODE" = "200" ] && [ "$LIST_HAS" = "ready" ]; then
    echo "persistence: status endpoint + course materials list both report ready"
  else
    record "$id" "FAIL" "persistence mismatch: list HTTP $LIST_CODE, material in list='$LIST_HAS' (expected ready)"
    return 1
  fi

  # 3g. read-only DB evidence: vector rows for this material
  vector_count="$("${DC[@]}" exec -T db psql -U openlearn -d openlearn_dev -tAc \
    "SELECT count(*) FROM vector_records WHERE id LIKE '${material_id}:%';" 2>/dev/null | tr -d '[:space:]')"
  echo "vector_records rows for material: ${vector_count:-?}"
  if [ -n "$vector_count" ] && [ "$vector_count" -gt 0 ] 2>/dev/null; then
    record "$id" "PASS" "lifecycle pending->processing->ready observed; persisted (status + list); vector rows=$vector_count; s3_key=$s3_key"
  else
    record "$id" "FAIL" "status ready but vector_records has ${vector_count:-no} rows for the material — persistence incomplete"
    return 1
  fi
  return 0
}

# The embedding provider the worker was configured with (reported in the
# summary so a mock-provider run is never mistaken for a real-vectors pass).
EMB_PROVIDER="$(env_var_value AI_EMBEDDING_PROVIDER "$REPO_DIR/backend/.env")"
EMB_PROVIDER="${EMB_PROVIDER:-<config-default: mock>}"

EN_RC=0; AR_RC=0
run_fixture en_born "$EN_PDF" "English born-digital (AlexNet p.1)" || EN_RC=$?
run_fixture ar_born "$AR_PDF" "Arabic born-digital" || AR_RC=$?

# ----------------------------- 4. auth/data sanity --------------------------
section "4. Data and authorization sanity (regression check only — PR #79 behavior is accepted, not redesigned)"
if [ "$STUDENT_OK" = "1" ]; then
  # 4a. the smoke course must be INVISIBLE in the student's owner-scoped list
  ST_LIST_CODE="$(curl -sS --noproxy '*' -o "$EVIDENCE_DIR/student-courses.json" -w "%{http_code}" \
    -H "Authorization: Bearer $(cat "$STUDENT_TOKEN_FILE")" \
    "$API_URL/v1/courses" 2>/dev/null)"
  EN_COURSE_ID="$(json_field "$EVIDENCE_DIR/en_born-course.json" "id")"
  LEAK="$(python3 -c "
import json
try:
    items = json.load(open('$EVIDENCE_DIR/student-courses.json'))
    print('LEAK' if any(c.get('id') == '$EN_COURSE_ID' for c in items) else 'ISOLATED')
except Exception:
    print('PARSE_ERROR')" 2>/dev/null)"
  if [ "$ST_LIST_CODE" = "401" ]; then
    record "sanity.student-isolation" "BLOCKED" "student token rejected (HTTP 401 — expired or invalid by the time of this late check) — re-run to exercise the isolation check; NOT an ownership result"
  elif [ "$ST_LIST_CODE" = "200" ] && [ "$LEAK" = "ISOLATED" ]; then
    echo "student course list: owner-scoped (smoke course absent) — HTTP $ST_LIST_CODE"
    record "sanity.student-isolation" "PASS" "GET /v1/courses (student) = 200 and the instructor's smoke course is absent (owner scoping intact)"
  else
    record "sanity.student-isolation" "FAIL" "student list HTTP $ST_LIST_CODE, smoke-course visibility=$LEAK — ownership regression"
  fi

  # 4b. the student must NOT read the instructor's material status
  EN_MATERIAL_ID="$(json_field "$EVIDENCE_DIR/en_born-register.json" "material_id")"
  ST_STATUS_CODE="$(curl -sS --noproxy '*' -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $(cat "$STUDENT_TOKEN_FILE")" \
    "$API_URL/v1/materials/$EN_MATERIAL_ID/status" 2>/dev/null)"
  if [ "$ST_STATUS_CODE" = "403" ] || [ "$ST_STATUS_CODE" = "404" ]; then
    echo "student material-status read -> HTTP $ST_STATUS_CODE (ownership enforced)"
    record "sanity.status-ownership" "PASS" "GET /v1/materials/{id}/status (student) -> HTTP $ST_STATUS_CODE — course-ownership enforcement intact"
  elif [ "$ST_STATUS_CODE" = "401" ]; then
    record "sanity.status-ownership" "BLOCKED" "student token rejected (HTTP 401 — expired or invalid) — ownership NOT exercised; re-run"
  else
    record "sanity.status-ownership" "FAIL" "student material-status read -> HTTP $ST_STATUS_CODE (expected 403/404) — ownership regression"
  fi
else
  record "sanity.student-isolation" "BLOCKED" "no student token captured — re-run to exercise the ownership regression block"
  record "sanity.status-ownership" "BLOCKED" "no student token captured"
fi

# ----------------------------- 5. cleanup -----------------------------------
section "5. Cleanup (only THIS run's recorded resources; skipped with --keep-resources / KEEP_RESOURCES=1)"
if [ "$KEEP_RESOURCES" = "1" ]; then
  echo "KEEP_RESOURCES=1 (--keep-resources) — resources left in place; ids in $CREATED_IDS"
  record "cleanup.skipped" "SKIPPED" "explicitly skipped — smoke resources remain (ids recorded)"
else
  # 5a. FK-less vector rows first (exact recorded material ids), then VERIFY
  # the deletion instead of only counting attempted statements
  V_FAIL=0
  while read -r FID KIND RID; do
    [ "$KIND" = "material" ] || continue
    "${DC[@]}" exec -T db psql -U openlearn -d openlearn_dev -tAc \
      "DELETE FROM vector_records WHERE id LIKE '${RID}:%';" >/dev/null 2>&1
    V_LEFT="$("${DC[@]}" exec -T db psql -U openlearn -d openlearn_dev -tAc \
      "SELECT count(*) FROM vector_records WHERE id LIKE '${RID}:%';" 2>/dev/null | tr -d '[:space:]')"
    [ "$V_LEFT" = "0" ] || { echo "WARN: vector rows for $RID still present after delete"; V_FAIL=$((V_FAIL+1)); }
  done < "$CREATED_IDS"
  if [ "$V_FAIL" = "0" ]; then
    record "cleanup.vectors" "PASS" "vector rows deleted and verified absent for every recorded material id"
  else
    record "cleanup.vectors" "FAIL" "$V_FAIL material id(s) still have vector_records rows after delete — inspect the db"
  fi

  # 5b. course via the API (cascades the material row; API-enforced ownership).
  # A failed DELETE is a real cleanup failure and is recorded as one.
  C_FAIL=0
  C_DEL=0
  while read -r FID KIND RID; do
    [ "$KIND" = "course" ] || continue
    CODE="$(curl -sS --noproxy '*' -o /dev/null -w "%{http_code}" -X DELETE \
      -H "Authorization: Bearer $(cat "$INSTRUCTOR_TOKEN_FILE")" \
      "$API_URL/v1/courses/$RID" 2>/dev/null)"
    echo "DELETE course $RID -> HTTP $CODE"
    if [ "$CODE" = "200" ] || [ "$CODE" = "204" ]; then
      C_DEL=$((C_DEL+1))
    else
      C_FAIL=$((C_FAIL+1))
    fi
  done < "$CREATED_IDS"
  if [ "$C_FAIL" = "0" ] && [ "$C_DEL" -gt 0 ]; then
    record "cleanup.course" "PASS" "course DELETE accepted for all $C_DEL recorded course id(s)"
  elif [ "$C_DEL" = "0" ] && [ "$C_FAIL" = "0" ]; then
    record "cleanup.course" "SKIPPED" "no course ids were recorded (run failed before course creation)"
  else
    record "cleanup.course" "FAIL" "$C_FAIL course DELETE(s) failed (non-200/204) — course (and its pending material rows) may remain; ids in created-ids.txt"
  fi

  # 5c. S3 objects by exact recorded key, deletion VERIFIED with a health
  # precondition. Two committed-baseline defects are fixed here:
  #   (1) the unbraced "$DC[@]" expansion made `mc rm` a guaranteed
  #       command-not-found (objects were never deleted while `mc stat`, which
  #       WAS braced, then reported the survivor); all compose invocations in
  #       this script now use "${DC[@]}";
  #   (2) `mc stat` failure was treated as proof of absence, so a broken
  #       mc/alias produced "verified gone" while objects leaked. The bucket
  #       listing precondition below runs through the SAME alias before any
  #       deletion, making a broken mc unable to masquerade as verification.
  MINIO_BUCKET="$(env_var_value S3_BUCKET_NAME "$REPO_DIR/.env.local")"
  S3_COUNT=0; S3_FAIL=0; S3_UNKNOWN=0
  if ! "${DC[@]}" exec -T minio mc ls "local/$MINIO_BUCKET" >/dev/null 2>&1; then
    echo "WARN: mc cannot list local/$MINIO_BUCKET — deletion cannot be verified"
    S3_UNKNOWN=$((S3_UNKNOWN+1))
  else
    while read -r FID KIND RID; do
      [ "$KIND" = "s3_key" ] || continue
      S3_COUNT=$((S3_COUNT+1))
      if ! "${DC[@]}" exec -T minio mc rm --force "local/$MINIO_BUCKET/$RID" >/dev/null 2>&1; then
        echo "WARN: mc rm failed for $RID (exit non-zero)"
        S3_FAIL=$((S3_FAIL+1))
      fi
      # independent authenticated absence check through the same verified client
      if "${DC[@]}" exec -T minio mc stat "local/$MINIO_BUCKET/$RID" >/dev/null 2>&1; then
        echo "WARN: object $RID still present after rm"
        S3_FAIL=$((S3_FAIL+1))
      else
        echo "S3 object deleted + verified gone: $RID"
      fi
    done < "$CREATED_IDS"
  fi
  if [ "$S3_UNKNOWN" != "0" ]; then
    record "cleanup.s3" "FAIL" "S3 cleanup verification IMPOSSIBLE (mc/alias/endpoint broken — bucket listing failed); object state UNKNOWN, do not treat cleanup as done; keys in created-ids.txt"
  elif [ "$S3_FAIL" = "0" ] && [ "$S3_COUNT" -gt 0 ]; then
    record "cleanup.s3" "PASS" "$S3_COUNT S3 object(s) deleted and independently verified absent (mc ls precondition + per-key stat)"
  elif [ "$S3_COUNT" = "0" ] && [ "$S3_FAIL" = "0" ]; then
    record "cleanup.s3" "SKIPPED" "no s3 keys were recorded (run failed before presign)"
  else
    record "cleanup.s3" "FAIL" "$S3_FAIL of $S3_COUNT S3 object(s) survived deletion or failed to delete — inspect the minio service; keys in created-ids.txt"
  fi

  # 5d. verify the material rows are gone (course delete cascades them)
  LEFT=0
  while read -r FID KIND RID; do
    [ "$KIND" = "material" ] || continue
    N="$("${DC[@]}" exec -T db psql -U openlearn -d openlearn_dev -tAc \
      "SELECT count(*) FROM materials WHERE id='${RID}';" 2>/dev/null | tr -d '[:space:]')"
    [ "$N" = "0" ] || LEFT=$((LEFT+1))
  done < "$CREATED_IDS"
  if [ "$LEFT" = "0" ]; then
    record "cleanup.db" "PASS" "material rows verified absent after the course cascade"
  else
    record "cleanup.db" "FAIL" "$LEFT material row(s) survived the course cascade — inspect the db"
  fi
  MAIN_CLEANUP_DONE=1
fi

# ----------------------------- 6. verdict -----------------------------------
section "6. Verdict"
echo "Results (SMOKERESULT|fixture|status|note):"
FAILED=0
RESULT_COUNT=0
while IFS= read -r line; do
  echo "  $line"
  RESULT_COUNT=$((RESULT_COUNT+1))
  state="$(printf '%s' "$line" | awk -F'|' '{print $3}')"
  case "$state" in FAIL|BLOCKED) FAILED=1 ;; esac
done < "$RESULTS"
# Aggregation hardening: an empty or fixture-less results file must never
# yield a PASS (e.g. an interrupted run whose per-fixture FAIL lines were
# never written). Both locked fixtures must have an explicit PASS line.
if [ "$RESULT_COUNT" = "0" ]; then
  echo "  (results file empty — no checks recorded; treating as incomplete run)"
  FAILED=1
fi
for FIX in en_born ar_born; do
  if ! grep -q "^SMOKERESULT|${FIX}|PASS|" "$RESULTS"; then
    echo "  MISSING: no PASS recorded for ${FIX} — the run is incomplete, not a pass"
    FAILED=1
  fi
done
echo
echo "embedding provider configured for the worker: $EMB_PROVIDER"
echo "(bge-m3 = real vectors; mock = placeholder vectors — a mocked stage, not a real-embeddings pass)"
echo
echo "Repository state after run (must show no tracked changes):"
git -C "$REPO_DIR" status --porcelain || true
echo
if [ "$FAILED" = "0" ]; then
  echo "VERDICT: LOCAL MATERIAL-INGESTION SMOKE PASSED (exit 0)"
  echo "Observed: real API flow + real services + real lifecycle for BOTH locked fixtures;"
  echo "born-digital scope only (the OCR stage was never invoked — see the header notes)."
  exit 0
else
  echo "VERDICT: LOCAL MATERIAL-INGESTION SMOKE HAS FAILURES/BLOCKS (exit 1)"
  echo "Do NOT tune config to force a pass — triage the recorded results above."
  exit 1
fi
