#!/usr/bin/env bash
# podd_ingest_bootstrap.sh — W10 Task 1 (Pod D / Hisham)
#
# One-time, IDEMPOTENT Keycloak provisioning for the ingestion runner.
# Creates NOTHING in the app DB (that is the seed step's job).
#
# Ensures in realm "openlearn":
#   1. client  openlearn-runner  (public, standard flow OFF, ROPC ON)
#   2. audience mapper on that client -> "openlearn-api" (access token claim)
#   3. user    pod-d-runner      (enabled, emailVerified, known password)
#   4. realm role assignment: instructor
#
# Does NOT touch: openlearn-frontend, admin-cli, any existing client/user.
#
# Usage (on the VPS, repo root, staging compose up):
#   bash scripts/podd_ingest_bootstrap.sh
# Admin creds come from env or are sourced from .env / infra/.env
# (KEYCLOAK_ADMIN_USER / KEYCLOAK_ADMIN_PASSWORD — same names compose uses).
#
# Output: BOOTSTRAP OK block printing SUB=<keycloak uuid> — the seed step
# needs exactly that value (it becomes users.keycloak_subject).

set -euo pipefail

KC_CONTAINER="${KC_CONTAINER:-staging-keycloak}"
KC_URL="${KC_URL:-https://keycloak-staging.duckdns.org}"
REALM="${REALM:-openlearn}"
CLIENT_ID="${RUNNER_CLIENT_ID:-openlearn-runner}"
RUNNER_USER="${RUNNER_USER:-pod-d-runner}"
RUNNER_PASS="${RUNNER_PASS:-PodD-Runner-W10!}"
RUNNER_EMAIL="${RUNNER_EMAIL:-pod-d-runner@staging.local}"
RUNNER_ROLE="${RUNNER_ROLE:-instructor}"
AUDIENCE="openlearn-api"   # must equal backend KEYCLOAK_AUDIENCE

if [ -z "${KEYCLOAK_ADMIN_USER:-}" ] || [ -z "${KEYCLOAK_ADMIN_PASSWORD:-}" ]; then
  for f in .env infra/.env infra/staging.env; do
    if [ -f "$f" ]; then
      echo ">>> sourcing $f for admin credentials"
      set -a; . "./$f"; set +a
      break
    fi
  done
fi
: "${KEYCLOAK_ADMIN_USER:?set KEYCLOAK_ADMIN_USER (env or .env)}"
: "${KEYCLOAK_ADMIN_PASSWORD:?set KEYCLOAK_ADMIN_PASSWORD (env or .env)}"

docker inspect "$KC_CONTAINER" >/dev/null 2>&1 \
  || { echo ">>> FAIL: container '$KC_CONTAINER' not found (is staging compose up?)"; exit 1; }

KCADM() { docker exec "$KC_CONTAINER" /opt/keycloak/bin/kcadm.sh "$@"; }

echo ">>> [1/6] admin login -> $KC_URL (realm master)"
KCADM config credentials --server "$KC_URL" --realm master \
  --user "$KEYCLOAK_ADMIN_USER" --password "$KEYCLOAK_ADMIN_PASSWORD"

echo ">>> [2/6] ensure client '$CLIENT_ID' (public, ROPC on)"
CID=$(KCADM get clients -r "$REALM" -q clientId="$CLIENT_ID" \
      --fields id --format csv --noquotes | tail -n +2 | head -1)
if [ -z "$CID" ]; then
  KCADM create clients -r "$REALM" \
    -s clientId="$CLIENT_ID" -s enabled=true -s publicClient=true \
    -s standardFlowEnabled=false -s directAccessGrantsEnabled=true
  CID=$(KCADM get clients -r "$REALM" -q clientId="$CLIENT_ID" \
        --fields id --format csv --noquotes | tail -n +2 | head -1)
fi
[ -n "$CID" ] || { echo ">>> FAIL: could not resolve client uuid"; exit 1; }
echo "    client uuid: $CID"
# force the flags even if the client pre-existed
KCADM update "clients/$CID" -r "$REALM" \
  -s enabled=true -s publicClient=true -s directAccessGrantsEnabled=true

echo ">>> [3/6] ensure audience mapper -> $AUDIENCE"
MAPPER_NAME="pod-d-runner-aud"
HAVE_MAPPER=$(KCADM get "clients/$CID/protocol-mappers/models" -r "$REALM" \
  --fields name --format csv --noquotes 2>/dev/null | grep -x "$MAPPER_NAME" || true)
if [ -z "$HAVE_MAPPER" ]; then
  KCADM create "clients/$CID/protocol-mappers/models" -r "$REALM" \
    -s name="$MAPPER_NAME" -s protocol="openid-connect" \
    -s protocolMapper="oidc-audience-mapper" \
    -s "config={\"included.clientAudience\":\"$AUDIENCE\",\"access.token.claim\":\"true\"}" \
    || echo "    (mapper create skipped — probably already exists)"
fi

echo ">>> [4/6] ensure user '$RUNNER_USER'"
UID_=$(KCADM get users -r "$REALM" -q exact=true -q username="$RUNNER_USER" \
       --fields id --format csv --noquotes | tail -n +2 | head -1)
if [ -z "$UID_" ]; then
  KCADM create users -r "$REALM" \
    -s username="$RUNNER_USER" -s enabled=true \
    -s email="$RUNNER_EMAIL" -s emailVerified=true \
    -s firstName="Pod" -s lastName="Runner"
  UID_=$(KCADM get users -r "$REALM" -q exact=true -q username="$RUNNER_USER" \
         --fields id --format csv --noquotes | tail -n +2 | head -1)
fi
[ -n "$UID_" ] || { echo ">>> FAIL: could not resolve user uuid"; exit 1; }
echo "    user uuid (=JWT sub): $UID_"
KCADM update "users/$UID_" -r "$REALM" -s enabled=true -s emailVerified=true
KCADM update "users/$UID_/reset-password" -r "$REALM" \
  -s type=password -s value="$RUNNER_PASS" -s temporary=false

echo ">>> [5/6] ensure realm role '$RUNNER_ROLE' + assignment"
if ! KCADM get "roles/$RUNNER_ROLE" -r "$REALM" >/dev/null 2>&1; then
  KCADM create roles -r "$REALM" -s name="$RUNNER_ROLE"
  echo "    (role created)"
fi
KCADM add-roles -r "$REALM" --uusername "$RUNNER_USER" --rolename "$RUNNER_ROLE" \
  || echo "    (add-roles skipped — probably already mapped)"

echo ">>> [6/6] verify role mapping"
GOT=$(KCADM get "users/$UID_/role-mappings/realm" -r "$REALM" \
      --fields name --format csv --noquotes 2>/dev/null | grep -x "$RUNNER_ROLE" || true)
[ -n "$GOT" ] || { echo ">>> FAIL: '$RUNNER_ROLE' not mapped to $RUNNER_USER"; exit 1; }

echo ""
echo "================= BOOTSTRAP OK ================="
echo "  CLIENT_ID  = $CLIENT_ID"
echo "  RUNNER_USER= $RUNNER_USER"
echo "  SUB        = $UID_"
echo "  (keep SUB for the seed step; the runner fetches"
echo "   a fresh token itself via ROPC on every run)"
echo "================================================"

# Optional live ROPC smoke from the VPS host (needs curl + python3 there).
if command -v curl >/dev/null 2>&1 && command -v python3 >/dev/null 2>&1; then
  echo ">>> ROPC smoke test (host):"
  RESP=$(curl -s -X POST "$KC_URL/realms/$REALM/protocol/openid-connect/token" \
    -d grant_type=password -d client_id="$CLIENT_ID" \
    -d username="$RUNNER_USER" -d password="$RUNNER_PASS" -d scope=openid)
  echo "$RESP" | RUNNER_ROLE="$RUNNER_ROLE" python3 -c '
import json,sys,base64,os
d=json.load(sys.stdin)
tok=d.get("access_token")
if not tok: sys.exit("  ROPC FAILED: "+json.dumps(d)[:200])
p=tok.split(".")[1]; p+="="*(-len(p)%4)
c=json.loads(base64.urlsafe_b64decode(p))
aud=c.get("aud"); aud=aud if isinstance(aud,list) else [aud]
rr=(c.get("realm_access") or {}).get("roles",[])
print("  iss :",c.get("iss")); print("  sub :",c.get("sub"))
print("  aud :",aud); print("  roles:",rr)
print("  AUD_OK:", "openlearn-api" in aud, "| ROLE_OK:", os.environ["RUNNER_ROLE"] in rr)
' || echo "  (smoke failed — check output above)"
fi
