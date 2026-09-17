"""Single-page PDF artifact extraction for targeted OCR (P7.2-A).

Application/service-layer PDF handling per ADR-0009. This module produces the
real OCR source artifact that P7.1's injected ``PageSourceResolver`` hands to
an ``OCRInterface`` provider: a standalone, real (vector/text-preserving) PDF
containing exactly one page of the source document.

It deliberately knows nothing about OCR providers, rendering-to-image,
Gemini, or RAG logic. Uses the installed ``pypdfium2`` (already present as a
Docling dependency); no shell-outs, no external binaries.
"""

from __future__ import annotations

from pathlib import Path

import pypdfium2 as pdfium

from app.documents import CanonicalDocument, Page
from app.documents.exceptions import (
    DocumentNotFoundError,
    PageExtractionError,
    UnsupportedDocumentTypeError,
)
from app.services.ocr import PageSourceResolver


def create_single_page_pdf(
    source_pdf: str | Path,
    page_number: int,
    output_dir: str | Path | None = None,
) -> Path:
    """Extract exactly one page (1-based) of ``source_pdf`` into a new PDF.

    The artifact is named ``{source_stem}-page-{page_number:04d}.pdf`` and is
    written to ``output_dir`` (created if necessary; defaults to the source
    file's directory). Existing artifacts with the same name are overwritten,
    so the operation is deterministic and idempotent. The original PDF is
    never modified, and every opened PDFium document is closed.

    Returns the path to the generated artifact, which is re-opened and
    verified (readable, exactly one page) before being returned.

    Errors:
        DocumentNotFoundError         source missing or not a regular file
        UnsupportedDocumentTypeError  source does not have a .pdf extension
        ValueError                    page_number < 1 (bad argument)
        PageExtractionError           unreadable/malformed PDF, page beyond
                                      the page count, or write/verify failure
    """
    source_path = Path(source_pdf)

    if not source_path.exists() or not source_path.is_file():
        raise DocumentNotFoundError(f"Source PDF not found or not a file: {source_pdf}")

    if source_path.suffix.lower() != ".pdf":
        raise UnsupportedDocumentTypeError(
            f"OCR page extraction requires a PDF file; got extension "
            f"'{source_path.suffix or '<none>'}' for {source_path}"
        )

    if page_number < 1:
        raise ValueError(
            f"page_number must be >= 1 (1-based PDF page number), got {page_number}"
        )

    output_directory = Path(output_dir) if output_dir is not None else source_path.parent
    zero_based_index = page_number - 1

    try:
        source_doc = pdfium.PdfDocument(source_path)
    except pdfium.PdfiumError as exc:
        raise PageExtractionError(f"Source is not a readable PDF: {source_path}") from exc

    artifact_path = output_directory / f"{source_path.stem}-page-{page_number:04d}.pdf"

    try:
        page_count = len(source_doc)
        if zero_based_index >= page_count:
            raise PageExtractionError(
                f"Cannot extract page {page_number}: "
                f"'{source_path.name}' has only {page_count} page(s)."
            )

        output_directory.mkdir(parents=True, exist_ok=True)

        artifact_doc = pdfium.PdfDocument.new()
        try:
            # Copies the real page object (text/vector/resources) into the
            # new document — not an image renamed to .pdf.
            artifact_doc.import_pages(source_doc, [zero_based_index])
            artifact_doc.save(artifact_path)
        except pdfium.PdfiumError as exc:
            raise PageExtractionError(
                f"Failed to write single-page artifact '{artifact_path.name}' "
                f"for page {page_number} of '{source_path.name}'"
            ) from exc
        finally:
            artifact_doc.close()
    finally:
        source_doc.close()

    # The artifact must be readable immediately and contain exactly one page.
    try:
        with pdfium.PdfDocument(artifact_path) as verification_doc:
            if len(verification_doc) != 1:
                raise PageExtractionError(
                    f"Generated artifact does not contain exactly one page: {artifact_path}"
                )
    except pdfium.PdfiumError as exc:
        raise PageExtractionError(
            f"Generated artifact failed verification as a readable PDF: {artifact_path}"
        ) from exc

    return artifact_path


def pdf_page_source_resolver(
    output_dir: str | Path | None = None,
) -> PageSourceResolver:
    """Build a P7.1 ``PageSourceResolver`` backed by real PDF page extraction.

    The returned callable maps ``(document, page)`` to the filesystem path of
    a freshly created single-page PDF artifact for ``page.page_number`` of
    ``document.source``. It performs no OCR, imports no provider SDK, and
    contains no business logic.
    """

    def resolve(document: CanonicalDocument, page: Page) -> str:
        artifact_path = create_single_page_pdf(
            document.source,
            page.page_number,
            output_dir,
        )
        return str(artifact_path)

    return resolve
