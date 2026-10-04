"""Unit tests for the Stage-1 pipeline composition (B2).

Covers ``app.services.document_pipeline.ingest_and_enrich`` — the
composition of the existing ingestion and targeted-OCR services only.
Following the repository's established conventions:

* Docling's ``DocumentConverter`` is patched at the import location used by
  the production module (``app.services.ingestion.DocumentConverter``), so
  no real conversion, model download, network access, or OCR is performed
  (same isolation strategy as ``tests/documents/test_ingestion.py``);
* the default-resolver tests use a genuine deterministic multi-page PDF
  built as raw bytes so the real ``pdf_page_source_resolver`` composition is
  exercised end-to-end (same fixture strategy as
  ``tests/services/test_ocr_source.py``);
* the OCR provider and page-source resolver are deterministic in-process
  fakes bound to the frozen ``OCRInterface`` contract; async tests carry
  explicit ``@pytest.mark.asyncio`` markers for the repository's strict
  asyncio mode.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from unittest.mock import MagicMock

import pypdfium2 as pdfium
import pytest
from docling.datamodel.base_models import ConversionStatus, ErrorItem
from docling.datamodel.document import ConversionResult
from docling_core.types.doc.document import (
    DoclingDocument,
    DocumentOrigin,
    PageItem,
    ProvenanceItem,
    Size,
    TextItem,
)
from docling_core.types.doc.labels import DocItemLabel

from app.config import settings
from app.documents import CanonicalDocument, Page
from app.pal.exceptions import ProviderTimeoutError
from app.pal.interfaces.ocr import OCRInterface
from app.pal.models.types import HealthStatus, OCRResult
from app.services.document_pipeline import ingest_and_enrich

# ---------------------------------------------------------------------------
# Deterministic real-PDF fixture (hand-written minimal PDF, base-14 font)
# ---------------------------------------------------------------------------


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def _build_multipage_pdf(page_texts: list[str]) -> bytes:
    """Build a valid deterministic multi-page PDF, one text marker per page.

    Object layout: 1=Catalog, 2=Pages tree, then per page i (0-based):
    page=3+2i and content stream=4+2i, finally the shared font object.
    """
    page_count = len(page_texts)
    font_obj_num = 3 + 2 * page_count

    objects: dict[int, bytes] = {}
    objects[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
    kids = " ".join(f"{3 + 2 * i} 0 R" for i in range(page_count))
    objects[2] = f"<< /Type /Pages /Kids [{kids}] /Count {page_count} >>".encode()
    for i, text in enumerate(page_texts):
        objects[3 + 2 * i] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 {font_obj_num} 0 R >> >> "
            f"/Contents {4 + 2 * i} 0 R >>"
        ).encode()
        stream = f"BT /F1 24 Tf 72 700 Td ({_escape_pdf_text(text)}) Tj ET".encode()
        objects[4 + 2 * i] = (
            b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"
        )
    objects[font_obj_num] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"

    out = bytearray(b"%PDF-1.4\n")
    offsets: dict[int, int] = {}
    for obj_num in sorted(objects):
        offsets[obj_num] = len(out)
        out += f"{obj_num} 0 obj\n".encode() + objects[obj_num] + b"\nendobj\n"

    xref_offset = len(out)
    out += b"xref\n" + f"0 {len(objects) + 1}\n".encode() + b"0000000000 65535 f \n"
    for obj_num in sorted(objects):
        out += f"{offsets[obj_num]:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode()
    out += f"startxref\n{xref_offset}\n%%EOF\n".encode()
    return bytes(out)


# ---------------------------------------------------------------------------
# Docling conversion fakes (real Docling classes, no real conversion)
# ---------------------------------------------------------------------------


def _make_source_file(tmp_path: Path, filename: str) -> Path:
    """Create a minimal placeholder file so that _resolve_path() succeeds."""
    source = tmp_path / filename
    source.write_bytes(b"placeholder bytes: content is irrelevant, conversion is mocked")
    return source


def _text_item(ref: str, text: str, page_no: int) -> TextItem:
    """Build a TextItem with a deterministic self_ref and provenance."""
    return TextItem(
        self_ref=ref,
        label=DocItemLabel.TEXT,
        orig=text,
        text=text,
        prov=[
            ProvenanceItem(
                page_no=page_no,
                bbox={"l": 0.0, "t": 0.0, "r": 100.0, "b": 100.0, "coord_origin": "TOPLEFT"},
                charspan=(0, len(text)),
            )
        ],
    )


def _page_item(page_no: int, size: Size | None = None) -> PageItem:
    if size is None:
        size = Size(width=612.0, height=792.0)
    return PageItem(page_no=page_no, size=size)


def _docling_document(
    pages: dict[int, PageItem],
    texts: list[TextItem] | None = None,
    origin: DocumentOrigin | None = None,
) -> DoclingDocument:
    return DoclingDocument(name="mocked-doc", pages=pages, texts=texts or [], origin=origin)


def _conversion_result(
    status: ConversionStatus,
    document: DoclingDocument | None,
    errors: list[ErrorItem] | None = None,
) -> ConversionResult:
    """Build a real ConversionResult envelope without a real InputDocument."""
    return ConversionResult.model_construct(
        status=status,
        document=document,
        errors=[] if errors is None else errors,
    )


@pytest.fixture()
def converter_cls(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Patch DocumentConverter in the production module's namespace."""
    cls_mock = MagicMock(name="DocumentConverter")
    monkeypatch.setattr("app.services.ingestion.DocumentConverter", cls_mock)
    return cls_mock


@pytest.fixture()
def ocr_threshold(monkeypatch: pytest.MonkeyPatch):
    """Setter for the application OCR threshold for the current test."""

    def _set(threshold: int) -> None:
        monkeypatch.setattr(settings, "ocr_min_text_chars", threshold)

    return _set


# ---------------------------------------------------------------------------
# PAL contract fakes (same isolation strategy as tests/services/test_ocr.py)
# ---------------------------------------------------------------------------


class FakeOCRProvider(OCRInterface):
    """Deterministic OCR provider recording every source it is called with.

    When ``error`` is set, ``extract_text`` raises that exception instead of
    returning a result, so tests can verify that the pipeline propagates
    provider failures unchanged.
    """

    provider_name = "fake-ocr"

    def __init__(self, error: Exception | None = None) -> None:
        self.calls: list[str] = []
        self.error = error

    async def health_check(self) -> HealthStatus:
        return HealthStatus(healthy=True, provider=self.provider_name, message="ok")

    async def extract_text(self, source: str) -> OCRResult:
        self.calls.append(source)
        if self.error is not None:
            raise self.error
        return OCRResult(
            text=f"[ocr] {source}",
            provider=self.provider_name,
            metadata={"engine": "fake", "source": source},
        )

    async def extract_text_batch(self, sources: Sequence[str]) -> list[OCRResult]:
        return [await self.extract_text(source) for source in sources]


class FakePageSourceResolver:
    """Deterministic resolver recording every (document_id, page_number)."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, int]] = []

    def __call__(self, document: CanonicalDocument, page: Page) -> str:
        self.calls.append((document.document_id, page.page_number))
        return f"doc://{document.document_id}/page/{page.page_number}"


# ---------------------------------------------------------------------------
# Test 1 — PDF OCR threshold triggers
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_pdf_page_below_threshold_triggers_ocr_and_preserves_enrichment(
    tmp_path: Path,
    converter_cls: MagicMock,
    ocr_threshold,
) -> None:
    ocr_threshold(10)
    source = _make_source_file(tmp_path, "scan.pdf")
    converter_cls.return_value.convert.return_value = _conversion_result(
        ConversionStatus.SUCCESS,
        _docling_document(
            pages={1: _page_item(1)},
            texts=[_text_item("#/texts/0", "short", 1)],
        ),
    )
    provider = FakeOCRProvider()
    resolver = FakePageSourceResolver()

    result = await ingest_and_enrich(
        source, ocr_provider=provider, page_source_resolver=resolver
    )

    # Composition reached the existing OCR enrichment path.
    assert resolver.calls == [("scan", 1)]
    assert provider.calls == ["doc://scan/page/1"]
    # Existing enrichment behavior preserved: text replaced, metadata merged.
    page = result.pages[0]
    assert page.text == "[ocr] doc://scan/page/1"
    assert page.metadata["ocr"]["applied"] is True
    assert page.metadata["ocr"]["provider"] == "fake-ocr"
    # Existing page metadata from ingestion survives the enrichment.
    assert page.metadata["page_size"] == {"width": 612.0, "height": 792.0}
    assert result.document_id == "scan"
    assert result.source == str(source.resolve())


# ---------------------------------------------------------------------------
# Test 2 — PDF page above threshold
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_pdf_page_above_threshold_does_not_invoke_ocr(
    tmp_path: Path,
    converter_cls: MagicMock,
    ocr_threshold,
) -> None:
    ocr_threshold(10)
    source = _make_source_file(tmp_path, "rich.pdf")
    converter_cls.return_value.convert.return_value = _conversion_result(
        ConversionStatus.SUCCESS,
        _docling_document(
            pages={1: _page_item(1)},
            texts=[_text_item("#/texts/0", "a" * 11, 1)],
        ),
    )
    provider = FakeOCRProvider()
    resolver = FakePageSourceResolver()

    result = await ingest_and_enrich(
        source, ocr_provider=provider, page_source_resolver=resolver
    )

    assert provider.calls == []
    assert resolver.calls == []
    assert result.pages[0].text == "a" * 11
    assert "ocr" not in result.pages[0].metadata
    assert result.metadata["conversion_status"] == ConversionStatus.SUCCESS.value


# ---------------------------------------------------------------------------
# Test 3 — Multi-page PDF
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_multipage_pdf_enriches_eligible_pages_in_order(
    tmp_path: Path,
    converter_cls: MagicMock,
    ocr_threshold,
) -> None:
    ocr_threshold(10)
    source = _make_source_file(tmp_path, "lecture.pdf")
    converter_cls.return_value.convert.return_value = _conversion_result(
        ConversionStatus.SUCCESS,
        _docling_document(
            pages={1: _page_item(1), 2: _page_item(2), 3: _page_item(3), 4: _page_item(4)},
            texts=[
                _text_item("#/texts/0", "a" * 11, 1),  # above threshold
                _text_item("#/texts/1", "tiny", 2),  # OCR
                _text_item("#/texts/2", "b" * 3, 3),  # OCR
                _text_item("#/texts/3", "c" * 20, 4),  # above threshold
            ],
        ),
    )
    provider = FakeOCRProvider()
    resolver = FakePageSourceResolver()

    result = await ingest_and_enrich(
        source, ocr_provider=provider, page_source_resolver=resolver
    )

    # Only eligible pages resolved and OCR'd, in page order.
    assert resolver.calls == [("lecture", 2), ("lecture", 3)]
    assert provider.calls == ["doc://lecture/page/2", "doc://lecture/page/3"]
    assert [p.page_number for p in result.pages] == [1, 2, 3, 4]
    assert result.pages[0].text == "a" * 11
    assert result.pages[3].text == "c" * 20
    assert "ocr" not in result.pages[0].metadata
    assert "ocr" not in result.pages[3].metadata
    assert result.pages[1].text == "[ocr] doc://lecture/page/2"
    assert result.pages[2].text == "[ocr] doc://lecture/page/3"
    assert result.pages[1].metadata["ocr"]["source"] == "doc://lecture/page/2"
    assert result.pages[2].metadata["ocr"]["source"] == "doc://lecture/page/3"


# ---------------------------------------------------------------------------
# Test 4 — Non-PDF skip
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_non_pdf_source_skips_ocr_and_records_note(
    tmp_path: Path,
    converter_cls: MagicMock,
    ocr_threshold,
) -> None:
    ocr_threshold(50)
    source = _make_source_file(tmp_path, "notes.md")
    converter_cls.return_value.convert.return_value = _conversion_result(
        ConversionStatus.SUCCESS,
        _docling_document(
            pages={1: _page_item(1)},
            texts=[_text_item("#/texts/0", "hello markdown", 1)],
        ),
    )
    provider = FakeOCRProvider()
    resolver = FakePageSourceResolver()

    result = await ingest_and_enrich(
        source, ocr_provider=provider, page_source_resolver=resolver
    )

    # Neither the resolver nor the provider is ever invoked.
    assert provider.calls == []
    assert resolver.calls == []
    # The B1 (c) skip note is recorded exactly as specified.
    assert result.metadata["ocr"] == {
        "applied": False,
        "skipped": True,
        "reason": "non_pdf_source_not_in_week7_8_ocr_scope",
    }
    # Page content untouched.
    assert result.pages[0].text == "hello markdown"
    assert "ocr" not in result.pages[0].metadata


# ---------------------------------------------------------------------------
# Test 5 — Explicit resolver injection
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_explicit_resolver_is_used_verbatim(
    tmp_path: Path,
    converter_cls: MagicMock,
    ocr_threshold,
) -> None:
    ocr_threshold(10)
    source = _make_source_file(tmp_path, "scan.pdf")
    converter_cls.return_value.convert.return_value = _conversion_result(
        ConversionStatus.SUCCESS,
        _docling_document(
            pages={1: _page_item(1)},
            texts=[_text_item("#/texts/0", "short", 1)],
        ),
    )
    provider = FakeOCRProvider()
    resolver = FakePageSourceResolver()

    result = await ingest_and_enrich(
        source, ocr_provider=provider, page_source_resolver=resolver
    )

    # The injected resolver produced the source handed to the provider.
    assert resolver.calls == [("scan", 1)]
    assert provider.calls == ["doc://scan/page/1"]
    assert result.pages[0].text == "[ocr] doc://scan/page/1"
    # The default PDF resolver was not used: no artifacts next to the source.
    assert [p.name for p in tmp_path.iterdir()] == ["scan.pdf"]


# ---------------------------------------------------------------------------
# Test 6 — PDF default resolver (real single-page artifacts)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_pdf_without_resolver_uses_existing_pdf_resolver(
    tmp_path: Path,
    converter_cls: MagicMock,
    ocr_threshold,
) -> None:
    ocr_threshold(10)
    source = tmp_path / "fixture.pdf"
    source.write_bytes(_build_multipage_pdf(["marker-alpha", "marker-beta"]))
    # Mocked conversion still reports two pages; page 1 is below threshold.
    converter_cls.return_value.convert.return_value = _conversion_result(
        ConversionStatus.SUCCESS,
        _docling_document(
            pages={1: _page_item(1), 2: _page_item(2)},
            texts=[
                _text_item("#/texts/0", "short", 1),
                _text_item("#/texts/1", "a" * 11, 2),
            ],
        ),
    )
    provider = FakeOCRProvider()

    result = await ingest_and_enrich(source, ocr_provider=provider)

    # Page 1 was OCR'd through the real existing PDF resolver; page 2 not.
    assert len(provider.calls) == 1
    artifact = Path(provider.calls[0])
    assert artifact.parent == tmp_path
    assert artifact.name == "fixture-page-0001.pdf"
    assert artifact.exists()
    assert artifact.read_bytes().startswith(b"%PDF-")
    with pdfium.PdfDocument(artifact) as single_page_doc:
        assert len(single_page_doc) == 1
        artifact_text = single_page_doc[0].get_textpage().get_text_range()
    assert "marker-alpha" in artifact_text
    assert result.pages[0].text == f"[ocr] {artifact}"
    assert result.pages[0].metadata["ocr"]["applied"] is True
    assert result.pages[1].text == "a" * 11
    assert "ocr" not in result.pages[1].metadata


# ---------------------------------------------------------------------------
# Test 7 — OCR/provider error propagation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_provider_error_propagates_unchanged(
    tmp_path: Path,
    converter_cls: MagicMock,
    ocr_threshold,
) -> None:
    ocr_threshold(10)
    source = _make_source_file(tmp_path, "scan.pdf")
    converter_cls.return_value.convert.return_value = _conversion_result(
        ConversionStatus.SUCCESS,
        _docling_document(
            pages={1: _page_item(1)},
            texts=[_text_item("#/texts/0", "short", 1)],
        ),
    )
    error = ProviderTimeoutError("gateway timed out")
    provider = FakeOCRProvider(error=error)
    resolver = FakePageSourceResolver()

    with pytest.raises(ProviderTimeoutError) as excinfo:
        await ingest_and_enrich(
            source, ocr_provider=provider, page_source_resolver=resolver
        )

    # The very same exception instance surfaces: not swallowed, not converted.
    assert excinfo.value is error
    # The failure happened inside the composed enrichment, after resolution.
    assert resolver.calls == [("scan", 1)]
    assert provider.calls == ["doc://scan/page/1"]


# ---------------------------------------------------------------------------
# Test 8 — Existing metadata preservation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_existing_document_metadata_survives_non_pdf_skip(
    tmp_path: Path,
    converter_cls: MagicMock,
    ocr_threshold,
) -> None:
    ocr_threshold(50)
    source = _make_source_file(tmp_path, "notes.md")
    origin = DocumentOrigin(
        filename="notes.md",
        mimetype="text/markdown",
        binary_hash=1234567890123456789,
        uri="file:///fixtures/notes.md",
    )
    converter_cls.return_value.convert.return_value = _conversion_result(
        ConversionStatus.SUCCESS,
        _docling_document(
            pages={1: _page_item(1)},
            texts=[_text_item("#/texts/0", "hello markdown", 1)],
            origin=origin,
        ),
    )
    provider = FakeOCRProvider()
    resolver = FakePageSourceResolver()

    result = await ingest_and_enrich(
        source, ocr_provider=provider, page_source_resolver=resolver
    )

    # Every ingestion metadata key survives the skip-note merge...
    assert result.metadata["filename"] == "notes.md"
    assert result.metadata["mimetype"] == "text/markdown"
    assert result.metadata["binary_hash"] == 1234567890123456789
    assert result.metadata["uri"] == "file:///fixtures/notes.md"
    assert result.metadata["conversion_status"] == ConversionStatus.SUCCESS.value
    assert result.metadata["page_count"] == 1
    # ...and only the OCR skip note was added.
    assert result.metadata["ocr"] == {
        "applied": False,
        "skipped": True,
        "reason": "non_pdf_source_not_in_week7_8_ocr_scope",
    }
    assert set(result.metadata) == {
        "filename",
        "mimetype",
        "binary_hash",
        "uri",
        "conversion_status",
        "page_count",
        "ocr",
    }


# ---------------------------------------------------------------------------
# Deterministic artifact handling (roadmap B2: deterministic temp artifacts;
# delete-cleanup itself is the B5 seam's responsibility per decisions.md §5)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_default_resolver_artifacts_are_deterministic(
    tmp_path: Path,
    converter_cls: MagicMock,
    ocr_threshold,
) -> None:
    ocr_threshold(10)
    source = tmp_path / "fixture.pdf"
    source.write_bytes(_build_multipage_pdf(["marker-alpha"]))
    converter_cls.return_value.convert.return_value = _conversion_result(
        ConversionStatus.SUCCESS,
        _docling_document(
            pages={1: _page_item(1)},
            texts=[_text_item("#/texts/0", "short", 1)],
        ),
    )

    first_provider = FakeOCRProvider()
    await ingest_and_enrich(source, ocr_provider=first_provider)
    second_provider = FakeOCRProvider()
    await ingest_and_enrich(source, ocr_provider=second_provider)

    # Same deterministic artifact name on every run, no duplicates.
    assert first_provider.calls == second_provider.calls
    artifact = Path(first_provider.calls[0])
    assert artifact.name == "fixture-page-0001.pdf"
    siblings = [p for p in tmp_path.iterdir() if p.name != "fixture.pdf"]
    assert [p.name for p in siblings] == ["fixture-page-0001.pdf"]
