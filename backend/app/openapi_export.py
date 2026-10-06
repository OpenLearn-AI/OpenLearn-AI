"""Regenerate the tracked OpenAPI document from the live FastAPI application.

Usage (run from ``backend/``)::

    python -m app.openapi_export

Writes ``docs/openapi.json`` at the repository root with deterministic
formatting (2-space indent, sorted keys, trailing newline) so the tracked file
has no spurious diff. The output path is derived from this module's location,
not the current working directory, but the command still has to be run from
``backend/`` so that the ``app`` package is importable.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.main import app

# app/openapi_export.py -> app -> backend -> repository root
REPO_ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = REPO_ROOT / "docs" / "openapi.json"


def render() -> str:
    """Return the OpenAPI document as the exact text written to disk."""
    return json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n"


def main() -> None:
    OPENAPI_PATH.parent.mkdir(parents=True, exist_ok=True)
    OPENAPI_PATH.write_text(render(), encoding="utf-8")
    print(f"Wrote {OPENAPI_PATH}")


if __name__ == "__main__":
    main()