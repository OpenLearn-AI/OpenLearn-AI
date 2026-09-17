"""Unit tests for the targeted OCR orchestration service (P7.1).

Fully isolated: the OCR provider and the page-source resolver are
deterministic in-process fakes bound to the frozen ``OCRInterface`` contract.
No network, no models, no real OCR. Async tests carry explicit
``@pytest.mark.asyncio`` markers for the repository's strict asyncio mode.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

import pytest

from app.config import settings
from app.documents import CanonicalDocument, Page
from app.pal.interfaces.ocr import OCRInterface
from app.pal.models.types import BoundingBox, HealthStatus, OCRRegion, OCRResult

from app.services.ocr import enrich_document_with_ocr, needs_ocr


class FakeOCRProvider(OCRInterface):
    """Deterministic OCR provider used only for orchestration tests.

    Records every source it is called with and returns a fixed deterministic
    result, so tests can verify exactly which sources reached the provider.
    """

    provider_name = "fake-ocr"

    def __init__(self) -> None:
        self.calls: list[str] = []

    async def health_check(self) -> HealthStatus:
        return HealthStatus(healthy=True, provider=self.provider_name, message="ok")

    async def extract_text(self, source: str) -> OCRResult:
        self.calls.append(source)
        return OCRResult(
            text=f"[ocr] {source}",
            provider=self.provider_name,
            regions=[
                OCRRegion(
                    text=f"[ocr] {source}",
                    bounding_box=BoundingBox(x1=0.0, y1=0.0, x2=100.0, y2=20.0),
                    confidence=0.99,
                ),
            ],
            metadata={"engine": "fake", "source": source},
        )

    async def extract_text_batch(self, sources: Sequence[str]) -> list[OCRResult]:
        return [await self.extract_text(source) for source in sources]


class FakePageSourceResolver:
    """Deterministic resolver producing a stable per-page source reference.

    Records every (document_id, page_number) it is invoked with so tests can
    verify that only eligible pages are resolved, exactly once each.
    """

    def __init__(self) -> None:
        self.calls: list[tuple[str, int]] = []

    def __call__(self, document: CanonicalDocument, page: Page) -> str:
        self.calls.append((document.document_id, page.page_number))
        return f"doc://{document.document_id}/page/{page.page_number}"


@pytest.fixture()
def ocr_threshold(monkeypatch: pytest.MonkeyPatch) -> Callable[[int], None]:
    """Setter for the application OCR threshold for the current test."""

    def _set(threshold: int) -> None:
        monkeypatch.setattr(settings, "ocr_min_text_chars", threshold)

    return _set


# ---------------------------------------------------------------------------
# needs_ocr quality gate
# ---------------------------------------------------------------------------


def test_empty_text_requires_ocr(ocr_threshold: Callable[[int], None]) -> None:
    ocr_threshold(50)
    assert needs_ocr("") is True


def test_text_below_threshold_requires_ocr(ocr_threshold: Callable[[int], None]) -> None:
    ocr_threshold(10)
    assert needs_ocr("a" * 9) is True


def test_text_exactly_at_threshold_does_not_require_ocr(
    ocr_threshold: Callable[[int], None],
) -> None:
    ocr_threshold(10)
    assert needs_ocr("a" * 10) is False


def test_text_above_threshold_does_not_require_ocr(
    ocr_threshold: Callable[[int], None],
) -> None:
    ocr_threshold(10)
    assert needs_ocr("a" * 11) is False


def test_threshold_defaults_to_configured_settings_value() -> None:
    # Gate must read settings.ocr_min_text_chars (default 50), not a literal.
    assert settings.ocr_min_text_chars == 50
    assert needs_ocr("a" * 49) is True
    assert needs_ocr("a" * 50) is False


# ---------------------------------------------------------------------------
# Document enrichment
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_page_with_sufficient_text_does_not_invoke_resolver_or_provider(
    ocr_threshold: Callable[[int], None],
) -> None:
    ocr_threshold(10)
    provider = FakeOCRProvider()
    resolver = FakePageSourceResolver()
    page = Page(page_number=1, text="a" * 10, metadata={"page_size": {"width": 612.0}})
    document = CanonicalDocument(document_id="doc", source="/docs/doc.pdf", pages=[page])

    result = await enrich_document_with_ocr(document, provider, resolver)

    assert result is document
    assert resolver.calls == []
    assert provider.calls == []
    assert page.text == "a" * 10
    assert page.metadata == {"page_size": {"width": 612.0}}


@pytest.mark.asyncio
async def test_eligible_page_resolves_source_once_and_passes_it_to_provider(
    ocr_threshold: Callable[[int], None],
) -> None:
    ocr_threshold(10)
    provider = FakeOCRProvider()
    resolver = FakePageSourceResolver()
    page = Page(page_number=1, text="short")
    document = CanonicalDocument(document_id="doc", source="/docs/doc.pdf", pages=[page])

    await enrich_document_with_ocr(document, provider, resolver)

    assert resolver.calls == [("doc", 1)]
    assert provider.calls == ["doc://doc/page/1"]
    assert page.text == "[ocr] doc://doc/page/1"


@pytest.mark.asyncio
async def test_ocr_enrichment_preserves_existing_metadata_and_attaches_ocr_metadata(
    ocr_threshold: Callable[[int], None],
) -> None:
    ocr_threshold(5)
    provider = FakeOCRProvider()
    resolver = FakePageSourceResolver()
    page = Page(
        page_number=2,
        text="tiny",
        metadata={"page_size": {"width": 612.0, "height": 792.0}, "origin": "docling"},
    )
    document = CanonicalDocument(document_id="doc", source="/docs/doc.pdf", pages=[page])

    await enrich_document_with_ocr(document, provider, resolver)

    # Existing metadata preserved verbatim.
    assert page.metadata["page_size"] == {"width": 612.0, "height": 792.0}
    assert page.metadata["origin"] == "docling"

    ocr_meta = page.metadata["ocr"]
    assert isinstance(ocr_meta, dict)
    assert ocr_meta["applied"] is True
    assert ocr_meta["provider"] == "fake-ocr"
    assert ocr_meta["source"] == "doc://doc/page/2"
    regions = ocr_meta["regions"]
    assert isinstance(regions, list) and len(regions) == 1
    assert regions[0]["text"] == "[ocr] doc://doc/page/2"
    assert regions[0]["confidence"] == 0.99
    assert regions[0]["bounding_box"] == {"x1": 0.0, "y1": 0.0, "x2": 100.0, "y2": 20.0}
    assert ocr_meta["provider_metadata"] == {"engine": "fake", "source": "doc://doc/page/2"}


@pytest.mark.asyncio
async def test_only_eligible_pages_resolve_and_invoke_provider_in_page_order(
    ocr_threshold: Callable[[int], None],
) -> None:
    ocr_threshold(10)
    provider = FakeOCRProvider()
    resolver = FakePageSourceResolver()
    pages = [
        Page(page_number=1, text="a" * 10),  # exactly at threshold -> no OCR
        Page(page_number=2, text="a" * 3),   # below threshold -> OCR
        Page(page_number=3, text="a" * 20),  # above threshold -> no OCR
        Page(page_number=4, text="a"),       # below threshold -> OCR
    ]
    document = CanonicalDocument(document_id="doc", source="/docs/doc.pdf", pages=pages)

    await enrich_document_with_ocr(document, provider, resolver)

    assert resolver.calls == [("doc", 2), ("doc", 4)]
    assert provider.calls == ["doc://doc/page/2", "doc://doc/page/4"]
    assert pages[0].text == "a" * 10
    assert pages[2].text == "a" * 20
    assert "ocr" not in pages[0].metadata
    assert "ocr" not in pages[2].metadata
    assert pages[1].text == "[ocr] doc://doc/page/2"
    assert pages[3].text == "[ocr] doc://doc/page/4"
    assert pages[1].metadata["ocr"]["source"] == "doc://doc/page/2"
    assert pages[3].metadata["ocr"]["source"] == "doc://doc/page/4"


@pytest.mark.asyncio
async def test_document_structure_and_page_numbers_unchanged(
    ocr_threshold: Callable[[int], None],
) -> None:
    ocr_threshold(10)
    provider = FakeOCRProvider()
    resolver = FakePageSourceResolver()
    pages = [Page(page_number=1, text="a" * 2), Page(page_number=2, text="b" * 20)]
    document = CanonicalDocument(
        document_id="doc-1", source="/docs/doc.pdf", title="Doc", pages=pages
    )

    result = await enrich_document_with_ocr(document, provider, resolver)

    assert result is document
    assert len(result.pages) == 2
    assert [p.page_number for p in result.pages] == [1, 2]
    assert result.document_id == "doc-1"
    assert result.source == "/docs/doc.pdf"
    assert result.title == "Doc"


@pytest.mark.asyncio
async def test_document_without_pages_does_not_invoke_resolver_or_provider(
    ocr_threshold: Callable[[int], None],
) -> None:
    ocr_threshold(10)
    provider = FakeOCRProvider()
    resolver = FakePageSourceResolver()
    document = CanonicalDocument(document_id="empty", source="/docs/empty.pdf")

    result = await enrich_document_with_ocr(document, provider, resolver)

    assert resolver.calls == []
    assert provider.calls == []
    assert result.pages == []
