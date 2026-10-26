"""P7.2-A tests: single-page PDF artifact extraction and resolver.

Exercises the real installed PDF library (pypdfium2) end-to-end: fixtures are
genuine deterministic multi-page PDFs built as raw bytes, and extraction
results are verified by re-parsing artifacts. No mocks of the PDF layer, no
network, no OCR providers.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from pathlib import Path

import pypdfium2 as pdfium
import pytest

from app.config import settings
from app.documents import CanonicalDocument, DocumentNotFoundError, Page
from app.documents.exceptions import PageExtractionError, UnsupportedDocumentTypeError
from app.pal.interfaces.ocr import OCRInterface
from app.pal.models.types import HealthStatus, OCRResult
from app.services.ocr import enrich_document_with_ocr
from app.services.ocr_source import create_single_page_pdf, pdf_page_source_resolver

PAGE_MARKERS = ["marker-alpha", "marker-beta", "marker-gamma"]


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


@pytest.fixture()
def multipage_pdf(tmp_path: Path) -> Path:
    pdf_path = tmp_path / "fixture.pdf"
    pdf_path.write_bytes(_build_multipage_pdf(PAGE_MARKERS))
    return pdf_path


# ---------------------------------------------------------------------------
# Verification helpers (real library, no mocks)
# ---------------------------------------------------------------------------


def _pdf_page_count(path: Path) -> int:
    with pdfium.PdfDocument(path) as doc:
        return len(doc)


def _pdf_page_text(path: Path, page_index: int = 0) -> str:
    with pdfium.PdfDocument(path) as doc:
        return doc[page_index].get_textpage().get_text_range()


# ---------------------------------------------------------------------------
# Core extraction (real PDF in, real PDF out)
# ---------------------------------------------------------------------------


def test_extract_page_one_produces_readable_valid_pdf(
    multipage_pdf: Path, tmp_path: Path
) -> None:
    artifact = create_single_page_pdf(multipage_pdf, 1, tmp_path / "artifacts")

    assert artifact.exists()
    assert artifact.read_bytes().startswith(b"%PDF-")  # real PDF container
    with pdfium.PdfDocument(artifact) as doc:          # readable == parses
        assert len(doc) == 1
    assert "marker-alpha" in _pdf_page_text(artifact)


def test_extract_page_two_returns_requested_page(
    multipage_pdf: Path, tmp_path: Path
) -> None:
    artifact = create_single_page_pdf(multipage_pdf, 2, tmp_path / "artifacts")

    text = _pdf_page_text(artifact)
    assert "marker-beta" in text
    assert "marker-alpha" not in text  # not just page 1 every time
    assert "marker-gamma" not in text


def test_every_extracted_artifact_contains_exactly_one_page(
    multipage_pdf: Path, tmp_path: Path
) -> None:
    for requested in (1, 2, 3):
        artifact = create_single_page_pdf(multipage_pdf, requested, tmp_path / f"out{requested}")
        assert _pdf_page_count(artifact) == 1


# ---------------------------------------------------------------------------
# Invalid inputs
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad_page", [0, -1])
def test_invalid_page_number_below_one_rejected(multipage_pdf: Path, bad_page: int) -> None:
    with pytest.raises(ValueError, match="page_number"):
        create_single_page_pdf(multipage_pdf, bad_page)


def test_page_number_beyond_page_count_rejected(multipage_pdf: Path) -> None:
    with pytest.raises(PageExtractionError, match=r"has only 3 page"):
        create_single_page_pdf(multipage_pdf, 4)


def test_missing_source_fails_with_document_not_found(tmp_path: Path) -> None:
    with pytest.raises(DocumentNotFoundError, match="missing.pdf"):
        create_single_page_pdf(tmp_path / "missing.pdf", 1)


def test_directory_source_fails_with_document_not_found(tmp_path: Path) -> None:
    with pytest.raises(DocumentNotFoundError, match="not found or not a file"):
        create_single_page_pdf(tmp_path, 1)


def test_non_pdf_extension_rejected(tmp_path: Path) -> None:
    text_file = tmp_path / "notes.txt"
    text_file.write_text("just text", encoding="utf-8")
    with pytest.raises(UnsupportedDocumentTypeError, match="requires a PDF file"):
        create_single_page_pdf(text_file, 1)


def test_pdf_extension_with_non_pdf_content_rejected(tmp_path: Path) -> None:
    fake = tmp_path / "fake.pdf"
    fake.write_text("this is definitely not a pdf document", encoding="utf-8")
    with pytest.raises(PageExtractionError, match="not a readable PDF"):
        create_single_page_pdf(fake, 1)


# ---------------------------------------------------------------------------
# Preservation and output handling
# ---------------------------------------------------------------------------


def test_original_pdf_is_not_modified(multipage_pdf: Path) -> None:
    digest_before = hashlib.sha256(multipage_pdf.read_bytes()).hexdigest()

    create_single_page_pdf(multipage_pdf, 3)

    digest_after = hashlib.sha256(multipage_pdf.read_bytes()).hexdigest()
    assert digest_before == digest_after
    with pdfium.PdfDocument(multipage_pdf) as doc:
        assert len(doc) == 3  # original still intact


def test_output_dir_is_created_and_artifact_written_there(
    multipage_pdf: Path, tmp_path: Path
) -> None:
    output_dir = tmp_path / "generated" / "nested"

    artifact = create_single_page_pdf(multipage_pdf, 2, output_dir)

    assert output_dir.is_dir()
    assert artifact == output_dir / "fixture-page-0002.pdf"  # deterministic name
    assert artifact.is_file()
    assert _pdf_page_count(artifact) == 1
    assert "marker-beta" in _pdf_page_text(artifact)


# ---------------------------------------------------------------------------
# Resolver behavior
# ---------------------------------------------------------------------------


def test_resolver_returns_artifact_path_for_requested_page(
    multipage_pdf: Path, tmp_path: Path
) -> None:
    document = CanonicalDocument(document_id="doc", source=str(multipage_pdf))
    page = Page(page_number=2, text="tiny")
    resolver = pdf_page_source_resolver(output_dir=tmp_path / "generated")

    source = resolver(document, page)

    artifact = Path(source)
    assert artifact.exists()
    assert artifact.parent == tmp_path / "generated"
    assert _pdf_page_count(artifact) == 1
    assert "marker-beta" in _pdf_page_text(artifact)


class RecordingFakeOCRProvider(OCRInterface):
    """Minimal deterministic provider recording the sources it receives."""

    provider_name = "fake-ocr"

    def __init__(self) -> None:
        self.sources: list[str] = []

    async def health_check(self) -> HealthStatus:
        return HealthStatus(healthy=True, provider=self.provider_name)

    async def extract_text(self, source: str) -> OCRResult:
        self.sources.append(source)
        return OCRResult(text=f"ocr:{source}", provider=self.provider_name)

    async def extract_text_batch(self, sources: Sequence[str]) -> list[OCRResult]:
        return [await self.extract_text(source) for source in sources]


@pytest.mark.asyncio
async def test_resolver_plugs_into_p71_ocr_enrichment(
    multipage_pdf: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "ocr_min_text_chars", 100)
    document = CanonicalDocument(
        document_id="fixture",
        source=str(multipage_pdf),
        pages=[
            Page(page_number=1, text="a" * 150),  # >= threshold: untouched
            Page(page_number=2, text="tiny"),     # < threshold: OCR via artifact
        ],
    )
    provider = RecordingFakeOCRProvider()
    resolver = pdf_page_source_resolver()

    result = await enrich_document_with_ocr(document, provider, resolver)

    expected_artifact = multipage_pdf.parent / "fixture-page-0002.pdf"
    # The provider received exactly the real artifact path — never page text.
    assert provider.sources == [str(expected_artifact)]
    assert result.pages[0].text == "a" * 150
    assert result.pages[1].text == f"ocr:{expected_artifact}"
    assert "ocr" in result.pages[1].metadata
    assert expected_artifact.exists()
    with pdfium.PdfDocument(expected_artifact) as artifact_doc:
        assert len(artifact_doc) == 1
    assert "marker-beta" in _pdf_page_text(expected_artifact)
