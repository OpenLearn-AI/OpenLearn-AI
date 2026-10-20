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
#            + material-processing credentials (Redis/MinIO) synced into
#              backend/.env from the generated .env.local values
#   Phase 4  Docker infrastructure (db + redis + minio + one-shot minio-init
#            bucket creation + keycloak + one-shot bootstrap)
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
elif command -v python3.12 >/dev/null 2>&1; then
    PYTHON_CMD=(python3.12)
    PYTHON_LABEL="python3.12"
elif command -v uv >/dev/null 2>&1 && UV_PY="$(uv python find 3.12 2>/dev/null)"; then
    PYTHON_CMD=("${UV_PY}")
    PYTHON_LABEL="uv-managed Python 3.12"
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
        echo "# Dev-only credential for the Keycloak demo instructor account (Batch 2.1)."
        echo "OPENLEARN_INSTRUCTOR_USER_PASSWORD=Instructor-${RANDOM_SUFFIX}7"
    } > .env.local

    ok "Created .env.local with a generated OPENLEARN_TEST_USER_PASSWORD and OPENLEARN_INSTRUCTOR_USER_PASSWORD (dev-only)."
    ok "The test-user and instructor passwords are stored in .env.local — they are intentionally not printed."
else
    ok ".env.local already exists — left untouched"
fi

if ! grep -qE '^OPENLEARN_TEST_USER_PASSWORD=.+' .env.local; then
    warn ".env.local exists but does not define OPENLEARN_TEST_USER_PASSWORD."

    die "Add a line 'OPENLEARN_TEST_USER_PASSWORD=<your dev password>' to .env.local (policy: >= 8 chars, 1 uppercase, 1 digit), then re-run."
fi

# The instructor demo account (Batch 2.1) is new relative to existing setups:
# append a generated value instead of failing, so re-running setup on an
# already-configured machine keeps working.
if ! grep -qE '^OPENLEARN_INSTRUCTOR_USER_PASSWORD=.+' .env.local; then
    RANDOM_SUFFIX="$(
        "${PYTHON_CMD[@]}" -c 'import secrets; print(secrets.token_hex(8))'
    )"

    {
        echo "# Dev-only credential for the Keycloak demo instructor account (Batch 2.1)."
        echo "OPENLEARN_INSTRUCTOR_USER_PASSWORD=Instructor-${RANDOM_SUFFIX}7"
    } >> .env.local

    ok "Appended a generated OPENLEARN_INSTRUCTOR_USER_PASSWORD to .env.local (dev-only; the bootstrap now also provisions the instructor demo account)."
fi

# ---------------------------------------------------------------------------
# Material-processing credentials (local environment batch).
#
# The dev compose now also runs Redis (Celery broker) and MinIO (S3-compatible
# storage) — both require credentials that live ONLY in the git-ignored
# .env.local (compose reads it via --env-file). The same MinIO credentials
# must also reach the backend process (backend/.env -> app/config.py) so the
# presigned-URL path and the worker's object fetch authenticate as the same
# MinIO user. Generated once with the append-if-missing pattern above;
# existing values are never overwritten and never printed.
# ---------------------------------------------------------------------------
env_var_value() {
    # Last occurrence wins — python-dotenv/pydantic-settings resolve a
    # duplicated key to its LAST value, so the reading side must match
    # (pre-existing files written by older setup versions may contain
    # duplicates; a warning about them is emitted below).
    sed -n "s/^${1}=//p" "$2" | tail -1 | tr -d '\r'
}

ensure_env_var() {
    local file="$1" name="$2" value="$3" comment="$4"

    if grep -qE "^${name}=.+" "${file}"; then
        ok "${file} already defines ${name} — left untouched"
    elif grep -qE "^${name}=" "${file}"; then
        # Present but EMPTY: not a user-set value. Replace the line in place
        # instead of appending — appending would create a duplicate key, and
        # python-dotenv resolves duplicates to the LAST occurrence anyway.
        # In-place keeps the file layout stable and is idempotent.
        # sed -i.bak + cleanup: portable across GNU sed and BSD/macOS sed
        # (plain `sed -i` fails on macOS).
        if sed -i.bak "s|^${name}=.*$|${name}=${value}|" "${file}" && rm -f "${file}.bak"; then
            ok "Filled the empty ${name} in ${file} in place (never printed)."
        else
            rm -f "${file}.bak"
            warn "Could not fill the empty ${name} in ${file} in place — fix it manually to: ${name}=<generated value>"
        fi
    else
        {
            echo "${comment}"
            echo "${name}=${value}"
        } >> "${file}"

        ok "Appended a generated ${name} to ${file} (never printed)."
    fi
}

if [ ! -f .env.local ]; then
    die ".env.local should exist at this point — the block above must have created it."
fi

ensure_env_var .env.local REDIS_PASSWORD \
    "Redis-$( "${PYTHON_CMD[@]}" -c 'import secrets; print(secrets.token_hex(12))' )" \
    "# Dev-only Redis (Celery broker) password for the local material-processing stack."

# REDIS_URL: full-URL override composed from the generated REDIS_PASSWORD so
# the credential lives in exactly one place. The API process started with the
# documented command (uvicorn app.main:app --reload --port 8000) resolves it
# through the pydantic settings contract (app/config.py reads the root
# .env.local), and scripts/run-worker-dev.sh honors it too — host-run
# processes must reach the loopback-published dev Redis, not the
# container-network "redis" hostname. An existing REDIS_URL (your own
# override) is never replaced.
ensure_env_var .env.local REDIS_URL \
    "redis://:$(env_var_value REDIS_PASSWORD .env.local)@127.0.0.1:6379" \
    "# Full Redis URL override consumed by the API (app/config.py) and the local worker (Redis published on loopback by the dev compose)."

ensure_env_var .env.local MINIO_ROOT_USER \
    "openlearn-local-$( "${PYTHON_CMD[@]}" -c 'import secrets; print(secrets.token_hex(4))' )" \
    "# Dev-only MinIO root user (doubles as the backend's S3 access key id)."

ensure_env_var .env.local MINIO_ROOT_PASSWORD \
    "Minio-$( "${PYTHON_CMD[@]}" -c 'import secrets; print(secrets.token_hex(12))' )" \
    "# Dev-only MinIO root password (doubles as the backend's S3 secret key)."

ensure_env_var .env.local S3_BUCKET_NAME \
    "openlearn-materials" \
    "# Bucket used by the local material-processing pipeline (created idempotently by the minio-init one-shot service)."

# Backend side: backend/.env must carry the SAME MinIO credentials plus the
# AI-provider selection the worker will use. Missing variables are appended
# (credentials synced from .env.local; AI defaults from backend/.env.example).
# A variable you set yourself is never overwritten; a MISMATCH between
# backend/.env and .env.local is warned about instead of silently "fixed".
for VAR_NAME in S3_ACCESS_KEY_ID S3_SECRET_ACCESS_KEY; do
    case "${VAR_NAME}" in
        S3_ACCESS_KEY_ID)    LOCAL_VALUE="$(env_var_value MINIO_ROOT_USER .env.local)" ;;
        S3_SECRET_ACCESS_KEY) LOCAL_VALUE="$(env_var_value MINIO_ROOT_PASSWORD .env.local)" ;;
    esac

    if [ -f backend/.env ] && grep -qE "^${VAR_NAME}=.+" backend/.env; then
        BACKEND_VALUE="$(env_var_value "${VAR_NAME}" backend/.env)"
        if [ "${BACKEND_VALUE}" != "${LOCAL_VALUE}" ]; then
            warn "backend/.env defines ${VAR_NAME} with a DIFFERENT value than .env.local's MinIO credential — left untouched (uploads will fail until they match)."
        else
            ok "backend/.env ${VAR_NAME} matches the MinIO credential in .env.local"
        fi
    elif [ -f backend/.env ] && grep -qE "^${VAR_NAME}=" backend/.env; then
        # Present but EMPTY (e.g. copied from .env.example): fill in place so
        # no duplicate key is created (older versions appended here, which is
        # how duplicate S3 blocks appeared in backend/.env files).
        if sed -i.bak "s|^${VAR_NAME}=.*$|${VAR_NAME}=${LOCAL_VALUE}|" backend/.env && rm -f backend/.env.bak; then
            ok "Filled the empty ${VAR_NAME} in backend/.env in place (synced from .env.local; value never printed)."
        else
            rm -f backend/.env.bak
            warn "Could not fill the empty ${VAR_NAME} in backend/.env in place — set it manually to the .env.local MinIO credential."
        fi
    else
        {
            echo "# Synced from .env.local by scripts/setup-dev.sh (must match the MinIO service credentials)."
            echo "${VAR_NAME}=${LOCAL_VALUE}"
        } >> backend/.env
        ok "Appended ${VAR_NAME} to backend/.env (synced from .env.local; value never printed)."
    fi
done

if [ -f backend/.env ] && grep -qE '^S3_BUCKET_NAME=.+' backend/.env; then
    LOCAL_BUCKET="$(env_var_value S3_BUCKET_NAME .env.local)"
    BACKEND_BUCKET="$(env_var_value S3_BUCKET_NAME backend/.env)"
    if [ "${BACKEND_BUCKET}" != "${LOCAL_BUCKET}" ]; then
        warn "backend/.env S3_BUCKET_NAME (${BACKEND_BUCKET}) differs from .env.local (${LOCAL_BUCKET}) — left untouched."
    else
        ok "backend/.env S3_BUCKET_NAME matches .env.local"
    fi
elif [ -f backend/.env ] && grep -qE '^S3_BUCKET_NAME=' backend/.env; then
    sed -i.bak "s|^S3_BUCKET_NAME=.*$|S3_BUCKET_NAME=$(env_var_value S3_BUCKET_NAME .env.local)|" backend/.env && rm -f backend/.env.bak
    ok "Filled the empty S3_BUCKET_NAME in backend/.env in place"
else
    {
        echo "# Bucket used by the material pipeline (created by the minio-init one-shot compose service)."
        echo "S3_BUCKET_NAME=$(env_var_value S3_BUCKET_NAME .env.local)"
    } >> backend/.env
    ok "Appended S3_BUCKET_NAME to backend/.env"
fi

# AI-provider selection for the local worker: honest real-path defaults
# (postgres vectors, bge-m3 embeddings, mock OCR — see backend/.env.example
# for exactly what each default does and does not exercise). The block is
# appended ONLY when neither the managed mark NOR the AI keys are already
# present: a backend/.env created from .env.example already carries the same
# defaults (without the mark), and older versions appended a second block in
# that case — the duplicate-AI-block bug. Your own choices are never replaced.
AI_DEFAULTS_BLOCK_MARK="# === AI providers (local material-processing path) — managed block, appended by scripts/setup-dev.sh ==="
if [ -f backend/.env ] && grep -qF "${AI_DEFAULTS_BLOCK_MARK}" backend/.env; then
    ok "backend/.env already carries the AI-provider block — left untouched"
elif [ -f backend/.env ] && grep -qE '^AI_VECTOR_DB_PROVIDER=.+' backend/.env; then
    ok "backend/.env already defines the AI-provider keys (e.g. from .env.example) — managed block not appended"
else
    {
        echo "${AI_DEFAULTS_BLOCK_MARK}"
        echo "AI_OCR_PROVIDER=mock"
        echo "AI_EMBEDDING_PROVIDER=bge-m3"
        echo "AI_EMBEDDING_MODEL=BAAI/bge-m3"
        echo "AI_EMBEDDING_DIMENSION=1024"
        echo "AI_EMBEDDING_DEVICE=cpu"
        echo "AI_VECTOR_DB_PROVIDER=postgres"
    } >> backend/.env
    ok "Appended the AI-provider block to backend/.env (mock OCR / bge-m3 embeddings / postgres vectors — see backend/.env.example for what this exercises)."
fi

# Duplicate-key detection (report-only, no silent rewrite): older setup
# versions could append duplicate keys (empty S3/AI lines from the
# .env.example copy followed by appended real values). python-dotenv resolves
# a duplicated key to its LAST occurrence, so the effective configuration is
# well-defined — but duplicates are confusing and are reported here so they
# can be removed manually (keep the LAST occurrence of each key).
report_duplicate_keys() { # <file>
    local file="$1" dups
    dups="$(awk -F= '/^[A-Za-z_][A-Za-z0-9_]*=/{c[$1]++} END{for(k in c) if(c[k]>1) print k}' "${file}" | sort | tr '\n' ' ')"
    if [ -n "${dups}" ]; then
        warn "${file} defines the following keys MORE THAN ONCE: ${dups}— the LAST occurrence wins at runtime; consider removing the earlier duplicates (this is report-only; the script never rewrites your values)."
    fi
}
report_duplicate_keys "${REPO_ROOT}/.env.local"
report_duplicate_keys "${REPO_ROOT}/backend/.env"

# ===========================================================================
# Phase 4 — Docker infrastructure
# ===========================================================================
COMPOSE=(docker compose --env-file .env.local -f "${COMPOSE_FILE}")

# Run `mc` inside the running MinIO service container through an alias that is
# re-established from that container's OWN runtime credentials on every call.
# The MinIO image ships a default `local` alias with EMPTY credentials, so an
# unauthenticated `mc ready local` passes while every authenticated operation
# (`stat`/`ls`/`rm`) is denied; any alias written into the container's writable
# layer is also lost on recreation. Re-deriving the alias from
# $MINIO_ROOT_USER/$MINIO_ROOT_PASSWORD each call keeps these checks working
# after recreation without hardcoding or printing any secret. `mc alias set` is
# an offline config write (it does not contact the server); the following `mc`
# call is the real authenticated probe. Exit status: 3 means the alias could not
# be established; otherwise mc's own status is returned.
minio_mc() {
    "${COMPOSE[@]}" exec -T minio sh -c '
        mc alias set local http://127.0.0.1:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null 2>&1 || exit 3
        exec mc "$@"
    ' mc "$@"
}

log "Phase 4/8 — Docker infrastructure (db, redis, minio, keycloak, keycloak-bootstrap)"

log "Starting database container..."
"${COMPOSE[@]}" up -d db

ok "'db' service requested (pgvector/pgvector:pg16, localhost:5432)"

log "Starting Redis and MinIO (material-processing dependencies)..."
"${COMPOSE[@]}" up -d redis minio

ok "'redis' service requested (digest-pinned redis, localhost:6379, loopback only)"
ok "'minio' service requested (digest-pinned MinIO, S3 API localhost:9000, console localhost:9001, loopback only)"

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
# Redis readiness
#
# Readiness = the broker answers an authenticated PING (password from
# .env.local, passed via the REDISCLI_AUTH environment variable — never as a
# command-line argument, so the secret stays out of process listings).
# ---------------------------------------------------------------------------
log "Waiting for Redis to answer an authenticated PING (bounded: ${PG_WAIT_SECONDS}s)..."

REDIS_PASSWORD_VALUE="$(env_var_value REDIS_PASSWORD .env.local)"

REDIS_READY=false

for _ in $(seq 1 $((PG_WAIT_SECONDS / 2))); do

    if "${COMPOSE[@]}" exec -T -e REDISCLI_AUTH="${REDIS_PASSWORD_VALUE}" redis \
        redis-cli --no-auth-warning ping 2>/dev/null | grep -q PONG; then
        REDIS_READY=true
        break
    fi

    sleep 2
done

if [ "${REDIS_READY}" != "true" ]; then

    warn "Redis did not become ready within ${PG_WAIT_SECONDS}s. Last log lines:"
    "${COMPOSE[@]}" logs --tail 20 redis >&2 || true

    die "Redis is not ready. Check the logs above (common cause: port 6379 already in use)."
fi

ok "Redis is ready (broker for the local Celery worker)"

# ---------------------------------------------------------------------------
# MinIO readiness + one-shot bucket creation
#
# Readiness mirrors the compose healthcheck (`mc ready local`). The bucket is
# created by the minio-init one-shot service — the SAME mechanism staging uses
# (infra/deploy.sh runs it via `--profile init up -d minio-init` and waits for
# its real exit code; the "init" profile keeps `up --wait` from blocking on a
# container whose job is to exit). `mc mb` on an existing bucket is reported,
# not an error — the whole step is idempotent.
# ---------------------------------------------------------------------------
log "Waiting for MinIO S3 API to become ready (bounded: ${PG_WAIT_SECONDS}s)..."

MINIO_READY=false

for _ in $(seq 1 $((PG_WAIT_SECONDS / 2))); do

    if "${COMPOSE[@]}" exec -T minio mc ready local >/dev/null 2>&1; then
        MINIO_READY=true
        break
    fi

    sleep 2
done

if [ "${MINIO_READY}" != "true" ]; then

    warn "MinIO did not become ready within ${PG_WAIT_SECONDS}s. Last log lines:"
    "${COMPOSE[@]}" logs --tail 20 minio >&2 || true

    die "MinIO is not ready. Check the logs above (common cause: ports 9000/9001 already in use)."
fi

ok "MinIO is ready"

log "Running minio-init (creates the materials bucket if missing — idempotent)..."

if "${COMPOSE[@]}" --profile init run --rm minio-init; then
    MINIO_INIT_EXIT_CODE=0
else
    MINIO_INIT_EXIT_CODE=$?
fi

if [ "${MINIO_INIT_EXIT_CODE}" -ne 0 ]; then

    warn "minio-init exited with code ${MINIO_INIT_EXIT_CODE}."
    "${COMPOSE[@]}" logs --tail 40 minio-init >&2 || true

    die "Bucket creation failed. Fix the error above and re-run."
fi

ok "minio-init completed (bucket creation is idempotent; the bucket is confirmed with an authenticated check next)."

# Authenticated confirmation that the bucket is really reachable with the
# configured credentials — the unauthenticated `mc ready local` above cannot
# see this (see the minio_mc comment). Failing here means the service container
# cannot authenticate, which is exactly the defect this check guards against.
MINIO_BUCKET="$(env_var_value S3_BUCKET_NAME .env.local)"

if minio_mc stat "local/${MINIO_BUCKET}" >/dev/null 2>&1; then
    ok "Materials bucket confirmed present (authenticated): ${MINIO_BUCKET} (the bucket name is configuration, not a secret)"
else
    die "MinIO bucket '${MINIO_BUCKET}' is not reachable with the configured credentials. Confirm MINIO_ROOT_USER/MINIO_ROOT_PASSWORD in .env.local match the running minio container, then re-run."
fi

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

for SVC in db redis minio keycloak; do

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

if "${COMPOSE[@]}" exec -T -e REDISCLI_AUTH="${REDIS_PASSWORD_VALUE}" redis \
    redis-cli --no-auth-warning ping 2>/dev/null | grep -q PONG; then

    ok "Redis reachable on localhost:6379 (authenticated PING ok)"

else

    die "Redis is no longer reachable."
fi

# Final MinIO check, distinguishing the three failure modes the old single
# `mc stat` collapsed into one misleading message ("not ready or bucket
# missing"): (a) the service is not running, (b) authentication fails, (c) the
# bucket is genuinely missing. The bucket name is configuration, not a secret.
MINIO_BUCKET="$(env_var_value S3_BUCKET_NAME .env.local)"

if [ -z "$("${COMPOSE[@]}" ps --status running -q minio 2>/dev/null)" ]; then

    die "The 'minio' service is not running. Start it with: ${COMPOSE[*]} up -d minio"

elif ! minio_mc ready local >/dev/null 2>&1; then

    die "The 'minio' service is running but its S3 API is not answering. Check: ${COMPOSE[*]} logs --tail 40 minio"

elif ! minio_mc ls local/ >/dev/null 2>&1; then

    die "MinIO is answering but authenticated requests are DENIED — the credentials in .env.local do not match the running minio container. Re-create it with: ${COMPOSE[*]} up -d --force-recreate minio"

elif minio_mc stat "local/${MINIO_BUCKET}" >/dev/null 2>&1; then

    ok "MinIO reachable on localhost:9000; bucket '${MINIO_BUCKET}' confirmed present (authenticated)"

else

    die "MinIO is authenticated but the materials bucket '${MINIO_BUCKET}' does not exist. Re-run setup-dev.sh to create it."
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

echo "Start the two dev servers and the processing worker yourself (this"
echo "script intentionally does not run them in the foreground):"
echo

echo "  1) Backend API (new terminal):"
echo "       cd backend"

if [ -f "${VENV_DIR}/Scripts/python.exe" ]; then
    echo "       .\\.venv\\Scripts\\Activate.ps1"
else
    echo "       source .venv/bin/activate"
fi

echo "       uvicorn app.main:app --reload --port 8000"
echo "       # verify: curl http://localhost:8000/health"
echo

echo "  2) Processing worker (new terminal — required for material ingestion):"
echo "       bash scripts/run-worker-dev.sh"
echo "       # first material processed downloads the BGE-M3 model (~2 GB, once)"
echo

echo "  3) Frontend (new terminal):"
echo "       cd frontend"
echo "       npm run dev"
echo "       # open: http://localhost:3000"
echo

echo "  4) Log in at http://localhost:3000/login as user 'testuser' (role student)"
echo "     or 'instructor' (role instructor — the demo course-owner account, Batch 2.1)."
echo "     The passwords are the OPENLEARN_TEST_USER_PASSWORD and"
echo "     OPENLEARN_INSTRUCTOR_USER_PASSWORD values in .env.local"
echo "     (generated by this script on first run, or your own if you set it)."
echo

echo "  5) Verify the whole environment in one command:"
echo "       bash scripts/verify-local-environment.sh"
echo "     End-to-end ingestion smoke test with the two locked demo PDFs:"
echo "       bash scripts/run-material-smoke-test.sh"
echo

echo "Full guide: docs/development/LOCAL_SETUP.md"
