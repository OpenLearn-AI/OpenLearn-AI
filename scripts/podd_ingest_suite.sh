#!/usr/bin/env bash
# podd_ingest_suite.sh — W10 Task 1 (Pod D / Hisham) — VPS-side wrapper.
# Usage (repo root, staging compose up):
#   bash scripts/podd_ingest_suite.sh seed <SUB>
#       -> pushes+runs podd_ingest_seed.py inside the worker container
#   bash scripts/podd_ingest_suite.sh fixtures <a.pdf> [b.pdf ...]
#       -> pushes runner+fixtures, builds manifest, runs the real-HTTP suite,
#          copies the evidence bundle back to ./evidence/
# Optional env: PODD_SCANNED="2,3" (1-based fixture indices = scanned),
#   PODD_POLL_TIMEOUT, PODD_MAX_OCR_FIXTURES, PODD_CATEGORY
set -euo pipefail

MODE="${1:-}"
case "$MODE" in
  seed)     SUB="${2:?usage: $0 seed <SUB-from-bootstrap>}"; shift 2 ;;
  fixtures) shift ;;
  *)        echo ">>> usage: $0 seed <SUB> | fixtures <a.pdf> [b.pdf ...]"; exit 1 ;;
esac

CID="$(docker ps --filter label=com.docker.compose.service=celery_worker --format '{{.ID}}' | head -1)"
[ -n "$CID" ] || { echo ">>> FAIL: celery_worker container not found (staging compose up?)"; exit 1; }
echo ">>> worker container: $CID"

APPDIR=""
for CAND in /app /backend /srv /workspace /opt/app /code; do
  if docker exec -w "$CAND" "$CID" python -c 'import app' >/dev/null 2>&1; then APPDIR="$CAND"; break; fi
done
if [ -z "$APPDIR" ]; then
  APPDIR="$(docker exec "$CID" python -c 'import app,os; print(os.path.dirname(os.path.dirname(os.path.abspath(app.__file__))))' 2>/dev/null || true)"
fi
[ -n "$APPDIR" ] || { echo ">>> FAIL: app import context not found — send me: docker exec $CID pwd"; exit 1; }
echo ">>> app import context: $APPDIR"
BASE_PYPTH="$(docker exec "$CID" sh -c 'printf %s "${PYTHONPATH:-}"' 2>/dev/null || true)"
PYPATH="$APPDIR"; [ -n "$BASE_PYPTH" ] && PYPATH="$APPDIR:$BASE_PYPTH"

if [ "$MODE" = "seed" ]; then
  docker cp scripts/podd_ingest_seed.py "$CID":/tmp/podd_ingest_seed.py
  docker exec -w "$APPDIR" -e PYTHONPATH="$PYPATH" "$CID" \
    python /tmp/podd_ingest_seed.py --sub "$SUB"
  exit 0
fi

[ "$#" -ge 1 ] || { echo ">>> usage: $0 fixtures <a.pdf> [b.pdf ...]"; exit 1; }
for f in "$@"; do [ -f "$f" ] || { echo ">>> FAIL: fixture not found: $f"; exit 1; }; done

docker exec "$CID" mkdir -p /tmp/podd_fixtures
i=1
for f in "$@"; do
  docker cp "$f" "$CID":/tmp/podd_fixtures/fx${i}.pdf
  i=$((i+1))
done

MF_HOST="$(mktemp)"
python3 - "$MF_HOST" "$@" <<'MF_EOF'
import json, os, sys
mf, files = sys.argv[1], sys.argv[2:]
scanned = set((os.environ.get("PODD_SCANNED") or "").split(","))
fixtures = []
for i, p in enumerate(files, 1):
    fixtures.append({
        "id": "fx%d" % i,
        "file": "fx%d.pdf" % i,
        "title": os.path.splitext(os.path.basename(p))[0][:200],
        "category": os.environ.get("PODD_CATEGORY", "w10-manual"),
        "scanned": str(i) in scanned,
    })
json.dump({"fixtures": fixtures}, open(mf, "w"), indent=1)
print("manifest fixtures:", len(fixtures))
MF_EOF
docker cp "$MF_HOST" "$CID":/tmp/podd_manifest.json
rm -f "$MF_HOST"
docker cp scripts/podd_ingest_suite.py "$CID":/tmp/podd_ingest_suite.py

DOCKER_ENV=()
[ -n "${PODD_API_BASE:-}" ]         && DOCKER_ENV+=(-e PODD_API_BASE)
[ -n "${PODD_KC_BASE:-}" ]          && DOCKER_ENV+=(-e PODD_KC_BASE)
[ -n "${PODD_CLIENT_ID:-}" ]        && DOCKER_ENV+=(-e PODD_CLIENT_ID)
[ -n "${PODD_RUNNER_USER:-}" ]      && DOCKER_ENV+=(-e PODD_RUNNER_USER)
[ -n "${PODD_RUNNER_PASS:-}" ]      && DOCKER_ENV+=(-e PODD_RUNNER_PASS)
[ -n "${PODD_POLL_TIMEOUT:-}" ]     && DOCKER_ENV+=(-e PODD_POLL_TIMEOUT)
[ -n "${PODD_MAX_OCR_FIXTURES:-}" ] && DOCKER_ENV+=(-e PODD_MAX_OCR_FIXTURES)

docker exec -w "$APPDIR" -e PYTHONPATH="$PYPATH" "${DOCKER_ENV[@]}" "$CID" \
  python /tmp/podd_ingest_suite.py \
  --manifest /tmp/podd_manifest.json --fixtures-dir /tmp/podd_fixtures

mkdir -p evidence
LATEST="$(docker exec "$CID" sh -c 'ls -1t /tmp/podd_evidence_*.json 2>/dev/null | head -1')"
if [ -n "$LATEST" ]; then
  docker cp "$CID:$LATEST" "evidence/$(basename "$LATEST")"
  echo ">>> evidence: evidence/$(basename "$LATEST")"
fi
