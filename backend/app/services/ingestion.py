from __future__ import annotations

from pathlib import Path
from typing import Any

from docling.exceptions import ConversionError as DoclingConversionError
from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.document import ConversionResult as DoclingConversionResult
from docling.document_converter import DocumentConverter
from docling_core.types.doc.document import DoclingDocument

from app.documents import CanonicalDocument, DocumentConversionError, DocumentNotFoundError, Page
from app.documents.exceptions import UnsupportedDocumentTypeError

# Supported formats confirmed by installed Docling 2.127.0 environment
# and needed for local ingestion: PDF, DOCX, HTML, MD, and images.
_SUPPORTED_FORMATS = {
    InputFormat.PDF,
    InputFormat.DOCX,
    InputFormat.HTML,
    InputFormat.MD,
    InputFormat.IMAGE,
}


def _resolve_path(source: str | Path) -> Path:
    path = Path(source).resolve()
    if not path.exists() or not path.is_file():
        raise DocumentNotFoundError(f"Source not found or not a file: {source}")
    return path


def _detect_format(path: Path) -> InputFormat:
    suffix = path.suffix.lower()
    mapping = {
        ".pdf": InputFormat.PDF,
        ".docx": InputFormat.DOCX,
        ".doc": InputFormat.DOC,
        ".html": InputFormat.HTML,
        ".htm": InputFormat.HTML,
        ".mhtml": InputFormat.MHTML,
        ".md": InputFormat.MD,
        ".png": InputFormat.IMAGE,
        ".jpg": InputFormat.IMAGE,
        ".jpeg": InputFormat.IMAGE,
        ".tiff": InputFormat.IMAGE,
        ".tif": InputFormat.IMAGE,
        ".bmp": InputFormat.IMAGE,
        ".gif": InputFormat.IMAGE,
    }
    if suffix in mapping:
        fmt = mapping[suffix]
        if fmt in _SUPPORTED_FORMATS:
            return fmt
        else:
            # Supported by Docling but not in our minimal local set for this step
            raise UnsupportedDocumentTypeError(
                f"Document format '{fmt.value}' is supported by Docling but not enabled for ingestion at this step."
            )
    # Unknown suffix: try PDF as most common fallback, else unsupported
    if suffix == ".pdf":
        return InputFormat.PDF
    raise UnsupportedDocumentTypeError(
        f"Unsupported document extension '{suffix}' for ingestion."
    )


def _normalize_document(
    result: DoclingConversionResult,
    source_path: Path,
) -> CanonicalDocument:
    doc: DoclingDocument = result.document  # Pydantic BaseModel, not a dict

    # Build page -> ordered text chunks mapping once (preserve doc.texts order)
    page_texts_map: dict[int, list[str]] = {}
    for item in doc.texts or []:
        if item.prov:
            for prov in item.prov:
                if hasattr(item, "text"):
                    page_texts_map.setdefault(prov.page_no, []).append(item.text or "")

    pages: list[Page] = []

    # Iterate pages deterministically by page number
    if doc.pages:
        for page_no in sorted(doc.pages.keys()):
            page_ref = doc.pages[page_no]
            text_parts = page_texts_map.get(int(page_no), [])
            page_text = "\n".join(text_parts) if text_parts else ""
            # Preserve empty pages explicitly (already handled when text_parts is empty)
            pages.append(
                Page(
                    page_number=int(page_no),
                    text=page_text,
                    metadata={
                        "page_size": {
                            "width": float(page_ref.size.width) if hasattr(page_ref.size, "width") else None,
                            "height": float(page_ref.size.height) if hasattr(page_ref.size, "height") else None,
                        } if page_ref.size else {},
                    },
                )
            )

    # Derive document_id from source path stem (deterministic)
    document_id = source_path.stem

    # Source-level metadata (JSON-serializable only)
    meta: dict[str, Any] = {}
    if doc.origin:
        meta["filename"] = doc.origin.filename
        meta["mimetype"] = doc.origin.mimetype
        meta["binary_hash"] = int(doc.origin.binary_hash) if doc.origin.binary_hash is not None else None
        meta["uri"] = str(doc.origin.uri) if doc.origin.uri is not None else None

    meta["conversion_status"] = result.status.value if hasattr(result.status, "value") else str(result.status)
    meta["page_count"] = len(pages)

    # Include errors for PARTIAL_SUCCESS
    if result.has_errors() and result.errors:
        meta["conversion_errors"] = [
            {
                "component_type": str(e.component_type) if hasattr(e, "component_type") else None,
                "module_name": e.module_name,
                "message": e.error_message,
                "page_no": e.page_no,
            }
            for e in result.errors
        ]

    # Title from source filename/stem, not invented
    title = source_path.stem

    return CanonicalDocument(
        document_id=document_id,
        source=str(source_path.resolve()),
        title=title,
        language=None,
        pages=pages,
        metadata=meta,
    )


def ingest_document(source: str | Path) -> CanonicalDocument:
    """Ingest a local document via Docling and return an application CanonicalDocument."""
    source_path = _resolve_path(source)

    fmt = _detect_format(source_path)

    converter = DocumentConverter(allowed_formats=[fmt])
    try:
        result = converter.convert(
            source_path,
            raises_on_error=True,
        )
    except DoclingConversionError as exc:
        raise DocumentConversionError(
            f"Docling conversion error for '{source_path}': {exc}"
        ) from exc

    if result.status == ConversionStatus.FAILURE:
        raise DocumentConversionError(
            f"Docling conversion failed for '{source_path}': status={result.status}, errors={result.errors}"
        )

    if result.status == ConversionStatus.SKIPPED:
        raise DocumentConversionError(
            f"Docling conversion skipped for '{source_path}': status=SKIPPED"
        )

    # PARTIAL_SUCCESS: preserve content, make partial visible in metadata (done in _normalize_document)
    # SUCCESS: normal
    return _normalize_document(result, source_path)
