"""Stage-1 document pipeline composition (AI Week 7–8, batch B2).

Composes the existing, independently tested application services into the
Stage-1 boundary fixed by the approved B1 decisions
(``docs/tasks/ai-week7-8/decisions.md`` §2.1 and §4):

.. code-block:: text

    local source path
        →  ingest_document()             (Docling extraction; synchronous)
        →  targeted OCR enrichment       (async; PDF-only per B1 decision (c))
        →  enriched CanonicalDocument

This module is composition only, per ADR-0009 and ADR-0001:

* it duplicates no ingestion/OCR logic — the existing services remain the
  sole authority for extraction, the OCR quality gate
  (``settings.ocr_min_text_chars``), OCR text replacement, OCR metadata, and
  page-artifact rendering;
* it adds no pipeline class, registry, stage framework, plugin machinery, or
  retry/fallback policy — provider errors propagate unchanged (the PAL layer
  owns error normalization, the router owns provider fallback, and the Celery
  layer owns task retry/routes);
* it imports no provider SDK — providers and the page-source resolver are
  injected (TS §7.3); the only PAL import is the ``OCRInterface`` contract;
* ``ingest_document()`` is called synchronously and directly: the future
  caller (B5) invokes this async stage from the Celery task's existing
  task-local event loop, where a CPU-bound blocking call delays nothing else
  (B1 decision (a) sync/async boundary);
* it does not touch the Celery task, the material lifecycle, storage, or any
  provider implementation (B5 wires the seam).

PDF detection follows the exact suffix rule the PDF OCR components already
enforce (``.pdf``, case-insensitive), so behavior can never disagree between
layers. Non-PDF sources are outside the Week 7–8 targeted-OCR scope: they
skip OCR gracefully — no resolver call, no provider call, no error — and
record the document-level metadata note defined by B1 decision (c).
"""

from __future__ import annotations

from pathlib import Path

from app.documents import CanonicalDocument
from app.pal.interfaces.ocr import OCRInterface
from app.services.ingestion import ingest_document
from app.services.ocr import PageSourceResolver, enrich_document_with_ocr
from app.services.ocr_source import pdf_page_source_resolver

#: Document-level metadata key for the Stage-1 OCR disposition. The page-level
#: OCR enrichment uses the same key on ``Page.metadata``; this module records
#: the skip disposition for non-PDF sources at the document level only.
_OCR_METADATA_KEY = "ocr"

#: Document-level note recorded for sources outside the Week 7–8 targeted-OCR
#: scope (B1 decision (c), decisions.md §4). Copied per document so the note
#: dict is never shared or mutated across calls.
_OCR_SKIP_NOTE: dict[str, object] = {
    "applied": False,
    "skipped": True,
    "reason": "non_pdf_source_not_in_week7_8_ocr_scope",
}


def _is_pdf_source(source_path: str | Path) -> bool:
    """Return True when ``source_path`` has the ``.pdf`` suffix.

    Same rule as ``create_single_page_pdf`` and the Gemini provider enforce,
    per decisions.md §4 — suffix of the local path only; no MIME sniffing and
    no content inspection.
    """
    return Path(source_path).suffix.lower() == ".pdf"


async def ingest_and_enrich(
    source_path: str | Path,
    *,
    ocr_provider: OCRInterface,
    page_source_resolver: PageSourceResolver | None = None,
) -> CanonicalDocument:
    """Ingest a local document and apply Week 7–8 targeted-OCR enrichment.

    Behavior:

    * Ingestion always runs first via the existing synchronous
      :func:`app.services.ingestion.ingest_document`; its typed errors
      (``DocumentNotFoundError``, ``UnsupportedDocumentTypeError``,
      ``DocumentConversionError``) propagate unchanged.
    * PDF sources (``.pdf`` suffix): OCR enrichment runs through the existing
      :func:`app.services.ocr.enrich_document_with_ocr` — only pages below
      ``settings.ocr_min_text_chars`` are processed, each eligible page's
      source artifact is obtained from the resolver and passed verbatim to
      ``ocr_provider.extract_text``, and the OCR result replaces the page
      text with the ``ocr`` metadata merged (existing service contract).
      When ``page_source_resolver`` is ``None``, the existing
      :func:`app.services.ocr_source.pdf_page_source_resolver` is used;
      its single-page artifacts are written deterministically next to the
      source file (cleanup of the caller's task-local temporary directory
      is the B5 seam's responsibility per decisions.md §5).
    * Non-PDF sources: the provider and resolver are never invoked and no
      error is raised; the document is returned with the B1 (c) skip note
      merged into ``document.metadata["ocr"]`` — every pre-existing
      metadata key is preserved.

    All exceptions raised by the OCR provider propagate unchanged: this
    stage implements no retry, fallback, or error conversion.
    """
    # Step 1 — ingestion: the existing Docling service, unchanged and
    # called synchronously (B1 (a) sync/async boundary).
    document = ingest_document(source_path)

    # Step 2 — Week 7–8 targeted OCR is PDF-only (B1 decision (c)).
    if not _is_pdf_source(source_path):
        document.metadata = {
            **document.metadata,
            _OCR_METADATA_KEY: dict(_OCR_SKIP_NOTE),
        }
        return document

    # Step 3 — PDF path: default to the existing PDF page-source resolver;
    # an explicitly injected resolver is used verbatim.
    resolver = (
        page_source_resolver
        if page_source_resolver is not None
        else pdf_page_source_resolver()
    )
    return await enrich_document_with_ocr(document, ocr_provider, resolver)
