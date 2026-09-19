"""P8 tests: deterministic structure-aware chunking of CanonicalDocument."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from app.config import settings
from app.documents import CanonicalDocument, Chunk, Page
from app.documents.chunking import chunk_document


@pytest.fixture()
def chunk_config(monkeypatch: pytest.MonkeyPatch) -> Callable[[int, int], None]:
    """Setter for the application chunking configuration for the test."""

    def _set(size: int, overlap: int) -> None:
        monkeypatch.setattr(settings, "chunk_size", size)
        monkeypatch.setattr(settings, "chunk_overlap", overlap)

    return _set


def _doc(pages: list[Page], *, language: str | None = None) -> CanonicalDocument:
    return CanonicalDocument(
        document_id="doc-123",
        source="/docs/doc-123.pdf",
        language=language,
        pages=pages,
    )


# ---------------------------------------------------------------------------
# Basic behavior
# ---------------------------------------------------------------------------


def test_small_document_produces_multiple_chunks() -> None:
    doc = _doc(
        [Page(page_number=1, text="Alpha paragraph.\n\nBeta paragraph.\n\nGamma paragraph.")]
    )

    chunks = chunk_document(doc, chunk_size=35, chunk_overlap=0)

    assert len(chunks) == 2
    assert chunks[0].text == "Alpha paragraph.\n\nBeta paragraph."
    assert chunks[1].text == "Gamma paragraph."
    assert all(isinstance(c, Chunk) for c in chunks)
    assert "\n\n" in chunks[0].text  # paragraph structure kept inside chunks


def test_chunking_is_deterministic() -> None:
    doc = _doc(
        [
            Page(page_number=1, text="Page one alpha.\n\nPage one beta."),
            Page(page_number=2, text="Page two alpha."),
            Page(page_number=3, text="Page three text."),
        ],
        language="en",
    )

    first = chunk_document(doc, chunk_size=40, chunk_overlap=10)
    second = chunk_document(doc, chunk_size=40, chunk_overlap=10)

    assert [c.model_dump() for c in first] == [c.model_dump() for c in second]
    assert [c.chunk_id for c in first] == [c.chunk_id for c in second]


# ---------------------------------------------------------------------------
# Metadata preservation
# ---------------------------------------------------------------------------


def test_document_and_source_metadata_are_preserved() -> None:
    doc = _doc(
        [
            Page(
                page_number=1,
                text="Some content here.",
                metadata={"section": "Introduction"},
            )
        ],
        language="en",
    )

    chunks = chunk_document(doc, chunk_size=100, chunk_overlap=0)

    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.document_id == "doc-123"
    assert chunk.pages == [1]
    assert chunk.language == "en"
    assert chunk.section == "Introduction"


def test_language_is_none_when_document_has_none() -> None:
    doc = _doc([Page(page_number=1, text="Some content here.")])

    (chunk,) = chunk_document(doc, chunk_size=100, chunk_overlap=0)

    assert chunk.language is None  # never invented


def test_section_metadata_propagates_from_pages() -> None:
    doc = _doc(
        [
            Page(page_number=1, text="Alpha page text.", metadata={"section": "Introduction"}),
            Page(page_number=2, text="Beta page text.", metadata={"section": "Methods"}),
        ]
    )

    chunks = chunk_document(doc, chunk_size=30, chunk_overlap=0)

    assert [c.section for c in chunks] == ["Introduction", "Methods"]


def test_spanning_chunk_takes_section_of_first_contributing_page() -> None:
    doc = _doc(
        [
            Page(page_number=1, text="Alpha page text.", metadata={"section": "Introduction"}),
            Page(page_number=2, text="Beta page text.", metadata={"section": "Methods"}),
        ]
    )

    (chunk,) = chunk_document(doc, chunk_size=100, chunk_overlap=0)

    assert chunk.pages == [1, 2]
    assert chunk.section == "Introduction"


# ---------------------------------------------------------------------------
# IDs
# ---------------------------------------------------------------------------


def test_chunk_ids_follow_required_format() -> None:
    doc = _doc(
        [Page(page_number=1, text="Alpha paragraph.\n\nBeta paragraph.\n\nGamma paragraph.")]
    )

    chunks = chunk_document(doc, chunk_size=35, chunk_overlap=0)

    assert [c.chunk_id for c in chunks] == ["doc-123:0", "doc-123:1"]


# ---------------------------------------------------------------------------
# Page provenance
# ---------------------------------------------------------------------------


def test_single_page_chunk_preserves_page_number() -> None:
    doc = _doc([Page(page_number=1, text="Hello.\n\nWorld.")])

    (chunk,) = chunk_document(doc, chunk_size=100, chunk_overlap=0)

    assert chunk.pages == [1]
    assert chunk.text == "Hello.\n\nWorld."


def test_pages_preserved_across_multipage_chunks() -> None:
    doc = _doc(
        [
            Page(page_number=1, text="One intro paragraph."),
            Page(page_number=2, text="Second page paragraph."),
            Page(page_number=3, text="Third page paragraph."),
        ]
    )

    chunks = chunk_document(doc, chunk_size=45, chunk_overlap=0)

    assert [c.pages for c in chunks] == [[1, 2], [3]]  # spanning + single
    assert chunks[0].text == "One intro paragraph.\n\nSecond page paragraph."


# ---------------------------------------------------------------------------
# Empty / invalid content
# ---------------------------------------------------------------------------


def test_empty_document_returns_no_chunks() -> None:
    doc = _doc([])

    assert chunk_document(doc) == []


def test_blank_pages_produce_no_chunks() -> None:
    doc = _doc([Page(page_number=1, text=""), Page(page_number=2, text="   \n\t ")])

    assert chunk_document(doc) == []


def test_blank_page_is_skipped_but_real_pages_are_chunked() -> None:
    doc = _doc([Page(page_number=1, text=""), Page(page_number=2, text="Real content here.")])

    chunks = chunk_document(doc, chunk_size=50, chunk_overlap=0)

    assert [c.pages for c in chunks] == [[2]]


# ---------------------------------------------------------------------------
# Structure-aware splitting
# ---------------------------------------------------------------------------


def test_oversized_paragraph_splits_at_sentence_boundaries() -> None:
    doc = _doc(
        [Page(page_number=1, text="One two three. Four five six. Seven eight nine.")]
    )

    chunks = chunk_document(doc, chunk_size=20, chunk_overlap=0)

    assert [c.text for c in chunks] == [
        "One two three.",
        "Four five six.",
        "Seven eight nine.",
    ]


def test_hard_split_of_unpunctuated_run_at_word_boundaries() -> None:
    doc = _doc([Page(page_number=1, text="alpha beta gamma delta epsilon zeta")])

    chunks = chunk_document(doc, chunk_size=15, chunk_overlap=0)

    assert [c.text for c in chunks] == ["alpha beta", "gamma delta", "epsilon zeta"]


def test_all_chunks_respect_configured_max_size() -> None:
    long_text = ". ".join(f"Sentence number {i} with words" for i in range(30))
    doc = _doc([Page(page_number=1, text=long_text)])

    chunks = chunk_document(doc, chunk_size=100, chunk_overlap=0)

    assert len(chunks) > 3
    assert all(len(c.text) <= 100 for c in chunks)
    assert all(c.text.strip() for c in chunks)  # no empty/meaningless chunks


def test_chunk_overlap_carries_trailing_paragraph() -> None:
    doc = _doc([Page(page_number=1, text="P1\n\nP2\n\nP3")])

    chunks = chunk_document(doc, chunk_size=6, chunk_overlap=4)

    assert [c.chunk_id for c in chunks] == ["doc-123:0", "doc-123:1"]
    assert [c.text for c in chunks] == ["P1\n\nP2", "P2\n\nP3"]  # P2 overlaps
    assert all(c.pages == [1] for c in chunks)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def test_configuration_defaults_read_from_settings(
    chunk_config: Callable[[int, int], None],
) -> None:
    chunk_config(9, 0)
    doc = _doc([Page(page_number=1, text="aaaa\n\nbbbb")])

    chunks = chunk_document(doc)  # no explicit params: must read settings

    assert [c.text for c in chunks] == ["aaaa", "bbbb"]


@pytest.mark.parametrize(
    ("size", "overlap"),
    [(0, 0), (-5, 0), (100, -1), (100, 100), (100, 150)],
)
def test_invalid_configuration_raises_value_error(size: int, overlap: int) -> None:
    doc = _doc([Page(page_number=1, text="x")])

    with pytest.raises(ValueError):
        chunk_document(doc, chunk_size=size, chunk_overlap=overlap)


# ---------------------------------------------------------------------------
# Chunk model invariants
# ---------------------------------------------------------------------------


def test_chunk_model_accepts_valid_minimal_chunk() -> None:
    chunk = Chunk(document_id="doc", chunk_id="doc:0", text="body", pages=[1])

    assert chunk.metadata == {}
    assert chunk.section is None


@pytest.mark.parametrize("bad_text", ["", "   \n\t"])
def test_chunk_model_rejects_blank_text(bad_text: str) -> None:
    with pytest.raises(ValueError, match="blank"):
        Chunk(document_id="doc", chunk_id="doc:0", text=bad_text, pages=[1])


@pytest.mark.parametrize("bad_id", ["doc", "other:0", "doc:", "doc:x", "doc:0a"])
def test_chunk_model_rejects_malformed_chunk_id(bad_id: str) -> None:
    with pytest.raises(ValueError, match="chunk_id must match"):
        Chunk(document_id="doc", chunk_id=bad_id, text="body", pages=[1])


@pytest.mark.parametrize("bad_pages", [[], [0], [2, 1], [1, 1]])
def test_chunk_model_rejects_invalid_page_lists(bad_pages: list[int]) -> None:
    with pytest.raises(ValueError):
        Chunk(document_id="doc", chunk_id="doc:0", text="body", pages=bad_pages)
