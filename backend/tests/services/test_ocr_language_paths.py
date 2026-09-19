"""Week 6 OCR-closure tests: Arabic behavior of the targeted OCR layer.

The quality gate counts characters (language-agnostic by design) and the
enrichment pipeline moves provider text into Page.text/metadata verbatim —
these tests pin both behaviors for Arabic strings, which the original Week 6
requirement calls out explicitly.
"""

from __future__ import annotations

import pytest

from app.config import settings
from app.documents import CanonicalDocument, Page
from app.pal.interfaces.ocr import OCRInterface
from app.pal.models.types import HealthStatus, OCRResult
from app.services.ocr import enrich_document_with_ocr, needs_ocr

_ARABIC_TEXT = "هذا نص عربي تجريبي لاختبار مسار OCR"


class _StubArabicOCR(OCRInterface):
    """Deterministic provider returning a fixed Arabic extraction."""

    provider_name = "stub"

    async def health_check(self) -> HealthStatus:
        return HealthStatus(healthy=True, provider=self.provider_name)

    async def extract_text(self, source: str) -> OCRResult:
        return OCRResult(
            text=_ARABIC_TEXT,
            provider=self.provider_name,
            metadata={"model": "stub-model"},
        )

    async def extract_text_batch(self, sources: list[str]) -> list[OCRResult]:
        return [await self.extract_text(source) for source in sources]


def test_needs_ocr_threshold_counts_arabic_characters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "ocr_min_text_chars", 10)
    assert needs_ocr("أ" * 9) is True    # below threshold -> OCR
    assert needs_ocr("أ" * 10) is False  # exact threshold -> no OCR


@pytest.mark.asyncio
async def test_arabic_page_is_enriched_with_normalized_text_and_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "ocr_min_text_chars", 10)
    document = CanonicalDocument(
        document_id="doc-ar",
        source="/docs/doc-ar.pdf",
        pages=[Page(page_number=1, text="قصير")],  # eligible: below threshold
    )
    resolved_pages: list[int] = []

    def resolver(doc: CanonicalDocument, page: Page) -> str:
        resolved_pages.append(page.page_number)
        return f"doc://{doc.document_id}/page/{page.page_number}"

    result = await enrich_document_with_ocr(document, _StubArabicOCR(), resolver)

    assert resolved_pages == [1]  # resolver invoked exactly once
    assert result.pages[0].text == _ARABIC_TEXT  # Arabic replaces page text

    ocr_meta = result.pages[0].metadata["ocr"]
    assert isinstance(ocr_meta, dict)
    assert ocr_meta["applied"] is True
    assert ocr_meta["provider"] == "stub"
    assert ocr_meta["source"] == "doc://doc-ar/page/1"
    assert ocr_meta["provider_metadata"] == {"model": "stub-model"}
