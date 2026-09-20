#!/usr/bin/env bash

set -euo pipefail

IMAGE_TAG="${1:-}"

if [[ -z "$IMAGE_TAG" ]]; then
  echo "ERROR: Image tag is required."
  echo "Usage: ./infra/deploy.sh sha-<commit-sha>"
  exit 1
fi

if [[ "$IMAGE_TAG" != sha-* ]]; then
  echo "ERROR: IMAGE_TAG must be a SHA tag."
  echo "Expected format: sha-<commit-sha>"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

COMPOSE_FILE="docker-compose.staging.yml"
ENV_FILE=".env.runtime"

BACKEND_IMAGE="ghcr.io/openlearn-ai/openlearn-backend"
FRONTEND_IMAGE="ghcr.io/openlearn-ai/openlearn-frontend"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: $ENV_FILE not found."
  exit 1
fi

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "ERROR: $COMPOSE_FILE not found."
  exit 1
fi

export IMAGE_TAG

SKIP_MIGRATIONS="${SKIP_MIGRATIONS:-0}"
SKIP_DISK_GUARD="${SKIP_DISK_GUARD:-0}"

if [[ "$SKIP_MIGRATIONS" != "0" && "$SKIP_MIGRATIONS" != "1" ]]; then
  echo "ERROR: SKIP_MIGRATIONS must be 0 or 1."
  exit 1
fi

if [[ "$SKIP_DISK_GUARD" != "0" && "$SKIP_DISK_GUARD" != "1" ]]; then
  echo "ERROR: SKIP_DISK_GUARD must be 0 or 1."
  exit 1
fi

echo "==> Deploying image tag: $IMAGE_TAG"

# Helpers
get_disk_stats() {
  df -B1 / | awk 'NR==2 {print $2, $3, $4, $5}'
}

format_gib() {
  awk -v bytes="$1" 'BEGIN {printf "%.2f GiB", bytes / 1024 / 1024 / 1024}'
}

image_is_referenced_by_any_container() {
  local target_image_id="$1"
  local container_id
  local container_image_id

  while IFS= read -r container_id; do
    [[ -z "$container_id" ]] && continue

    container_image_id="$(
      docker inspect \
        --format '{{.Image}}' \
        "$container_id" \
        2>/dev/null || true
    )"

    if [[ "$container_image_id" == "$target_image_id" ]]; then
      return 0
    fi
  done < <(docker ps -aq)

  return 1
}

cleanup_openlearn_old_images() {
  local image
  local tag
  local image_id
  local -a SHA_TAGS

  for image in "$BACKEND_IMAGE" "$FRONTEND_IMAGE"; do
    echo "==> Cleaning old SHA-tagged images for $image..."

    mapfile -t SHA_TAGS < <(
      docker images "$image" --format '{{.Tag}}' |
        grep '^sha-' |
        sort -u || true
    )

    for tag in "${SHA_TAGS[@]}"; do
      if [[ "$tag" == "$IMAGE_TAG" ]]; then
        echo "    Keeping current release: $image:$tag"
        continue
      fi

      image_id="$(
        docker image inspect \
          "$image:$tag" \
          --format '{{.Id}}' \
          2>/dev/null || true
      )"

      if [[ -z "$image_id" ]]; then
        echo "    Skipping $image:$tag (image no longer exists)"
        continue
      fi

      if image_is_referenced_by_any_container "$image_id"; then
        echo "    Keeping $image:$tag (referenced by a container)"
        continue
      fi

      echo "    Removing unused old release: $image:$tag"
      docker image rm "$image:$tag"
    done
  done

  echo "==> Removing dangling images..."
  docker image prune -f
}

calculate_release_guard() {
  if [[ "$SKIP_DISK_GUARD" == "1" ]]; then
    echo
    echo "WARN: SKIP_DISK_GUARD=1 — disk guard bypassed."
    echo "      Emergency use only. Verify disk space manually."
    echo
    return 0
  fi

  local total_bytes
  local used_bytes
  local available_bytes
  local usage_percent

  read -r total_bytes used_bytes available_bytes usage_percent <<< "$(get_disk_stats)"

  if [[ -z "$total_bytes" || -z "$available_bytes" ]]; then
    echo "ERROR: Could not inspect root filesystem disk usage."
    exit 1
  fi

  local backend_container_id
  local frontend_container_id
  local backend_image_id
  local frontend_image_id
  local backend_size
  local frontend_size

  backend_container_id="$(
    docker compose \
      --env-file "$ENV_FILE" \
      -f "$COMPOSE_FILE" \
      ps -q backend
  )"

  frontend_container_id="$(
    docker compose \
      --env-file "$ENV_FILE" \
      -f "$COMPOSE_FILE" \
      ps -q frontend
  )"

  if [[ -z "$backend_container_id" ]]; then
    echo "ERROR: Could not find the currently running backend container."
    echo "       Disk guard cannot safely estimate release size."
    exit 1
  fi

  if [[ -z "$frontend_container_id" ]]; then
    echo "ERROR: Could not find the currently running frontend container."
    echo "       Disk guard cannot safely estimate release size."
    exit 1
  fi

  backend_image_id="$(
    docker inspect \
      --format '{{.Image}}' \
      "$backend_container_id" \
      2>/dev/null || true
  )"

  frontend_image_id="$(
    docker inspect \
      --format '{{.Image}}' \
      "$frontend_container_id" \
      2>/dev/null || true
  )"

  if [[ -z "$backend_image_id" ]]; then
    echo "ERROR: Could not determine the running backend image ID."
    exit 1
  fi

  if [[ -z "$frontend_image_id" ]]; then
    echo "ERROR: Could not determine the running frontend image ID."
    exit 1
  fi

  backend_size="$(
    docker image inspect \
      "$backend_image_id" \
      --format '{{.Size}}' \
      2>/dev/null || true
  )"

  frontend_size="$(
    docker image inspect \
      "$frontend_image_id" \
      --format '{{.Size}}' \
      2>/dev/null || true
  )"

  if [[ -z "$backend_size" || -z "$frontend_size" ]]; then
    echo "ERROR: Could not inspect the current backend/frontend image sizes."
    echo "       Disk guard is fail-closed; deployment aborted."
    exit 1
  fi

  if ! [[ "$backend_size" =~ ^[0-9]+$ && "$frontend_size" =~ ^[0-9]+$ ]]; then
    echo "ERROR: Invalid image size returned by Docker."
    exit 1
  fi

  local predicted_release_bytes
  local five_percent_bytes
  local minimum_margin_bytes
  local safety_margin_bytes
  local required_free_bytes

  predicted_release_bytes=$((backend_size + frontend_size))

  five_percent_bytes=$((total_bytes * 5 / 100))
  minimum_margin_bytes=$((2 * 1024 * 1024 * 1024))

  if (( five_percent_bytes > minimum_margin_bytes )); then
    safety_margin_bytes="$five_percent_bytes"
  else
    safety_margin_bytes="$minimum_margin_bytes"
  fi

  required_free_bytes=$((predicted_release_bytes + safety_margin_bytes))

  echo
  echo "==> Disk pre-flight guard"
  echo "    Disk total:          $(format_gib "$total_bytes")"
  echo "    Disk used:           $(format_gib "$used_bytes")"
  echo "    Disk available:      $(format_gib "$available_bytes")"
  echo "    Backend image:       $(format_gib "$backend_size")"
  echo "    Frontend image:      $(format_gib "$frontend_size")"
  echo "    Predicted release:   $(format_gib "$predicted_release_bytes")"
  echo "    Safety margin:       $(format_gib "$safety_margin_bytes")"
  echo "    Required free:       $(format_gib "$required_free_bytes")"
  echo

  if (( available_bytes < required_free_bytes )); then
    echo "ERROR: Insufficient disk space for deployment."
    echo "       Deployment aborted before image pull."
    echo "       Available: $(format_gib "$available_bytes")"
    echo "       Required:  $(format_gib "$required_free_bytes")"
    exit 1
  fi

  echo "==> Disk guard passed."
}

# 1. Pre-clean
echo "==> Pre-deploy cleanup..."
cleanup_openlearn_old_images

# 2. Disk guard
calculate_release_guard

read -r PRE_PULL_TOTAL PRE_PULL_USED PRE_PULL_AVAILABLE PRE_PULL_PERCENT <<< "$(get_disk_stats)"

echo
echo "==> Disk before image pull:"
echo "    Available: $(format_gib "$PRE_PULL_AVAILABLE")"
echo

# 3. Pull
echo "==> Pulling images..."

docker compose \
  --env-file "$ENV_FILE" \
  -f "$COMPOSE_FILE" \
  pull

read -r POST_PULL_TOTAL POST_PULL_USED POST_PULL_AVAILABLE POST_PULL_PERCENT <<< "$(get_disk_stats)"

if [[ -n "$PRE_PULL_AVAILABLE" && -n "$POST_PULL_AVAILABLE" ]]; then
  ACTUAL_PULL_BYTES=$((PRE_PULL_AVAILABLE - POST_PULL_AVAILABLE))

  if (( ACTUAL_PULL_BYTES < 0 )); then
    ACTUAL_PULL_BYTES=0
  fi

  echo
  echo "==> Pull telemetry:"
  echo "    Free before pull:   $(format_gib "$PRE_PULL_AVAILABLE")"
  echo "    Free after pull:    $(format_gib "$POST_PULL_AVAILABLE")"
  echo "    Actual pull delta:  $(format_gib "$ACTUAL_PULL_BYTES")"
fi

# 4. Start database
echo "==> Starting database..."

docker compose \
  --env-file "$ENV_FILE" \
  -f "$COMPOSE_FILE" \
  up -d db --wait

# 5. Migrations
if [[ "$SKIP_MIGRATIONS" == "1" ]]; then
  echo "==> SKIP_MIGRATIONS=1 — skipping database migrations."
else
  echo "==> Running database migrations..."

  docker compose \
    --env-file "$ENV_FILE" \
    -f "$COMPOSE_FILE" \
    run --rm --no-deps backend alembic upgrade head
fi

# 6. Start services
echo "==> Starting services..."

docker compose \
  --env-file "$ENV_FILE" \
  -f "$COMPOSE_FILE" \
  up -d --remove-orphans --wait --wait-timeout 180

# 7. Health checks
echo "==> Checking backend..."

curl --fail --silent --show-error \
  http://127.0.0.1:8000/health > /dev/null

echo "==> Backend health check passed."

echo "==> Checking frontend..."

curl --fail --silent --show-error \
  http://127.0.0.1:3000/ > /dev/null

echo "==> Frontend health check passed."

# 8. Post-health cleanup
echo "==> Post-health cleanup..."
cleanup_openlearn_old_images

# 9. Final telemetry
read -r FINAL_TOTAL FINAL_USED FINAL_AVAILABLE FINAL_PERCENT <<< "$(get_disk_stats)"

echo
echo "==> Final disk telemetry:"
echo "    Disk total:     $(format_gib "$FINAL_TOTAL")"
echo "    Disk used:      $(format_gib "$FINAL_USED")"
echo "    Disk available: $(format_gib "$FINAL_AVAILABLE")"
echo "    Disk usage:     $FINAL_PERCENT"

if [[ -n "$PRE_PULL_AVAILABLE" && -n "$FINAL_AVAILABLE" ]]; then
  NET_DISK_DELTA=$((PRE_PULL_AVAILABLE - FINAL_AVAILABLE))

  echo "    Net deployment delta: $(format_gib "$NET_DISK_DELTA")"
fi

echo
echo "==> Deployment completed successfully."
