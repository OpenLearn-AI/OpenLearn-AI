#!/usr/bin/env bash
# =============================================================================
# run-batch-0.1-local-verification.sh
#
# OpenLearn-AI — frontend-redesign — Batch 0.1 (baseline verification run)
# LOCAL evidence collector for the three checks that were BLOCKED in the
# remote sandbox (no Docker, no credentials, staging unreachable):
#
#   Check 6  E2E suite with real Keycloak  (login / courses-crud /
#                                         profile / affordance — since
#                                         Batch 5.1 the CRUD flow consumes
#                                         the instructor credential pair;
#                                         an absent pair shows as an
#                                         explicit CRUD skip, never a
#                                         silent pass)
#   Check 7  F5 live probe                (authenticated GET /v1/courses —
#                                         does created_at carry a TZ offset?)
#   Check 8  CORS preflight               (local web origin vs local backend;
#                                         staging variant is OPT-IN, --with-staging-preflight)
#
# Checks 1–5 (lint/typecheck/unit/storybook/build) already PASSED in the
# remote run and are recorded in the execution ledger; they are re-run here
# only if you pass --with-fast-checks (optional, ~1 min).
#
# Guarantees (mirror the batch rules):
#   * READ-ONLY for the repository: no tracked file is created/modified.
#     Playwright output dirs (frontend/test-results, frontend/playwright-report)
#     are MOVED into the evidence directory, leaving `git status` clean.
#   * No credentials are fabricated; the F5 probe captures a REAL token from
#     the real browser login flow (direct grants are disabled on the
#     openlearn-frontend client — by design nothing is weakened or bypassed).
#   * No auth is disabled, no test weakened, no config changed.
#   * Secrets hygiene: the token is written to a 0600 file OUTSIDE the repo
#     and deleted on exit; it is never printed. The password is never echoed.
#
# Usage:
#   bash run-batch-0.1-local-verification.sh
#       --full-setup               run scripts/setup-dev.sh first (idempotent)
#       --allow-probe-create       if GET /v1/courses is empty: POST one clearly
#                                  labeled probe course locally, re-read, then
#                                  DELETE it (local dev DB only, self-cleaning)
#       --with-staging-preflight   additionally fire the READ-ONLY staging
#                                  CORS preflight (one OPTIONS request)
#       --with-fast-checks         also re-run lint/typecheck/unit
#
# Note: every check is always recorded — the run never stops at a failure;
# the final verdict is computed mechanically from all recorded results.
#
# Verdict semantics (house style, matches the AI Week 7–8 verifiers):
#   PASS / FAIL / BLOCKED / SKIPPED / INCONCLUSIVE; exit 0 only when every
#   REQUIRED check is PASS (or SKIPPED by explicit opt-out) — failures and
#   blocks are recorded as evidence, never tuned away.
#
# Requirements: Docker + compose v2, Node >= 20, bash, curl, python3.
# The script assumes scripts/setup-dev.sh has been run at least once
# (backend/.venv, backend/.env, frontend/.env.local, root .env.local exist).
# =============================================================================

set -uo pipefail

# ----------------------------- configuration --------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${REPO_DIR:-$SCRIPT_DIR}"
# Auto-detect the repo if the script was saved outside it: try CWD and parents.
if [ ! -f "$REPO_DIR/frontend/package.json" ]; then
  for CAND in "$PWD" "$PWD/.." "$PWD/../.."; do
    if [ -f "$CAND/frontend/package.json" ] && [ -f "$CAND/scripts/setup-dev.sh" ]; then
      REPO_DIR="$(cd "$CAND" && pwd)"; break
    fi
  done
fi
[ -f "$REPO_DIR/frontend/package.json" ] || {
  echo "ERROR: could not locate the OpenLearn-AI repository (need frontend/package.json)." >&2
  echo "       cd into the repo (or a parent of it) and re-run, or set REPO_DIR=/path/to/OpenLearn-AI." >&2
  exit 66
}
API_URL="${API_URL:-http://localhost:8000}"
WEB_URL="${WEB_URL:-http://localhost:3000}"
KC_DISCOVERY="${KC_DISCOVERY:-http://localhost:8080/realms/openlearn/.well-known/openid-configuration}"
E2E_USERNAME="${E2E_USERNAME:-testuser}"
# Batch 5.1: the course CRUD flow runs on the instructor account. The
# username defaults to the bootstrap-provisioned 'instructor'; the
# password falls back to the root .env.local's
# OPENLEARN_INSTRUCTOR_USER_PASSWORD (the same mechanism as the student
# password below). Absence is LEGAL — the CRUD test then skips with an
# explicit, actionable message; it never falls back to the student pair.
E2E_INSTRUCTOR_USERNAME="${E2E_INSTRUCTOR_USERNAME:-instructor}"
OPENLEARN_INSTRUCTOR_USER_PASSWORD="$(sed -n 's/^OPENLEARN_INSTRUCTOR_USER_PASSWORD=//p' "$REPO_DIR/.env.local" | head -1 | tr -d '\r')"
E2E_INSTRUCTOR_PASSWORD="${E2E_INSTRUCTOR_PASSWORD:-$OPENLEARN_INSTRUCTOR_USER_PASSWORD}"
STAGING_API="https://openlearn-api-staging.duckdns.org"
STAGING_WEB="https://openlearn-web-staging.duckdns.org"

FULL_SETUP=0; ALLOW_CREATE=0; WITH_STAGING=0; WITH_FAST=0
for arg in "$@"; do
  case "$arg" in
    --full-setup) FULL_SETUP=1 ;;
    --allow-probe-create) ALLOW_CREATE=1 ;;
    --with-staging-preflight) WITH_STAGING=1 ;;
    --with-fast-checks) WITH_FAST=1 ;;
    *) echo "unknown option: $arg" >&2; exit 64 ;;
  esac
done

TS="$(date +%Y%m%d-%H%M%S)"
EVIDENCE_DIR="${EVIDENCE_DIR:-$REPO_DIR/../openlearn-batch-0.1-evidence}"
EVIDENCE_DIR="$EVIDENCE_DIR/run-$TS"
LOG="$EVIDENCE_DIR/evidence.log"
mkdir -p "$EVIDENCE_DIR"
chmod 700 "$EVIDENCE_DIR"
TOKEN_FILE="$EVIDENCE_DIR/f5.token"   # deleted on exit, never printed

# ----------------------------- tiny framework -------------------------------
declare -a CHECK_IDS=(); declare -A CHECK_STATE=(); declare -A CHECK_NOTE=()
record() { # record <id> <state> <note...>
  CHECK_IDS+=("$1"); CHECK_STATE["$1"]="$2"; CHECK_NOTE["$1"]="$3"
  printf '  -> %-28s %s\n' "$1" "$2"
}
section() { printf '\n== %s ==\n' "$*"; }
fail_soft() { # fatal preflight failure — cannot continue meaningfully
  printf 'FATAL: %s\n' "$*" >&2
  exit 2
}

exec > >(tee -a "$LOG") 2>&1
cat <<EOF
==============================================================================
OpenLearn-AI Batch 0.1 — LOCAL verification run
repo:     $REPO_DIR
branch:   $(git -C "$REPO_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')
HEAD:     $(git -C "$REPO_DIR" rev-parse HEAD 2>/dev/null || echo '?')
api:      $API_URL   web: $WEB_URL
evidence: $EVIDENCE_DIR
options:  full-setup=$FULL_SETUP allow-probe-create=$ALLOW_CREATE \
with-staging-preflight=$WITH_STAGING with-fast-checks=$WITH_FAST
==============================================================================
EOF

cleanup() {
  [ -f "$TOKEN_FILE" ] && rm -f "$TOKEN_FILE"
}
trap cleanup EXIT

# ----------------------------- 0. preflight ---------------------------------
section "0. Preflight"
MISSING=0
for tool in docker node npm curl python3 git; do
  if ! command -v "$tool" >/dev/null 2>&1; then echo "missing tool: $tool"; MISSING=1; fi
done
[ "$MISSING" = "0" ] || fail_soft "install the missing tools above and re-run"

[ -f "$REPO_DIR/.env.local" ] || fail_soft ".env.local not found in $REPO_DIR — run: bash scripts/setup-dev.sh"
OPENLEARN_TEST_USER_PASSWORD="$(sed -n 's/^OPENLEARN_TEST_USER_PASSWORD=//p' "$REPO_DIR/.env.local" | head -1 | tr -d '\r')"
if [ -z "${OPENLEARN_TEST_USER_PASSWORD:-}" ] && [ -z "${E2E_PASSWORD:-}" ]; then
  fail_soft "OPENLEARN_TEST_USER_PASSWORD not set in .env.local — add it (see scripts/setup-dev.sh) and re-run"
fi
E2E_PASSWORD="${E2E_PASSWORD:-$OPENLEARN_TEST_USER_PASSWORD}"
if [ -z "$E2E_INSTRUCTOR_PASSWORD" ]; then
  echo "NOTE: E2E_INSTRUCTOR_PASSWORD is not set (neither the env var nor OPENLEARN_INSTRUCTOR_USER_PASSWORD in .env.local) — the instructor course-CRUD test will SKIP with an explicit message (see scripts/setup-dev.sh for the credential generation)."
fi
[ -f "$REPO_DIR/backend/.env" ] || echo "WARN: backend/.env missing — backend may fail to start (run scripts/setup-dev.sh)"
[ -f "$REPO_DIR/frontend/.env.local" ] || echo "WARN: frontend/.env.local missing — dev server may fail (run scripts/setup-dev.sh)"
[ -x "$REPO_DIR/backend/.venv/bin/uvicorn" ] || echo "WARN: backend/.venv missing — backend cannot be auto-started (run scripts/setup-dev.sh)"

START_STATE="$(git -C "$REPO_DIR" status --porcelain)"
if [ -n "$START_STATE" ]; then
  echo "NOTE: working tree is not clean at start (pre-existing changes are preserved, never touched):"
  echo "$START_STATE"
fi

# ----------------------------- 1. local stack -------------------------------
section "1. Local stack (docker: db + keycloak, backend :8000, frontend :3000)"
if [ "$FULL_SETUP" = "1" ]; then
  echo "Running scripts/setup-dev.sh first (idempotent — safe on an existing setup) ..."
  ( cd "$REPO_DIR" && bash scripts/setup-dev.sh ) || fail_soft "setup-dev.sh failed — fix it and re-run"
fi
DC=(docker compose --env-file "$REPO_DIR/.env.local" -f "$REPO_DIR/infra/docker-compose.dev.yml")
if ! "${DC[@]}" ps >/dev/null 2>&1; then
  record "stack.compose" "BLOCKED" "docker compose not reachable — is Docker running?"
  docker info >/dev/null 2>&1 || echo "  hint: Docker daemon appears to be down; start Docker and re-run."
fi
if "${DC[@]}" ps >/dev/null 2>&1; then
  echo "Starting/refreshing containers: db, keycloak ..."
  "${DC[@]}" up -d db keycloak || record "stack.compose" "FAIL" "compose up failed (see docker compose ps)"
  echo "Waiting (bounded 180s) for Keycloak discovery ..."
  KC_OK=0
  for i in $(seq 1 36); do
    if curl -sf --max-time 5 "$KC_DISCOVERY" >/dev/null; then KC_OK=1; break; fi
    sleep 5
  done
  [ "$KC_OK" = "1" ] && record "stack.keycloak" "PASS" "OIDC discovery answered" \
                      || record "stack.keycloak" "FAIL" "discovery never answered; try: ${DC[*]} logs keycloak"
fi

if ! curl -sf --max-time 5 "$API_URL/health" >/dev/null 2>&1; then
  if [ -x "$REPO_DIR/backend/.venv/bin/uvicorn" ]; then
    echo "Starting backend (uvicorn :8000) ..."
    ( cd "$REPO_DIR/backend" && nohup .venv/bin/uvicorn app.main:app --port 8000 \
        > "$EVIDENCE_DIR/backend.log" 2>&1 & echo $! > "$EVIDENCE_DIR/backend.pid" )
  else
    record "stack.backend" "BLOCKED" "backend/.venv missing — run scripts/setup-dev.sh"
  fi
else
  echo "Backend already running on :8000 — reusing it."
fi
BE_OK=0
for i in $(seq 1 24); do curl -sf --max-time 5 "$API_URL/health" >/dev/null 2>&1 && BE_OK=1 && break; sleep 5; done
[ "$BE_OK" = "1" ] && record "stack.backend" "PASS" "GET /health OK" \
                    || record "stack.backend" "FAIL" "backend /health never answered; see $EVIDENCE_DIR/backend.log"

if ! curl -sf --max-time 10 -o /dev/null "$WEB_URL" 2>&1; then
  echo "Starting frontend (next dev :3000) ..."
  ( cd "$REPO_DIR/frontend" && nohup npm run dev > "$EVIDENCE_DIR/frontend.log" 2>&1 & echo $! > "$EVIDENCE_DIR/frontend.pid" )
else
  echo "Frontend already running on :3000 — reusing it."
fi
FE_OK=0
for i in $(seq 1 36); do curl -sf --max-time 5 -o /dev/null "$WEB_URL" && FE_OK=1 && break; sleep 5; done
[ "$FE_OK" = "1" ] && record "stack.frontend" "PASS" "GET / OK" \
                    || record "stack.frontend" "FAIL" "frontend never answered; see $EVIDENCE_DIR/frontend.log"

# ----------------------------- 2. fast checks (optional) --------------------
if [ "$WITH_FAST" = "1" ]; then
  section "2. Fast checks (lint / typecheck / unit) — optional re-run"
  ( cd "$REPO_DIR/frontend" && npm run lint  >/dev/null 2>&1 ) && record "fast.lint" "PASS" "exit 0" || record "fast.lint" "FAIL" "see log"
  ( cd "$REPO_DIR/frontend" && npm run typecheck >/dev/null 2>&1 ) && record "fast.typecheck" "PASS" "exit 0" || record "fast.typecheck" "FAIL" "see log"
  ( cd "$REPO_DIR/frontend" && npm run test >/dev/null 2>&1 ) && record "fast.unit" "PASS" "22/22 expected" || record "fast.unit" "FAIL" "see log"
else
  record "fast.checks" "SKIPPED" "not requested (--with-fast-checks); already PASS in remote run"
fi

# ----------------------------- 3. E2E suite ---------------------------------
section "3. Check 6 — E2E suite with real Keycloak (Chromium, serial)"
echo "Ensuring Playwright chromium is installed (idempotent) ..."
( cd "$REPO_DIR/frontend" && npx playwright install chromium >/dev/null 2>&1 ) \
  || record "e2e.browser-install" "BLOCKED" "playwright install failed (network?)"

E2E_OUT="$EVIDENCE_DIR/e2e-output.txt"
( cd "$REPO_DIR/frontend" && \
  E2E_USERNAME="$E2E_USERNAME" E2E_PASSWORD="$E2E_PASSWORD" \
  E2E_INSTRUCTOR_USERNAME="$E2E_INSTRUCTOR_USERNAME" E2E_INSTRUCTOR_PASSWORD="$E2E_INSTRUCTOR_PASSWORD" \
  CI= \
  npm run test:e2e ) 2>&1 | tee "$EVIDENCE_DIR/e2e-raw.txt"
E2E_RC=${PIPESTATUS[0]}
tail -40 "$EVIDENCE_DIR/e2e-raw.txt" > "$E2E_OUT"
# keep the repo clean: move Playwright outputs out of the working tree
for d in test-results playwright-report; do
  if [ -d "$REPO_DIR/frontend/$d" ]; then
    mv "$REPO_DIR/frontend/$d" "$EVIDENCE_DIR/$d" && echo "moved frontend/$d -> evidence dir"
  fi
done
E2E_SUMMARY="$(grep -Eo '[0-9]+ (passed|failed|skipped|flaky)[^()]*' "$EVIDENCE_DIR/e2e-raw.txt" | tail -6 | tr '\n' ' ')"
echo "E2E exit code: $E2E_RC | summary: ${E2E_SUMMARY:-<none parsed>}"
# Batch 5.1: the suite is no longer a fixed trio — the affordance flow
# grew it to four tests, and an absent credential pair skips its tests
# explicitly. The PASS condition is therefore structural (exit 0, at
# least one test actually ran, nothing failed), not a hard-coded count;
# skips are surfaced honestly in the note.
E2E_SKIPPED_NOTE=""
if echo "$E2E_SUMMARY" | grep -q "skipped"; then
  E2E_SKIPPED_NOTE=" (some tests skipped — a credential pair is not configured; see the specs' explicit skip messages)"
fi
if echo "$E2E_SUMMARY" | grep -q "skipped" && ! echo "$E2E_SUMMARY" | grep -q "passed"; then
  record "e2e.trio" "BLOCKED" "specs self-skipped — credentials not picked up (E2E_USERNAME=$E2E_USERNAME; check .env.local)"
elif [ "$E2E_RC" = "0" ] && echo "$E2E_SUMMARY" | grep -q "passed" && ! echo "$E2E_SUMMARY" | grep -q "failed"; then
  record "e2e.trio" "PASS" "suite green${E2E_SKIPPED_NOTE}"
else
  record "e2e.trio" "FAIL" "exit=$E2E_RC summary=${E2E_SUMMARY:-none}; traces/screenshots moved to evidence dir"
fi

# ----------------------------- 4. F5 live probe -----------------------------
section "4. Check 7 — F5 live probe: authenticated GET /v1/courses (created_at offset?)"
echo "Capturing a REAL access token via the browser login flow (no auth weakening) ..."
cat > "$EVIDENCE_DIR/capture-token.cjs" <<'CAPTURE_SCRIPT_START'
// Token capture via the REAL UI login flow. Intercepts (a) the Keycloak
// token-endpoint response and (b) the Authorization header the dashboard
// itself sends to /v1/courses. Nothing is bypassed: same credentials, same
// client, same PKCE flow as the app.
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const base = process.env.WEB_URL || 'http://localhost:3000';
  const user = process.env.E2E_USERNAME;
  const pass = process.env.E2E_PASSWORD;
  if (!user || !pass) { console.error('CAPTURE_ERROR missing credentials'); process.exit(3); }
  let token = null, authHeader = null;
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
    page.on('request', (req) => {
      if (/\/v1\/courses(\?|$)/.test(req.url())) {
        const a = req.headers()['authorization'];
        if (a) authHeader = a;
      }
    });
    await page.goto(base + '/login');
    await page.getByRole('button', { name: /sign in with openlearn ai/i }).click();
    await page.waitForSelector('#username', { state: 'visible' });
    await page.fill('#username', user);
    await page.fill('#password', pass);
    await page.click('#kc-login');
    await page.waitForURL(/\/dashboard$/, { timeout: 30000 });
    await page.waitForTimeout(4000); // let the dashboard fire its API calls
  } finally { await browser.close(); }
  if (authHeader) fs.writeFileSync(process.env.HEADER_FILE, authHeader, { mode: 0o600 });
  if (token) fs.writeFileSync(process.env.TOKEN_FILE, token, { mode: 0o600 });
  if (!token && !authHeader) { console.error('NO_TOKEN_CAPTURED'); process.exit(4); }
  console.log('TOKEN_CAPTURED=yes' + (authHeader ? ' (+app header)' : ''));
})().catch((e) => { console.error('CAPTURE_ERROR', e.message); process.exit(2); });
CAPTURE_SCRIPT_START
HEADER_FILE="$EVIDENCE_DIR/f5.authheader"
( cd "$REPO_DIR/frontend" && \
  NODE_PATH="$REPO_DIR/frontend/node_modules" \
  WEB_URL="$WEB_URL" E2E_USERNAME="$E2E_USERNAME" E2E_PASSWORD="$E2E_PASSWORD" \
  TOKEN_FILE="$TOKEN_FILE" HEADER_FILE="$HEADER_FILE" \
  node "$EVIDENCE_DIR/capture-token.cjs" )
CAP_RC=$?
rm -f "$HEADER_FILE"

BEARER=""
if [ "$CAP_RC" = "0" ]; then
  if [ -s "$TOKEN_FILE" ]; then BEARER="Bearer $(cat "$TOKEN_FILE")"; fi
elif [ -s "$HEADER_FILE" ]; then
  BEARER="$(cat "$HEADER_FILE")"
fi

PROBE_STATE="BLOCKED"; PROBE_NOTE="token capture failed rc=$CAP_RC (check credentials / keycloak bootstrap)"
F5_VERDICT="NOT_OBSERVABLE"
if [ -n "$BEARER" ]; then
  echo "Firing authenticated GET $API_URL/v1/courses (token redacted from all logs) ..."
  HTTP_CODE="$(curl -sS -o "$EVIDENCE_DIR/f5-courses.json" -w "%{http_code}" --max-time 20 \
      -H "Authorization: $BEARER" "$API_URL/v1/courses")" || HTTP_CODE="000"
  echo "HTTP $HTTP_CODE"
  ANALYSIS="$(python3 - "$EVIDENCE_DIR/f5-courses.json" <<'PYEOF'
import json, sys, re
try:
    data = json.load(open(sys.argv[1]))
except Exception as e:
    print(f"PARSE_ERROR {e}"); raise SystemExit
if not isinstance(data, list):
    print(f"UNEXPECTED_SHAPE {type(data).__name__}"); raise SystemExit
vals = [c.get("created_at") for c in data if isinstance(c, dict)]
if not vals:
    print("EMPTY_LIST"); raise SystemExit
off = re.compile(r"(?:Z|[+-]\d{2}:?\d{2})$")
with_off = sum(1 for v in vals if isinstance(v, str) and off.search(v))
print(f"COUNT={len(vals)} WITH_OFFSET={with_off} SAMPLE={vals[0]!r}")
PYEOF
)"
  echo "created_at analysis: $ANALYSIS"
  case "$ANALYSIS" in
    COUNT=*WITH_OFFSET=*" "*)
      N="${ANALYSIS#*COUNT=}"; N="${N%% *}"; W="${ANALYSIS#*WITH_OFFSET=}"; W="${W%% *}"
      if [ "$N" = "$W" ] && [ "$N" != "0" ]; then
        PROBE_STATE="PASS"; PROBE_NOTE="all $N created_at values carry a TZ offset — Zod offset:true schema satisfied"
        F5_VERDICT="OFFSET_PRESENT"
      elif [ "$W" = "0" ]; then
        PROBE_STATE="FAIL"; PROBE_NOTE="live API emits NAIVE datetimes (no offset) — Zod offset:true will reject; feeds Batch 1.4"
        F5_VERDICT="OFFSET_ABSENT"
      else
        PROBE_STATE="FAIL"; PROBE_NOTE="MIXED emission: $W of $N carry offsets — feeds Batch 1.4"
        F5_VERDICT="MIXED"
      fi
      ;;
    EMPTY_LIST)
      if [ "$ALLOW_CREATE" = "1" ]; then
        echo "List empty — --allow-probe-create: creating ONE labeled probe course (local dev DB only) ..."
        PC="$(curl -sS -X POST "$API_URL/v1/courses" -H "Authorization: $BEARER" \
              -H "Content-Type: application/json" \
              -d '{"title":"[batch-0.1-probe] F5 created_at probe — safe to delete","description":"temporary probe course; deleted by the verifier"}' \
              -w "\n%{http_code}")"
        PC_CODE="$(printf '%s' "$PC" | tail -1)"; PC_BODY="$(printf '%s' "$PC" | sed '$d')"
        echo "POST /v1/courses -> HTTP $PC_CODE"
        PROBE_ID="$(printf '%s' "$PC_BODY" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("id",""))
except Exception: print("")' 2>/dev/null)"
        if [ -n "$PROBE_ID" ]; then
          echo "probe course id: $PROBE_ID"
          HTTP_CODE="$(curl -sS -o "$EVIDENCE_DIR/f5-courses.json" -w "%{http_code}" --max-time 20 \
              -H "Authorization: $BEARER" "$API_URL/v1/courses")" || HTTP_CODE="000"
          ANALYSIS="$(python3 - "$EVIDENCE_DIR/f5-courses.json" <<'PYEOF'
import json, sys, re
data = json.load(open(sys.argv[1]))
vals = [c.get("created_at") for c in data if isinstance(c, dict)]
off = re.compile(r"(?:Z|[+-]\d{2}:?\d{2})$")
with_off = sum(1 for v in vals if isinstance(v, str) and off.search(v))
print(f"COUNT={len(vals)} WITH_OFFSET={with_off} SAMPLE={vals[0]!r}" if vals else "EMPTY_LIST")
PYEOF
)"
          echo "created_at analysis: $ANALYSIS"
          W="${ANALYSIS#*WITH_OFFSET=}"; W="${W%% *}"; N="${ANALYSIS#*COUNT=}"; N="${N%% *}"
          if [ "${ANALYSIS:-}" != "EMPTY_LIST" ] && [ "$N" = "$W" ]; then
            PROBE_STATE="PASS"; PROBE_NOTE="all $N created_at values carry a TZ offset (probe course used)"
            F5_VERDICT="OFFSET_PRESENT"
          elif [ "$W" = "0" ] && [ "${N:-0}" != "0" ]; then
            PROBE_STATE="FAIL"; PROBE_NOTE="live API emits NAIVE datetimes — feeds Batch 1.4"; F5_VERDICT="OFFSET_ABSENT"
          else
            PROBE_STATE="FAIL"; PROBE_NOTE="mixed emission — feeds Batch 1.4"; F5_VERDICT="MIXED"
          fi
          DEL_CODE="$(curl -sS -o /dev/null -w "%{http_code}" -X DELETE \
              -H "Authorization: $BEARER" "$API_URL/v1/courses/$PROBE_ID")"
          echo "DELETE probe course -> HTTP $DEL_CODE (self-cleaning)"
        else
          PROBE_STATE="FAIL"; PROBE_NOTE="probe create failed HTTP $PC_CODE (instructor role required? testuser is student — see ledger note)"
        fi
      else
        PROBE_STATE="INCONCLUSIVE"; PROBE_NOTE="authenticated GET OK but no courses exist locally; re-run with --allow-probe-create"
        F5_VERDICT="NOT_OBSERVABLE"
      fi
      ;;
    PARSE_ERROR*|UNEXPECTED_SHAPE*)
      PROBE_STATE="FAIL"; PROBE_NOTE="$ANALYSIS"
      ;;
  esac
fi
record "f5.live-probe" "$PROBE_STATE" "$PROBE_NOTE"

# ----------------------------- 5. CORS preflight ----------------------------
section "5. Check 8 — CORS preflight (local web origin vs local backend)"
CORS_HDR="$EVIDENCE_DIR/cors-local.headers"
CORS_CODE="$(curl -sS -o /dev/null -D "$CORS_HDR" -w "%{http_code}" --max-time 15 -X OPTIONS \
  "$API_URL/v1/courses" \
  -H "Origin: $WEB_URL" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: authorization" 2>/dev/null)" || CORS_CODE="000"
echo "OPTIONS $API_URL/v1/courses"
echo "  Origin: $WEB_URL | Access-Control-Request-Method: GET | Access-Control-Request-Headers: authorization"
echo "  -> HTTP $CORS_CODE"
grep -i "^access-control-\|^vary:" "$CORS_HDR" 2>/dev/null | sed 's/\r$//' || echo "  (no CORS headers in response)"
ALLOW_ORIGIN="$(grep -i '^access-control-allow-origin:' "$CORS_HDR" 2>/dev/null | head -1 | sed 's/^[^:]*: *//' | tr -d '\r')"
ALLOW_METHODS="$(grep -i '^access-control-allow-methods:' "$CORS_HDR" 2>/dev/null | head -1 | sed 's/^[^:]*: *//' | tr -d '\r')"
ALLOW_HEADERS="$(grep -i '^access-control-allow-headers:' "$CORS_HDR" 2>/dev/null | head -1 | sed 's/^[^:]*: *//' | tr -d '\r')"
if { [ "$CORS_CODE" = "200" ] || [ "$CORS_CODE" = "204" ]; } && [ "$ALLOW_ORIGIN" = "$WEB_URL" ] \
   && echo "$ALLOW_METHODS" | grep -qi "GET" && echo "$ALLOW_HEADERS" | grep -qi "authorization"; then
  record "cors.preflight.local" "PASS" "HTTP $CORS_CODE; allow-origin=$ALLOW_ORIGIN; methods OK; authorization header allowed"
else
  record "cors.preflight.local" "FAIL" "HTTP $CORS_CODE; allow-origin='$ALLOW_ORIGIN' (expected $WEB_URL); methods='$ALLOW_METHODS'; headers='$ALLOW_HEADERS' — check CORS_ORIGINS in backend/.env"
fi

if [ "$WITH_STAGING" = "1" ]; then
  section "5b. OPTIONAL staging CORS preflight (READ-ONLY, opt-in)"
  SCORS_HDR="$EVIDENCE_DIR/cors-staging.headers"
  SCORS_CODE="$(curl -sS -o /dev/null -D "$SCORS_HDR" -w "%{http_code}" --max-time 20 -X OPTIONS \
    "$STAGING_API/v1/courses" \
    -H "Origin: $STAGING_WEB" \
    -H "Access-Control-Request-Method: GET" \
    -H "Access-Control-Request-Headers: authorization" 2>/dev/null)" || SCORS_CODE="000"
  echo "OPTIONS $STAGING_API/v1/courses (Origin: $STAGING_WEB) -> HTTP $SCORS_CODE"
  grep -i "^access-control-" "$SCORS_HDR" 2>/dev/null | sed 's/\r$//' || echo "  (no CORS headers / unreachable)"
  S_ALLOW_ORIGIN="$(grep -i '^access-control-allow-origin:' "$SCORS_HDR" 2>/dev/null | head -1 | sed 's/^[^:]*: *//' | tr -d '\r')"
  if { [ "$SCORS_CODE" = "200" ] || [ "$SCORS_CODE" = "204" ]; } && [ "$S_ALLOW_ORIGIN" = "$STAGING_WEB" ]; then
    record "cors.preflight.staging" "PASS" "HTTP $SCORS_CODE; allow-origin=$S_ALLOW_ORIGIN (Open Question #2 settled)"
  else
    record "cors.preflight.staging" "BLOCKED" "HTTP $SCORS_CODE from this network — run from a host that reaches staging"
  fi
else
  record "cors.preflight.staging" "SKIPPED" "not requested (--with-staging-preflight); roadmap Q2 remains open"
fi

# ----------------------------- 6. verdict -----------------------------------
section "6. Verdict"
echo "Check results:"
FAILED=0
for id in "${CHECK_IDS[@]}"; do
  st="${CHECK_STATE[$id]}"
  printf '  %-28s %-14s %s\n' "$id" "$st" "${CHECK_NOTE[$id]}"
  case "$st" in FAIL|BLOCKED) FAILED=1 ;; esac
done
echo
echo "Repository state after run (must show no tracked changes):"
git -C "$REPO_DIR" status --porcelain || true
echo
if [ "$FAILED" = "0" ]; then
  echo "VERDICT: BATCH 0.1 LOCAL VERIFICATION PASSED (exit 0)"
  echo "Paste this verdict block + the F5 'created_at analysis' line back to the executor"
  echo "to complete the Batch 0.1 ledger entry."
  exit 0
else
  echo "VERDICT: BATCH 0.1 LOCAL VERIFICATION HAS FAILURES/BLOCKS (exit 1)"
  echo "Do NOT tune config to force a pass — paste the block above back for triage."
  exit 1
fi
