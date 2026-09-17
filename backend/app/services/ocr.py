"""Targeted OCR orchestration for ingested documents (P7.1).

This module owns the *decision* of which pages need OCR and the *enrichment*
of a :class:`CanonicalDocument` through an injected PAL ``OCRInterface``
provider. Per ADR-0009:

* the quality gate is deliberately simple and deterministic (text length);
* providers are always injected by the caller, never constructed here;
* the OCR source for an eligible page is obtained through an injected
  ``PageSourceResolver`` — this layer never passes ``Page.text`` to the
  provider and never produces page artifacts itself (rendering/splitting is
  P7.2);
* no provider SDK (Gemini, PaddleOCR, Tesseract, ...) is imported here.
"""

from __future__ import annotations

from collections.abc import Callable

from app.config import settings
from app.documents import CanonicalDocument, Page
from app.pal.interfaces.ocr import OCRInterface
from app.pal.models.types import OCRResult

#: Application-level dependency that maps an eligible page to the OCR-able
#: source artifact string handed to ``OCRInterface.extract_text`` (e.g. a
#: page-image or page-slice reference once P7.2 provides real rendering).
#: The orchestration layer only knows this contract, never how sources are
#: produced.
PageSourceResolver = Callable[[CanonicalDocument, Page], str]

_OCR_METADATA_KEY = "ocr"


def needs_ocr(page_text: str) -> bool:
    """Return True when a page's extracted text is too short to trust.

    Deterministic length gate driven by ``settings.ocr_min_text_chars``:
    OCR is required when ``len(page_text) < ocr_min_text_chars``. A page with
    exactly the threshold number of characters is NOT sent to OCR.

    Known ADR-0009 limitation (accepted): garbage text layers at or above the
    threshold bypass OCR — no content-quality classification is performed.
    """
    return len(page_text) < settings.ocr_min_text_chars


def _ocr_metadata(result: OCRResult, source: str) -> dict[str, object]:
    """Build the page-level OCR metadata payload from a provider result."""
    payload: dict[str, object] = {
        "applied": True,
        "provider": result.provider,
        "source": source,
    }
    if result.regions:
        payload["regions"] = [region.model_dump(mode="json") for region in result.regions]
    if result.metadata:
        payload["provider_metadata"] = result.metadata
    return payload


async def enrich_document_with_ocr(
    document: CanonicalDocument,
    ocr_provider: OCRInterface,
    page_source_resolver: PageSourceResolver,
) -> CanonicalDocument:
    """Enrich the pages of ``document`` that need OCR via ``ocr_provider``.

    * Pages passing the quality gate are left completely untouched (text and
      metadata); neither the resolver nor the provider is invoked for them.
    * For each eligible page, ``page_source_resolver(document, page)`` is
      called exactly once to obtain the OCR source artifact, which is passed
      verbatim to ``ocr_provider.extract_text``. ``OCRResult.text`` replaces
      the page text, all existing metadata is kept, and an ``ocr`` entry is
      merged into ``Page.metadata`` (no schema changes).

    The provider and the resolver are injected; this service never
    instantiates a concrete provider and never produces page artifacts.
    Pages are processed sequentially, so resolver/provider call order and the
    page-to-source mapping are deterministic.
    """
    for page in document.pages:
        if not needs_ocr(page.text):
            continue
        source = page_source_resolver(document, page)
        result = await ocr_provider.extract_text(source)
        page.text = result.text
        page.metadata = {**page.metadata, _OCR_METADATA_KEY: _ocr_metadata(result, source)}
    return document
