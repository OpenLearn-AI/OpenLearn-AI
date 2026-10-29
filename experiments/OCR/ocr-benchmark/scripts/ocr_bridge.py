#!/usr/bin/env python3
"""Bridge: run ONE file through the production backend OCR chain.

Must be executed with the BACKEND virtualenv python and cwd=backend/
(spawned by BackendChainAdapter). Prints exactly one JSON line:
  {"status": "ok", "text": "..."}   or
  {"status": "error", "error": "..."}
"""

from __future__ import annotations

import asyncio
import json
import sys
import tempfile
from pathlib import Path

BENCH_ROOT = Path(__file__).resolve().parents[1]
REPO = BENCH_ROOT.parents[2]
BACKEND = REPO / "backend"
sys.path.insert(0, str(BACKEND))


def _to_pdf(source: Path, tmp_dir: Path) -> Path:
    """Normalize images to single-page PDFs (provider accepts PDFs only)."""
    if source.suffix.lower() == ".pdf":
        return source
    from PIL import Image  # lazy; provided by the backend env

    img = Image.open(source).convert("RGB")
    out = tmp_dir / (source.stem + ".pdf")
    img.save(out, "PDF", resolution=150.0)
    return out


def main() -> int:
    # --- benchmark bridge: load backend/.env into os.environ (stdlib only) ---
    import os as _os
    from pathlib import Path as _P
    _envf = _P.cwd() / ".env"
    if _envf.exists():
        for _ln in _envf.read_text(encoding="utf-8", errors="replace").splitlines():
            _ln = _ln.strip()
            if not _ln or _ln.startswith("#") or "=" not in _ln:
                continue
            _k, _, _v = _ln.partition("=")
            _os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

    if len(sys.argv) != 2:
        print(json.dumps({"status": "error",
                          "error": "usage: ocr_bridge.py <file>"},
                         ensure_ascii=True))
        return 0
    source = Path(sys.argv[1]).resolve()
    try:
        # NOTE: direct provider import instead of the factory.
        # get_ocr_provider("gemini") is exactly
        # `return GeminiOCRProvider()` (no extra logic), but the
        # factory module eagerly imports ALL providers
        # (litellm -> openai, embedding, vector_db) which are
        # irrelevant to the OCR chain and missing from local
        # dev venvs.
        from app.pal.providers.ocr.gemini_provider import GeminiOCRProvider

        provider = GeminiOCRProvider()
        tmp_dir = Path(tempfile.mkdtemp(prefix="ocrbench_"))
        pdf_path = _to_pdf(source, tmp_dir)
        result = asyncio.run(provider.extract_text(str(pdf_path)))
        # optional pacing between samples (Gemini free-tier RPM protection)
        import time as _t
        import os as _to
        _pace = float(_to.environ.get("OCRBENCH_PACING_S", "0") or 0)
        if _pace > 0:
            _t.sleep(_pace)
        print(json.dumps({"status": "ok", "text": result.text},
                         ensure_ascii=True))
    except Exception as exc:  # noqa: BLE001 - report, never crash ugly
        print(json.dumps(
            {"status": "error",
             "error": f"{type(exc).__name__}: {exc}"},
            ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
