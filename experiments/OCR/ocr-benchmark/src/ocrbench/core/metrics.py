"""OCR evaluation metrics: CER and WER.

Pure stdlib (per ADR-0001: runtime deps stay empty).
Unicode-safe (Arabic + English).
"""

from __future__ import annotations

import re

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Collapse whitespace runs into single spaces and strip ends."""
    return _WHITESPACE_RE.sub(" ", text).strip()


def _levenshtein(a, b) -> int:
    """Edit distance over any sequences (string chars or word lists)."""
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i]
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            cur.append(min(
                prev[j] + 1,         # deletion
                cur[j - 1] + 1,      # insertion
                prev[j - 1] + cost,  # substitution
            ))
        prev = cur
    return prev[-1]


def cer(reference: str, hypothesis: str, *, normalize: bool = True) -> float:
    """Character Error Rate: edit distance over chars / len(reference)."""
    ref = normalize_text(reference) if normalize else reference
    hyp = normalize_text(hypothesis) if normalize else hypothesis
    if not ref:
        return 0.0 if not hyp else 1.0
    return _levenshtein(ref, hyp) / len(ref)


def wer(reference: str, hypothesis: str, *, normalize: bool = True) -> float:
    """Word Error Rate: edit distance over words / len(reference words)."""
    ref = (normalize_text(reference) if normalize else reference).split()
    hyp = (normalize_text(hypothesis) if normalize else hypothesis).split()
    if not ref:
        return 0.0 if not hyp else 1.0
    return _levenshtein(ref, hyp) / len(ref)
