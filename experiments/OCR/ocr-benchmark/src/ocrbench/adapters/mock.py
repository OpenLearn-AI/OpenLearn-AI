"""Mock adapter: plumbing only.

Returns empty text, so CER will be 1.0 against any non-empty GT.
Used to validate the full runner loop without any OCR engine.
"""

from __future__ import annotations

from pathlib import Path

from .base import EngineAdapter


class MockAdapter(EngineAdapter):
    name = "mock"

    def run(self, sample_path: Path, languages: list) -> str:
        return ""
