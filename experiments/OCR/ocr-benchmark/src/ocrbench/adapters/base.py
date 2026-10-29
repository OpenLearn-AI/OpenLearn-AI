"""EngineAdapter contract + registry.

Per ADR-0001: each OCR engine gets its own pinned environment, so engine
imports are lazy and optional. The benchmark core never depends on an
engine directly — adapters own their engine access.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

_REGISTRY: dict = {}


class EngineAdapter(ABC):
    """One adapter = one way to turn a sample file into extracted text."""

    name: str = "base"

    @abstractmethod
    def run(self, sample_path: Path, languages: list) -> str:
        """Return the extracted text (or markdown) for one sample."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        _REGISTRY[cls.name] = cls


def available_engines() -> list:
    return sorted(_REGISTRY)


def get_adapter(name: str) -> EngineAdapter:
    # ensure built-in adapters are registered (lazy import)
    from . import backend_chain  # noqa: F401
    from . import mock  # noqa: F401
    if name not in _REGISTRY:
        raise KeyError(
            "unknown engine '%s' - available: %s" % (name, available_engines())
        )
    return _REGISTRY[name]()
