#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# scripts/setup-dev.sh — OpenLearn AI local development setup
#
# Automates the safe, repeatable parts of docs/development/LOCAL_SETUP.md:
#
#   Phase 1  Preflight (required tools)
#   Phase 2  Repository state (repository detection, no git mutations)
#   Phase 3  Environment files (created only if missing; never overwritten)
#   Phase 4  Docker infrastructure (db + keycloak + one-shot bootstrap)
#   Phase 5  Backend virtualenv + dependencies
#   Phase 6  Frontend dependencies (npm ci, lockfile-based)
#   Phase 7  Alembic migrations
#   Phase 8  Verification + printed next steps
#
# The script is idempotent and safe to re-run. It NEVER deletes git changes,
# resets git, checks out or switches branches, drops databases, removes
# Docker volumes, overwrites environment files, or prints secret values.
# It does not start the backend/frontend dev servers — it prints the
# commands for those at the end.
# ============================================================================

COMPOSE_FILE="infra/docker-compose.dev.yml"

# Bounded waits (seconds)
PG_WAIT_SECONDS=120
KC_WAIT_SECONDS=180

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------
if [ -t 1 ]; then
    C_RESET='\033[0m'
    C_BOLD='\033[1m'
    C_GREEN='\033[0;32m'
    C_YELLOW='\033[0;33m'
    C_RED='\033[0;31m'
    C_BLUE='\033[0;34m'
else
    C_RESET=''
    C_BOLD=''
    C_GREEN=''
    C_YELLOW=''
    C_RED=''
    C_BLUE=''
fi

log()  { printf '%b\n' "${C_BLUE}==> ${C_RESET}${C_BOLD}$*${C_RESET}"; }
ok()   { printf '%b\n' "    ${C_GREEN}[ok]${C_RESET} $*"; }
warn() { printf '%b\n' "    ${C_YELLOW}[warn]${C_RESET} $*"; }
die()  { printf '%b\n' "${C_RED}[setup-dev] ERROR:${C_RESET} $*" >&2; exit 1; }

logo() {
    printf '%b\n' "${C_BLUE}${C_BOLD}"
    cat <<'EOF'
       
   ____                       
  / __ \____  ___  ____       
 / / / / __ \/ _ \/ __ \      
/ /_/ / /_/ /  __/ / / /      
\____/ .___/\___/_/ /_/       
    / /                       
   / /   ___  ____  _________ 
  / /   / _ \/ __ `/ ___/ __ \
 / /___/  __/ /_/ / /  / / / /
/_____/\___/\__,_/_/  /_/ /_/ 

EOF
    printf '%b\n' "${C_RESET}"
}

# ---------------------------------------------------------------------------
# Keycloak realm readiness probe.
#
# Deliberately robust against:
#   1. Proxy variables hijacking localhost requests.
#   2. localhost resolving to IPv6 while Docker publishes IPv4.
#
# Uses the standard OIDC discovery document:
#   /realms/openlearn/.well-known/openid-configuration
# ---------------------------------------------------------------------------
kc_realm_probe() {
    if curl --noproxy '*' -fsS -o /dev/null \
        "http://127.0.0.1:8080/realms/openlearn/.well-known/openid-configuration" \
        2>/dev/null; then
        return 0
    fi

    curl --noproxy '*' -fsS -o /dev/null \
        "http://localhost:8080/realms/openlearn/.well-known/openid-configuration" \
        2>/dev/null
}

# ===========================================================================
# Startup
# ===========================================================================
logo
echo

# ===========================================================================
# Phase 1 — Preflight
# ===========================================================================
log "Phase 1/8 — Preflight: checking required tools"

require_cmd() {
    if ! command -v "$1" >/dev/null 2>&1; then
        die "Required tool '$1' not found on PATH. Install it and re-run."
    fi

    ok "$1 found: $(command -v "$1")"
}

require_cmd git
require_cmd docker
require_cmd node
require_cmd npm
require_cmd curl

if ! docker compose version >/dev/null 2>&1; then
    die "Docker Compose v2 ('docker compose' plugin) is required but not available. Install the docker-compose-plugin and re-run."
fi

ok "docker compose plugin available: $(docker compose version --short 2>/dev/null || echo 'v2')"

if ! docker info >/dev/null 2>&1; then
    die "The Docker daemon is not reachable. Start Docker (Docker Desktop or the system Docker service) and re-run."
fi

ok "Docker daemon reachable"

# ---------------------------------------------------------------------------
# Python selection
#
# Requires exactly Python 3.12 (the version used by CI).
#
# Windows/Git Bash can expose an MSYS2/MinGW python3 before Windows CPython.
# The backend dependencies require a normal CPython build on Windows because
# packages such as cryptography provide Windows CPython wheels but not the
# MinGW Python ABI.
#
# The Windows launcher (py.exe) is therefore only consulted in genuinely
# Windows-native shells (Git Bash / MSYS2 / Cygwin, detected via uname).
# Under WSL2 the Windows interop PATH can expose py.exe, but a Windows
# interpreter cannot manage a Linux virtualenv — so WSL2 uses python3 like
# any other Unix-like environment.
# ---------------------------------------------------------------------------
PYTHON_IS_WINDOWS_SHELL=false
case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*)
        PYTHON_IS_WINDOWS_SHELL=true
        ;;
esac

if [ "${PYTHON_IS_WINDOWS_SHELL}" = "true" ] && command -v py.exe >/dev/null 2>&1; then
    PYTHON_CMD=(py.exe -3.12)
    PYTHON_LABEL="Windows CPython 3.12 (py launcher)"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
    PYTHON_LABEL="python3"
else
    if [ "${PYTHON_IS_WINDOWS_SHELL}" = "true" ]; then
        die "Python 3.12 is required but neither 'py.exe -3.12' nor 'python3' was found on PATH."
    fi

    die "Python 3.12 is required but 'python3' was not found on PATH."
fi

if ! "${PYTHON_CMD[@]}" --version >/dev/null 2>&1; then
    die "Selected Python interpreter could not be executed: ${PYTHON_CMD[*]}"
fi

PYTHON_MAJOR="$(
    "${PYTHON_CMD[@]}" -c 'import sys; print(sys.version_info[0])'
)"

PYTHON_MINOR="$(
    "${PYTHON_CMD[@]}" -c 'import sys; print(sys.version_info[1])'
)"

if [ "${PYTHON_MAJOR}" -ne 3 ] || [ "${PYTHON_MINOR}" -ne 12 ]; then
    die "Python 3.12 is required for this development environment. Found: $("${PYTHON_CMD[@]}" --version 2>&1)"
fi

PYTHON_IMPLEMENTATION="$(
    "${PYTHON_CMD[@]}" -c 'import platform; print(platform.python_implementation())'
)"

PYTHON_PLATFORM="$(
    "${PYTHON_CMD[@]}" -c 'import sys; print(sys.platform)'
)"

# On Windows, reject non-CPython implementations.
if [ "${PYTHON_PLATFORM}" = "win32" ] && [ "${PYTHON_IMPLEMENTATION}" != "CPython" ]; then
    die "Windows CPython 3.12 is required. Found implementation: ${PYTHON_IMPLEMENTATION}"
fi

ok "Python: $("${PYTHON_CMD[@]}" --version 2>&1) (${PYTHON_LABEL}, ${PYTHON_IMPLEMENTATION}, ${PYTHON_PLATFORM})"

NODE_MAJOR="$(node -p 'process.versions.node.split(".")[0]')"

if [ "${NODE_MAJOR}" -lt 20 ]; then
    die "Node.js >= 20 is required (CI and README both target Node 20). Found: $(node --version)."
fi

ok "node version: $(node --version)"

# ===========================================================================
# Phase 2 — Repository state
# ===========================================================================
log "Phase 2/8 — Repository state"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [ ! -f "${REPO_ROOT}/${COMPOSE_FILE}" ] \
    || [ ! -d "${REPO_ROOT}/backend" ] \
    || [ ! -d "${REPO_ROOT}/frontend" ]; then

    die "This does not look like the OpenLearn AI repository (${REPO_ROOT}). Run the script from a clone of OpenLearn-AI."
fi

GIT_TOPLEVEL="$(
    git -C "${REPO_ROOT}" rev-parse --show-toplevel 2>/dev/null || true
)"

if [ -z "${GIT_TOPLEVEL}" ]; then
    die "'${REPO_ROOT}' is not a git working tree."
fi

ok "Repository root: ${REPO_ROOT}"

# Branch-independent by design: the setup runs on whatever branch the
# developer currently has checked out. The current branch is shown for
# information only — it is never used to gate or mutate anything, and the
# script never switches branches.
CURRENT_BRANCH="$(git -C "${REPO_ROOT}" branch --show-current || true)"

if [ -n "${CURRENT_BRANCH}" ]; then
    ok "Branch: ${CURRENT_BRANCH} (informational only — the setup runs on any branch)"
else
    warn "Could not determine the current branch (detached HEAD?). Continuing — the setup is branch-independent."
fi

cd "${REPO_ROOT}"

# ===========================================================================
# Phase 3 — Environment files
# ===========================================================================
log "Phase 3/8 — Environment files"

if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    ok "Created backend/.env from backend/.env.example"
else
    ok "backend/.env already exists — left untouched"
fi

if [ ! -f frontend/.env.local ]; then
    cp frontend/.env.example frontend/.env.local
    ok "Created frontend/.env.local from frontend/.env.example"
else
    ok "frontend/.env.local already exists — left untouched"
fi

# Root .env.local must define OPENLEARN_TEST_USER_PASSWORD.
# Generate it only when the file does not already exist.
if [ ! -f .env.local ]; then

    RANDOM_SUFFIX="$(
        "${PYTHON_CMD[@]}" -c 'import secrets; print(secrets.token_hex(8))'
    )"

    GENERATED_PASSWORD="Dev-${RANDOM_SUFFIX}7"

    {
        echo "# Local development environment for infra/docker-compose.dev.yml."
        echo "# Used via: docker compose --env-file .env.local -f infra/docker-compose.dev.yml <command>"
        echo "# Dev-only credential for the Keycloak test user (policy: >= 8 chars, 1 uppercase, 1 digit)."
        echo "OPENLEARN_TEST_USER_PASSWORD=${GENERATED_PASSWORD}"
    } > .env.local

    ok "Created .env.local with a generated OPENLEARN_TEST_USER_PASSWORD (dev-only)."
    ok "The test-user password is stored in .env.local — it is intentionally not printed."
else
    ok ".env.local already exists — left untouched"
fi

if ! grep -qE '^OPENLEARN_TEST_USER_PASSWORD=.+' .env.local; then
    warn ".env.local exists but does not define OPENLEARN_TEST_USER_PASSWORD."

    die "Add a line 'OPENLEARN_TEST_USER_PASSWORD=<your dev password>' to .env.local (policy: >= 8 chars, 1 uppercase, 1 digit), then re-run."
fi

# ===========================================================================
# Phase 4 — Docker infrastructure
# ===========================================================================
COMPOSE=(docker compose --env-file .env.local -f "${COMPOSE_FILE}")

log "Phase 4/8 — Docker infrastructure (db, keycloak, keycloak-bootstrap)"

log "Starting database container..."
"${COMPOSE[@]}" up -d db

ok "'db' service requested (pgvector/pgvector:pg16, localhost:5432)"

log "Waiting for PostgreSQL to accept connections (bounded: ${PG_WAIT_SECONDS}s)..."

PG_READY=false

for _ in $(seq 1 $((PG_WAIT_SECONDS / 2))); do

    # 'openlearn' is the compose-created maintenance database.
    # The application database is 'openlearn_dev'.
    if "${COMPOSE[@]}" exec -T db pg_isready -U openlearn -d postgres >/dev/null 2>&1; then
        PG_READY=true
        break
    fi

    sleep 2
done

if [ "${PG_READY}" != "true" ]; then

    warn "PostgreSQL did not become ready within ${PG_WAIT_SECONDS}s. Last log lines:"
    "${COMPOSE[@]}" logs --tail 20 db >&2 || true

    die "PostgreSQL is not ready. Check the logs above (common cause: port 5432 already in use)."
fi

ok "PostgreSQL is ready"

# ---------------------------------------------------------------------------
# Database creation
#
# The compose container creates the 'openlearn' maintenance database.
# The project actually uses:
#
#   openlearn_dev  -> application database
#   keycloak       -> Keycloak database
#
# Neither secondary database is guaranteed to be created by compose, so
# create them idempotently. No existing database is ever dropped.
# ---------------------------------------------------------------------------
db_exists() {
    local database_name="$1"
    local result

    result="$(
        "${COMPOSE[@]}" exec -T db psql \
            -U openlearn \
            -d postgres \
            -tAc "SELECT 1 FROM pg_database WHERE datname='${database_name}';" \
            2>/dev/null |
            tr -d '[:space:]'
    )"

    [ "${result}" = "1" ]
}

for DB_NAME in keycloak openlearn_dev; do

    if db_exists "${DB_NAME}"; then
        ok "Database '${DB_NAME}' already exists"
    else
        log "Creating database '${DB_NAME}'..."

        "${COMPOSE[@]}" exec -T db psql \
            -U openlearn \
            -d postgres \
            -c "CREATE DATABASE ${DB_NAME};"

        ok "Database '${DB_NAME}' created"
    fi

done

# ---------------------------------------------------------------------------
# Start Keycloak
# ---------------------------------------------------------------------------
log "Starting Keycloak (quay.io/keycloak/keycloak:26.7.3, localhost:8080)..."

"${COMPOSE[@]}" up -d keycloak

log "Waiting for realm 'openlearn' discovery endpoint (bounded: ${KC_WAIT_SECONDS}s)..."

KC_READY=false

for _ in $(seq 1 $((KC_WAIT_SECONDS / 2))); do

    if kc_realm_probe; then
        KC_READY=true
        break
    fi

    sleep 2
done

if [ "${KC_READY}" != "true" ]; then

    warn "Keycloak did not become ready within ${KC_WAIT_SECONDS}s. Last log lines:"
    "${COMPOSE[@]}" logs --tail 30 keycloak >&2 || true

    PROXY_LINES="$(
        env |
        grep -iE '^(https?_proxy|all_proxy)=' |
        sed -E 's/=.*/=<set>/' ||
        true
    )"

    if [ -n "${PROXY_LINES}" ]; then
        warn "Proxy variables detected in your shell (they can hijack localhost requests):"
        printf '%s\n' "${PROXY_LINES}" |
            sed 's/^/        /' >&2

        warn "Fix: export no_proxy=\"127.0.0.1,localhost\" NO_PROXY=\"127.0.0.1,localhost\" then re-run."
    fi

    if curl \
        --noproxy '*' \
        -sS \
        -o /dev/null \
        --max-time 3 \
        "http://127.0.0.1:8080/" \
        2>/dev/null; then

        warn "Port 8080 IS answering on 127.0.0.1 — Keycloak is up; the realm endpoint itself is failing."
        warn "If discovery returns 404 the realm may be disabled: open http://127.0.0.1:8080/admin (admin/admin) and check the 'openlearn' realm."
    else
        warn "Nothing answered on 127.0.0.1:8080 — verify the published port with:"
        warn "  docker compose --env-file .env.local -f ${COMPOSE_FILE} port keycloak 8080"
    fi

    die "Keycloak is not ready. Fix the cause above and re-run."
fi

ok "Keycloak realm 'openlearn' is reachable"

# ---------------------------------------------------------------------------
# One-shot Keycloak bootstrap
#
# This service is SUPPOSED to exit after doing its work.
#
# Success:
#   exit code 0 -> normal one-shot completion.
#
# Failure:
#   non-zero exit code -> actual bootstrap failure.
#
# `run --rm --no-deps` is intentional:
#   - run the bootstrap script once
#   - remove the temporary container afterwards
#   - do not restart/recreate Keycloak
#   - Keycloak is already running and ready
#
# This also makes the bootstrap command's exit code directly observable.
# ---------------------------------------------------------------------------
log "Running keycloak-bootstrap (creates/updates local test user 'testuser')..."

BOOTSTRAP_EXIT_CODE=0

"${COMPOSE[@]}" run \
    --rm \
    --no-deps \
    keycloak-bootstrap ||
    BOOTSTRAP_EXIT_CODE=$?

if [ "${BOOTSTRAP_EXIT_CODE}" -ne 0 ]; then

    warn "Keycloak bootstrap failed with exit code ${BOOTSTRAP_EXIT_CODE}."
    warn "The bootstrap container is a one-shot service, so stopping after success is normal; this non-zero code indicates an actual failure."

    echo
    warn "Keycloak bootstrap diagnostics:"
    "${COMPOSE[@]}" logs --tail 80 keycloak-bootstrap >&2 || true

    echo
    warn "Current Keycloak container status:"
    "${COMPOSE[@]}" ps keycloak keycloak-bootstrap >&2 || true

    die "Keycloak bootstrap failed. Fix the error above and re-run."
fi

ok "Keycloak bootstrap completed successfully (test user 'testuser' ready)"

# ===========================================================================
# Phase 5 — Backend environment
# ===========================================================================
log "Phase 5/8 — Backend environment (virtualenv + dependencies)"

VENV_DIR="$(pwd)/backend/.venv"

# Cross-platform venv detection:
#
# Windows CPython:
#   backend/.venv/Scripts/python.exe
#
# Unix/Linux/macOS:
#   backend/.venv/bin/python
#
if [ -f "${VENV_DIR}/Scripts/python.exe" ]; then

    VENV_PYTHON="${VENV_DIR}/Scripts/python.exe"

    VENV_PLATFORM="$(
        "${VENV_PYTHON}" -c 'import sysconfig; print(sysconfig.get_platform())'
    )"

    VENV_BASE_PREFIX="$(
        "${VENV_PYTHON}" -c 'import sys; print(sys.base_prefix)'
    )"

    if [ "${VENV_PLATFORM}" != "win-amd64" ]; then
        die "backend/.venv uses an incompatible Windows Python platform: ${VENV_PLATFORM}. Expected win-amd64. Move the existing backend/.venv aside and re-run."
    fi

    if [ "${VENV_BASE_PREFIX}" = "C:\\msys64\\mingw64" ] \
        || [[ "${VENV_BASE_PREFIX}" == *"/msys64/mingw64" ]]; then
        die "backend/.venv was created from MSYS2/MinGW Python (${VENV_BASE_PREFIX}). Move the existing backend/.venv aside and re-run so it can be recreated with Windows CPython 3.12."
    fi

    ok "Existing Windows CPython virtualenv found at backend/.venv"

elif [ -f "${VENV_DIR}/bin/python" ]; then

    VENV_PYTHON="${VENV_DIR}/bin/python"
    ok "Existing Unix virtualenv found at backend/.venv"

else

    PYTHON_VERSION="$("${PYTHON_CMD[@]}" --version 2>&1)"
    log "Creating virtualenv at backend/.venv using: ${PYTHON_VERSION}..."

    "${PYTHON_CMD[@]}" -m venv "${VENV_DIR}"

    if [ -f "${VENV_DIR}/Scripts/python.exe" ]; then
        VENV_PYTHON="${VENV_DIR}/Scripts/python.exe"
    elif [ -f "${VENV_DIR}/bin/python" ]; then
        VENV_PYTHON="${VENV_DIR}/bin/python"
    else
        die "Virtualenv was created but its Python executable could not be found."
    fi

    ok "Virtualenv created"
fi

VENV_VERSION="$("${VENV_PYTHON}" --version 2>&1)"
VENV_IMPLEMENTATION="$(
    "${VENV_PYTHON}" -c 'import platform; print(platform.python_implementation())'
)"
VENV_PLATFORM="$(
    "${VENV_PYTHON}" -c 'import sys; print(sys.platform)'
)"

ok "Virtualenv Python: ${VENV_VERSION} (${VENV_IMPLEMENTATION}, ${VENV_PLATFORM})"

# Safety check: on Windows, make sure the existing venv isn't the old
# MSYS2/MinGW environment that caused the cryptography wheel failure.
if [ "${VENV_PLATFORM}" = "win32" ]; then
    VENV_SYS_PLATFORM="$(
        "${VENV_PYTHON}" -c 'import sysconfig; print(sysconfig.get_platform())'
    )"

    if [ "${VENV_SYS_PLATFORM}" != "win-amd64" ]; then
        die "backend/.venv is not a standard Windows CPython environment. Platform reported: ${VENV_SYS_PLATFORM}. Move backend/.venv aside and re-run."
    fi
fi

if "${VENV_PYTHON}" -c 'import fastapi, alembic, sqlalchemy, asyncpg' >/dev/null 2>&1; then

    ok "Core backend dependencies already importable — skipping pip install"

else

    log "Installing backend dependencies (requirements.txt + requirements-dev.txt)..."
    log "NOTE: this is a large install (docling/sentence-transformers pull the torch stack); it can take several minutes."

    if ! "${VENV_PYTHON}" -m pip install \
        -r backend/requirements.txt \
        -r backend/requirements-dev.txt; then

        echo
        warn "Backend dependency installation failed."
        warn "Python interpreter used:"
        "${VENV_PYTHON}" --version >&2 || true

        warn "Python implementation/platform:"
        "${VENV_PYTHON}" -c \
            'import platform,sys; print(platform.python_implementation(), sys.platform)' \
            >&2 || true

        die "Backend dependencies could not be installed. See the pip error above."
    fi

    ok "Backend dependencies installed (versions exactly as pinned in the repository)"
fi

# ===========================================================================
# Phase 6 — Frontend environment
# ===========================================================================
log "Phase 6/8 — Frontend environment (npm ci from package-lock.json)"

if [ ! -d frontend/node_modules ] \
    || [ frontend/package-lock.json -nt frontend/node_modules ]; then

    log "Installing frontend dependencies with npm ci..."

    if ! (cd frontend && npm ci); then
        die "Frontend dependency installation failed. See npm output above."
    fi

    ok "Frontend dependencies installed"

else

    ok "frontend/node_modules is up to date with package-lock.json — skipping npm ci"
fi

# ===========================================================================
# Phase 7 — Database migrations
# ===========================================================================
log "Phase 7/8 — Alembic migrations (database: value of DATABASE_URL in backend/.env)"

log "Running 'alembic upgrade head' from backend/..."

if ! (
    cd backend &&
    "${VENV_PYTHON}" -m alembic upgrade head
); then

    die "Alembic migrations failed. Check backend/.env DATABASE_URL, PostgreSQL, and the migration error above."
fi

CURRENT_REV="$(
    cd backend &&
    "${VENV_PYTHON}" -m alembic current 2>/dev/null |
    tail -n 1 |
    tr -d '[:space:]' ||
    true
)"

if [ -z "${CURRENT_REV}" ]; then
    die "Alembic reported no current revision — migrations did not complete. Check backend/.env DATABASE_URL and the db container."
fi

ok "Migrations applied; current revision: ${CURRENT_REV}"

# ===========================================================================
# Phase 8 — Verification + next steps
# ===========================================================================
log "Phase 8/8 — Verification"

RUNNING_SERVICES="$(
    "${COMPOSE[@]}" ps \
        --services \
        --filter status=running \
        2>/dev/null ||
        true
)"

for SVC in db keycloak; do

    if printf '%s\n' "${RUNNING_SERVICES}" | grep -qx "${SVC}"; then
        ok "Docker service '${SVC}' is running"
    else
        die "Docker service '${SVC}' is not running. Inspect with: docker compose --env-file .env.local -f ${COMPOSE_FILE} ps"
    fi

done

# Use the compose-created maintenance database for the connectivity check.
if "${COMPOSE[@]}" exec -T db pg_isready -U openlearn -d postgres >/dev/null 2>&1; then

    ok "PostgreSQL reachable on localhost:5432 (databases: openlearn, openlearn_dev, keycloak)"

else

    die "PostgreSQL is no longer reachable."
fi

if kc_realm_probe; then
    ok "Keycloak realm 'openlearn' reachable on localhost:8080"
else
    die "Keycloak realm discovery is no longer reachable."
fi

if [ -n "${CURRENT_REV}" ]; then
    ok "Alembic schema present (revision ${CURRENT_REV})"
fi

echo
printf '%b\n' "${C_GREEN}${C_BOLD}Local development environment is ready.${C_RESET}"
echo

echo "Start the two dev servers yourself (this script intentionally does not"
echo "run them in the foreground):"
echo

echo "  1) Backend (new terminal):"
echo "       cd backend"

if [ -f "${VENV_DIR}/Scripts/python.exe" ]; then
    echo "       .\\.venv\\Scripts\\Activate.ps1"
else
    echo "       source .venv/bin/activate"
fi

echo "       uvicorn app.main:app --reload --port 8000"
echo "       # verify: curl http://localhost:8000/health"
echo

echo "  2) Frontend (new terminal):"
echo "       cd frontend"
echo "       npm run dev"
echo "       # open: http://localhost:3000"
echo

echo "  3) Log in at http://localhost:3000/login as user 'testuser'."
echo "     The password is the OPENLEARN_TEST_USER_PASSWORD value in .env.local"
echo "     (generated by this script on first run, or your own if you set it)."
echo

echo "Full guide: docs/development/LOCAL_SETUP.md"
