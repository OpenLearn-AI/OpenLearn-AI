"""Guard against drift between the app and the tracked docs/openapi.json.

The tracked document is generated, never hand-edited, so this test compares
parsed JSON structures (not text) and fails with regeneration instructions.
"""

import json
from pathlib import Path

from app.main import app

# backend/tests/test_openapi_contract.py -> tests -> backend -> repository root
REPO_ROOT = Path(__file__).resolve().parents[2]
TRACKED_OPENAPI = REPO_ROOT / "docs" / "openapi.json"

REGENERATE_HINT = (
    "docs/openapi.json is stale — regenerate it from the repository's backend/ "
    "directory (the command must be run from backend/):\n"
    "\n"
    "    cd backend\n"
    "    python -m app.openapi_export\n"
)


def test_tracked_openapi_matches_application() -> None:
    generated = app.openapi()

    assert TRACKED_OPENAPI.exists(), (
        f"{TRACKED_OPENAPI} does not exist.\n{REGENERATE_HINT}"
    )

    tracked = json.loads(TRACKED_OPENAPI.read_text(encoding="utf-8"))

    assert tracked == generated, REGENERATE_HINT
