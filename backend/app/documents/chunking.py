"""Structure-aware chunking of ``CanonicalDocument`` (Week 6 P8).

CanonicalDocument -> list[Chunk] with deterministic IDs, page provenance and
preserved source metadata (section, language).

Why not Chonkie (the Week 6 plan names Chonkie with an explicit fallback
clause): inspection of the current package showed that chonkie chunkers
operate on a single plain string and expose only text/offset/token_count —
page boundaries, section metadata, ID assignment and overlap bookkeeping
would all remain in this codebase anyway — while pulling in the HuggingFace
``tokenizers``/``hub`` stack, and the 1.x API differs materially from the
0.x line. The plan explicitly authorizes "simple structure-aware chunking"
in that case; this module is that fallback: deterministic, dependency-free,
paragraph/sentence-preferred splitting.

Algorithm (deterministic: no randomness, no clocks, no locale):
1. Each page's text is split into paragraphs on blank lines (``\\n{2,}``);
   each paragraph keeps its page number and the page's ``section`` metadata
   when present. Paragraphs longer than ``chunk_size`` are split at sentence
   boundaries; a sentence still longer than ``chunk_size`` is hard-split at
   whitespace. Atomic pieces therefore always satisfy ``len <= chunk_size``.
2. Pieces are packed greedily into chunks of at most ``chunk_size``
   characters, deliberately ignoring page boundaries so obvious structure
   stays intact; up to ``chunk_overlap`` characters worth of trailing pieces
   of the previous chunk are carried into the next chunk when they fit.
3. Chunk IDs follow ``{document_id}:{seq}`` (zero-based), ``pages`` are the
   sorted unique page numbers of the pieces in the chunk, ``section`` comes
   from the first contributing piece that has one, and ``language`` is the
   document language (never invented).
"""

from __future__ import annotations

import re
from typing import NamedTuple

from pydantic import BaseModel, Field, field_validator, model_validator

from app.config import settings
from app.documents.models import CanonicalDocument, Page

_SECTION_METADATA_KEY = "section"
_PARA_SEP = "\n\n"
_PARA_SEP_LEN = len(_PARA_SEP)
_PARAGRAPH_SPLIT_RE = re.compile(r"\n{2,}")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


class Chunk(BaseModel):
    """A retrieval-ready chunk derived from a ``CanonicalDocument``."""

    document_id: str = Field(min_length=1)
    chunk_id: str = Field(min_length=1)
    text: str
    pages: list[int] = Field(min_length=1)
    section: str | None = None
    language: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)

    @field_validator("text")
    @classmethod
    def _text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Chunk text must not be blank")
        return value

    @field_validator("pages")
    @classmethod
    def _pages_must_be_positive_unique_ascending(cls, value: list[int]) -> list[int]:
        if any(p < 1 for p in value):
            raise ValueError("Page numbers must be >= 1")
        if any(a >= b for a, b in zip(value, value[1:])):
            raise ValueError("Page numbers must be unique and strictly ascending")
        return value

    @model_validator(mode="after")
    def _chunk_id_must_follow_id_rule(self) -> "Chunk":
        prefix = f"{self.document_id}:"
        seq = self.chunk_id.removeprefix(prefix)
        if seq == self.chunk_id or not seq.isdigit():
            raise ValueError(
                f"chunk_id must match '{{document_id}}:{{seq}}' "
                f"(e.g. '{self.document_id}:0'); got {self.chunk_id!r}"
            )
        return self


class _Segment(NamedTuple):
    """An atomic piece of text with its source page and section."""

    text: str
    page_number: int
    section: str | None


def _hard_split(text: str, chunk_size: int) -> list[str]:
    """Split at whitespace; brute-cut any single oversized run."""
    pieces: list[str] = []
    current = ""
    for word in text.split():
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= chunk_size:
            current = f"{current} {word}"
        else:
            pieces.append(current)
            current = word
        while len(current) > chunk_size:
            pieces.append(current[:chunk_size])
            current = current[chunk_size:]
    if current:
        pieces.append(current)
    return pieces


def _split_oversized(
    text: str,
    page_number: int,
    section: str | None,
    chunk_size: int,
) -> list[_Segment]:
    """Split a paragraph longer than ``chunk_size`` at sentence boundaries."""
    segments: list[_Segment] = []
    for sentence in _SENTENCE_SPLIT_RE.split(text):
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(sentence) <= chunk_size:
            segments.append(_Segment(sentence, page_number, section))
        else:
            segments.extend(
                _Segment(piece, page_number, section)
                for piece in _hard_split(sentence, chunk_size)
            )
    return segments


def _page_segments(page: Page, chunk_size: int) -> list[_Segment]:
    """Atomic text pieces of one page, each tagged with page/section."""
    raw_section = page.metadata.get(_SECTION_METADATA_KEY)
    section = raw_section if isinstance(raw_section, str) and raw_section else None

    segments: list[_Segment] = []
    for paragraph in _PARAGRAPH_SPLIT_RE.split(page.text):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if len(paragraph) <= chunk_size:
            segments.append(_Segment(paragraph, page.page_number, section))
        else:
            segments.extend(
                _split_oversized(paragraph, page.page_number, section, chunk_size)
            )
    return segments


def _joined_length(segments: list[_Segment]) -> int:
    """Length of the pieces once joined with the paragraph separator."""
    if not segments:
        return 0
    return sum(len(s.text) for s in segments) + _PARA_SEP_LEN * (len(segments) - 1)


def _overlap_suffix(group: list[_Segment], chunk_overlap: int) -> list[_Segment]:
    """Longest strict suffix of ``group`` whose joined length fits the overlap."""
    suffix: list[_Segment] = []
    length = 0
    for segment in reversed(group[1:]):  # never carry the entire group
        extra = len(segment.text) + (_PARA_SEP_LEN if suffix else 0)
        if length + extra > chunk_overlap:
            break
        suffix.insert(0, segment)
        length += extra
    return suffix


def _pack_segments(
    segments: list[_Segment],
    chunk_size: int,
    chunk_overlap: int,
) -> list[list[_Segment]]:
    """Greedy FIFO packing of atomic segments into size-bounded groups."""
    groups: list[list[_Segment]] = []
    pending = list(reversed(segments))  # list.pop() yields segments in order

    while pending:
        carry: list[_Segment] = []
        if groups and chunk_overlap > 0:
            carry = _overlap_suffix(groups[-1], chunk_overlap)

        current: list[_Segment] = list(carry)
        added = False
        while pending:
            extra = len(pending[-1].text) + (_PARA_SEP_LEN if current else 0)
            if _joined_length(current) + extra > chunk_size:
                break
            current.append(pending.pop())
            added = True

        if not added:
            # The carried overlap alone blocks the first pending segment;
            # restart the chunk without overlap to guarantee progress.
            current = [pending.pop()]

        groups.append(current)

    return groups


def chunk_document(
    document: CanonicalDocument,
    *,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Chunk]:
    """Chunk ``document`` deterministically.

    ``chunk_size``/``chunk_overlap`` default to ``settings.chunk_size`` /
    ``settings.chunk_overlap``. Chunking requires ``1 <= chunk_size`` and
    ``0 <= chunk_overlap < chunk_size`` (``ValueError`` otherwise).

    Empty or whitespace-only pages produce no chunks; a document with no
    usable text yields ``[]`` — no meaningless empty chunks are created.
    """
    size = settings.chunk_size if chunk_size is None else chunk_size
    overlap = settings.chunk_overlap if chunk_overlap is None else chunk_overlap
    if size < 1:
        raise ValueError(f"chunk_size must be >= 1, got {size}")
    if overlap < 0 or overlap >= size:
        raise ValueError(
            f"chunk_overlap must satisfy 0 <= chunk_overlap < chunk_size; "
            f"got chunk_size={size}, chunk_overlap={overlap}"
        )

    segments: list[_Segment] = []
    for page in document.pages:
        segments.extend(_page_segments(page, size))

    chunks: list[Chunk] = []
    for seq, group in enumerate(_pack_segments(segments, size, overlap)):
        text = _PARA_SEP.join(segment.text for segment in group)
        pages = sorted({segment.page_number for segment in group})
        section = next(
            (segment.section for segment in group if segment.section is not None),
            None,
        )
        chunks.append(
            Chunk(
                document_id=document.document_id,
                chunk_id=f"{document.document_id}:{seq}",
                text=text,
                pages=pages,
                section=section,
                language=document.language,
                metadata={"char_count": len(text), "page_count": len(pages)},
            )
        )
    return chunks
