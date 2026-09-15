#!/usr/bin/env bash

set -euo pipefail

IMAGE_TAG="${1:-}"

if [[ -z "$IMAGE_TAG" ]]; then
  echo "ERROR: Image tag is required."
  echo "Usage: ./infra/deploy.sh sha-<commit-sha>"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

COMPOSE_FILE="docker-compose.staging.yml"
ENV_FILE=".env.runtime"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: $ENV_FILE not found."
  exit 1
fi

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "ERROR: $COMPOSE_FILE not found."
  exit 1
fi

export IMAGE_TAG

echo "==> Deploying image tag: $IMAGE_TAG"

echo "==> Pulling images..."
docker compose \
  --env-file "$ENV_FILE" \
  -f "$COMPOSE_FILE" \
  pull

echo "==> Running database migrations..."
docker compose \
  --env-file "$ENV_FILE" \
  -f "$COMPOSE_FILE" \
  run --rm --no-deps backend alembic upgrade head

echo "==> Starting services..."
docker compose \
  --env-file "$ENV_FILE" \
  -f "$COMPOSE_FILE" \
  up -d --remove-orphans --wait --wait-timeout 180

echo "==> Checking backend..."
curl --fail --silent --show-error \
  http://127.0.0.1:8000/health > /dev/null

echo "==> Backend health check passed."

echo "==> Checking frontend..."
curl --fail --silent --show-error \
  http://127.0.0.1:3000/ > /dev/null

echo "==> Frontend health check passed."

echo "==> Cleaning old staging images..."

docker image prune -f

for IMAGE in \
  ghcr.io/muhammadseyam/openlearn-backend \
  ghcr.io/muhammadseyam/openlearn-frontend
do
  echo "==> Removing old SHA-tagged images for $IMAGE..."

  mapfile -t SHA_TAGS < <(
    docker images "$IMAGE" --format '{{.Tag}}' |
      grep '^sha-' |
      while read -r TAG; do
        CREATED=$(docker image inspect "$IMAGE:$TAG" --format '{{.Created}}' 2>/dev/null || true)

        if [[ -n "$CREATED" ]]; then
          printf '%s %s\n' "$CREATED" "$TAG"
        fi
      done |
      sort -r |
      awk '{print $2}'
  )

  if (( ${#SHA_TAGS[@]} > 3 )); then
    for TAG in "${SHA_TAGS[@]:3}"; do
      echo "==> Removing old SHA-tagged image: $IMAGE:$TAG"
      docker rmi "$IMAGE:$TAG" || true
    done
  fi
done

echo "==> Deployment completed successfully."
