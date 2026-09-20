#!/usr/bin/env bash
set -euo pipefail

KEYCLOAK_SERVER="${KEYCLOAK_SERVER:-http://keycloak:8080}"
KEYCLOAK_REALM="openlearn"

TEST_USERNAME="testuser"
TEST_EMAIL="test@example.com"

: "${KC_BOOTSTRAP_ADMIN_USERNAME:?KC_BOOTSTRAP_ADMIN_USERNAME is required}"
: "${KC_BOOTSTRAP_ADMIN_PASSWORD:?KC_BOOTSTRAP_ADMIN_PASSWORD is required}"
: "${OPENLEARN_TEST_USER_PASSWORD:?OPENLEARN_TEST_USER_PASSWORD is required}"

KCADM="/opt/keycloak/bin/kcadm.sh"

echo "Waiting for Keycloak..."

logged_in=false

for attempt in $(seq 1 60); do
    if KC_CLI_PASSWORD="$KC_BOOTSTRAP_ADMIN_PASSWORD" \
        "$KCADM" config credentials \
        --server "$KEYCLOAK_SERVER" \
        --realm master \
        --user "$KC_BOOTSTRAP_ADMIN_USERNAME" \
        >/dev/null 2>&1; then
        logged_in=true
        break
    fi

    sleep 2
done

if [ "$logged_in" != "true" ]; then
    echo "ERROR: Keycloak did not become ready within 120 seconds."
    exit 1
fi

echo "Keycloak is ready."

echo "Ensuring dev realm settings..."

"$KCADM" update "realms/$KEYCLOAK_REALM" \
    -s "registrationAllowed=true" \
    -s "verifyEmail=false"

USER_ID="$(
    "$KCADM" get users \
        -r "$KEYCLOAK_REALM" \
        -q "q=username:$TEST_USERNAME" \
        --fields id \
        --format csv \
        --noquotes 2>/dev/null |
        tail -n 1 |
        tr -d '\r'
)"

if [ -z "$USER_ID" ] || [ "$USER_ID" = "id" ]; then
    echo "Creating local test user: $TEST_USERNAME"

    "$KCADM" create users \
        -r "$KEYCLOAK_REALM" \
        -s "username=$TEST_USERNAME" \
        -s "email=$TEST_EMAIL" \
        -s enabled=true \
        -s emailVerified=true

    USER_ID="$(
        "$KCADM" get users \
            -r "$KEYCLOAK_REALM" \
            -q "q=username:$TEST_USERNAME" \
            --fields id \
            --format csv \
            --noquotes |
            tail -n 1 |
            tr -d '\r'
    )"
else
    echo "Local test user already exists: $TEST_USERNAME"
fi

if [ -z "$USER_ID" ] || [ "$USER_ID" = "id" ]; then
    echo "ERROR: Could not determine the test user's ID."
    exit 1
fi

echo "Ensuring test user profile is correct..."

"$KCADM" update "users/$USER_ID" \
    -r "$KEYCLOAK_REALM" \
    -s "username=$TEST_USERNAME" \
    -s "email=$TEST_EMAIL" \
    -s enabled=true \
    -s emailVerified=true

echo "Setting local test-user password..."

KC_CLI_PASSWORD="$OPENLEARN_TEST_USER_PASSWORD" \
    "$KCADM" set-password \
    -r "$KEYCLOAK_REALM" \
    --userid "$USER_ID"

echo "Ensuring student role..."

"$KCADM" add-roles \
    -r "$KEYCLOAK_REALM" \
    --uusername "$TEST_USERNAME" \
    --rolename student

echo "Local Keycloak test user is ready."
echo "Username: $TEST_USERNAME"
echo "Realm:    $KEYCLOAK_REALM"
