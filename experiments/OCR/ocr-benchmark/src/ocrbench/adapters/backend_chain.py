"""Adapter: run samples through the REAL backend OCR chain.

Strategy: subprocess bridge into the backend's own virtualenv calling
app.pal.factory.get_ocr_provider("gemini") -> extract_text() — the exact
production path (PAL contract), not a parallel implementation.

Images (PNG/JPG) are normalized to single-page PDFs inside the bridge,
because the production GeminiOCRProvider accepts PDF sources only
(see backend/app/pal/providers/ocr/gemini_provider.py).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from .base import EngineAdapter

BENCH_ROOT = Path(__file__).resolve().parents[3]
REPO = BENCH_ROOT.parents[2]
BACKEND = REPO / "backend"
BRIDGE = BENCH_ROOT / "scripts" / "ocr_bridge.py"
GEMINI_TIMEOUT_S = 300


def _venv_python() -> Path:
    for rel in (("Scripts", "python.exe"), ("bin", "python")):
        p = BACKEND / ".venv" / Path(*rel)
        if p.exists():
            return p
    raise FileNotFoundError(
        f"backend virtualenv python not found under {BACKEND / '.venv'}")


class BackendChainAdapter(EngineAdapter):
    name = "backend_chain"

    def run(self, sample_path: Path, languages: list) -> str:
        cmd = [str(_venv_python()), str(BRIDGE), str(sample_path)]
        proc = subprocess.run(
            cmd,
            cwd=str(BACKEND),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=GEMINI_TIMEOUT_S,
        )
        lines = [l for l in proc.stdout.splitlines() if l.strip()]
        if proc.returncode != 0 and not lines:
            raise RuntimeError(
                f"bridge crashed: {proc.stderr.strip()[-500:]}")
        if not lines:
            raise RuntimeError(
                f"bridge produced no output; stderr={proc.stderr.strip()[-300:]}")
        payload = json.loads(lines[-1])
        if payload.get("status") != "ok":
            raise RuntimeError(payload.get("error", "unknown bridge error"))
        return payload["text"]
