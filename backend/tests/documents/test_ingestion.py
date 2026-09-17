"""Isolated unit tests for app.services.ingestion.ingest_document.

Docling's DocumentConverter is patched at the import location used by the
production module (``app.services.ingestion.DocumentConverter``), so no real
conversion, model download, network access, or OCR is performed.

The mocked conversion results are built from the real Docling classes
(``ConversionResult.model_construct`` for the result envelope, real
``DoclingDocument`` content models) so the fakes match the Docling 2.127.0
runtime shape actually consumed by the production code.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from docling.datamodel.base_models import ConversionStatus, ErrorItem, InputFormat
from docling.datamodel.document import ConversionResult
from docling.exceptions import ConversionError
from docling_core.types.doc.document import (
    DoclingDocument,
    DocumentOrigin,
    PageItem,
    ProvenanceItem,
    Size,
    TextItem,
)
from docling_core.types.doc.labels import DocItemLabel

from app.documents import (
    CanonicalDocument,
    DocumentConversionError,
    DocumentNotFoundError,
)
from app.documents.exceptions import UnsupportedDocumentTypeError
from app.services.ingestion import ingest_document

# ---------------------------------------------------------------------------
# Helpers: deterministic fakes matching the Docling 2.127.0 runtime shape.
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


def _conversion_error(page_no: int, message: str) -> ErrorItem:
    """Build an ErrorItem as Docling pipelines attach to partial results."""
    return ErrorItem.model_construct(
        component_type="model",
        module_name="page_assembly",
        error_message=message,
        page_no=page_no,
    )


@pytest.fixture()
def converter_cls(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Patch DocumentConverter in the production module's namespace."""
    cls_mock = MagicMock(name="DocumentConverter")
    monkeypatch.setattr("app.services.ingestion.DocumentConverter", cls_mock)
    return cls_mock


# ---------------------------------------------------------------------------
# SUCCESS paths
# ---------------------------------------------------------------------------


def test_success_single_page_returns_canonical_document(
    tmp_path: Path, converter_cls: MagicMock
) -> None:
    source = _make_source_file(tmp_path, "single_page.pdf")
    converter_cls.return_value.convert.return_value = _conversion_result(
        ConversionStatus.SUCCESS,
        _docling_document(
            pages={1: _page_item(1, Size(width=612.0, height=792.0))},
            texts=[_text_item("#/texts/0", "Hello ingestion", 1)],
        ),
    )

    result = ingest_document(source)

    assert isinstance(result, CanonicalDocument)
    assert len(result.pages) == 1
    page = result.pages[0]
    assert page.page_number == 1
    assert page.text == "Hello ingestion"
    assert page.metadata == {"page_size": {"width": 612.0, "height": 792.0}}

    resolved = source.resolve()
    assert result.source == str(resolved)
    converter_cls.return_value.convert.assert_called_once_with(
        resolved, raises_on_error=True
    )


def test_success_multiple_pages_grouped_by_page_no_in_ascending_order(
    tmp_path: Path, converter_cls: MagicMock
) -> None:
    source = _make_source_file(tmp_path, "multi_page.pdf")
    # Pages inserted out of order on purpose: ingestion must sort deterministically.
    converter_cls.return_value.convert.return_value = _conversion_result(
        ConversionStatus.SUCCESS,
        _docling_document(
            pages={3: _page_item(3), 1: _page_item(1), 2: _page_item(2)},
            texts=[
                _text_item("#/texts/0", "page two text", 2),
                _text_item("#/texts/1", "page three text", 3),
                _text_item("#/texts/2", "page one text", 1),
            ],
        ),
    )

    result = ingest_document(source)

    assert [page.page_number for page in result.pages] == [1, 2, 3]
    assert result.pages[0].text == "page one text"
    assert result.pages[1].text == "page two text"
    assert result.pages[2].text == "page three text"


def test_success_preserves_page_without_text_items(
    tmp_path: Path, converter_cls: MagicMock
) -> None:
    source = _make_source_file(tmp_path, "with_empty_page.pdf")
    converter_cls.return_value.convert.return_value = _conversion_result(
        ConversionStatus.SUCCESS,
        _docling_document(
            pages={1: _page_item(1), 2: _page_item(2)},
            texts=[_text_item("#/texts/0", "only on page one", 1)],
        ),
    )

    result = ingest_document(source)

    assert [page.page_number for page in result.pages] == [1, 2]
    assert result.pages[0].text == "only on page one"
    assert result.pages[1].text == ""


def test_success_joins_multiple_text_items_in_doc_texts_order(
    tmp_path: Path, converter_cls: MagicMock
) -> None:
    source = _make_source_file(tmp_path, "multi_item.pdf")
    converter_cls.return_value.convert.return_value = _conversion_result(
        ConversionStatus.SUCCESS,
        _docling_document(
            pages={1: _page_item(1)},
            texts=[
                _text_item("#/texts/0", "first chunk", 1),
                _text_item("#/texts/1", "second chunk", 1),
                _text_item("#/texts/2", "third chunk", 1),
            ],
        ),
    )

    result = ingest_document(source)

    assert result.pages[0].text == "first chunk\nsecond chunk\nthird chunk"


# ---------------------------------------------------------------------------
# Input validation (converter must never be created)
# ---------------------------------------------------------------------------


def test_missing_source_raises_document_not_found_without_converter(
    tmp_path: Path, converter_cls: MagicMock
) -> None:
    missing = tmp_path / "does_not_exist.pdf"

    with pytest.raises(DocumentNotFoundError, match="does_not_exist"):
        ingest_document(missing)

    converter_cls.assert_not_called()


def test_unsupported_extension_raises_unsupported_type_without_converter(
    tmp_path: Path, converter_cls: MagicMock
) -> None:
    source = _make_source_file(tmp_path, "archive.xyz")

    with pytest.raises(UnsupportedDocumentTypeError, match=r"\.xyz"):
        ingest_document(source)

    converter_cls.assert_not_called()


@pytest.mark.parametrize(
    ("filename", "expected_format"),
    [
        ("document.pdf", InputFormat.PDF),
        ("notes.md", InputFormat.MD),
        ("contract.docx", InputFormat.DOCX),
    ],
)
def test_converter_is_created_with_detected_allowed_format(
    tmp_path: Path,
    converter_cls: MagicMock,
    filename: str,
    expected_format: InputFormat,
) -> None:
    source = _make_source_file(tmp_path, filename)
    converter_cls.return_value.convert.return_value = _conversion_result(
        ConversionStatus.SUCCESS, _docling_document(pages={1: _page_item(1)})
    )

    ingest_document(source)

    converter_cls.assert_called_once_with(allowed_formats=[expected_format])


# ---------------------------------------------------------------------------
# Conversion status handling
# ---------------------------------------------------------------------------


def test_failure_status_raises_document_conversion_error(
    tmp_path: Path, converter_cls: MagicMock
) -> None:
    source = _make_source_file(tmp_path, "broken.pdf")
    converter_cls.return_value.convert.return_value = _conversion_result(
        ConversionStatus.FAILURE, None
    )

    with pytest.raises(DocumentConversionError, match="failed"):
        ingest_document(source)


def test_skipped_status_raises_document_conversion_error(
    tmp_path: Path, converter_cls: MagicMock
) -> None:
    source = _make_source_file(tmp_path, "skipped.pdf")
    converter_cls.return_value.convert.return_value = _conversion_result(
        ConversionStatus.SKIPPED, None
    )

    with pytest.raises(DocumentConversionError, match="skipped"):
        ingest_document(source)


def test_partial_success_preserves_content_and_reports_errors_in_metadata(
    tmp_path: Path, converter_cls: MagicMock
) -> None:
    source = _make_source_file(tmp_path, "partial.pdf")
    converter_cls.return_value.convert.return_value = _conversion_result(
        ConversionStatus.PARTIAL_SUCCESS,
        _docling_document(
            pages={1: _page_item(1), 2: _page_item(2)},
            texts=[
                _text_item("#/texts/0", "page one recovered", 1),
                _text_item("#/texts/1", "page two recovered", 2),
            ],
        ),
        errors=[_conversion_error(page_no=2, message="some items could not be extracted")],
    )

    result = ingest_document(source)

    assert isinstance(result, CanonicalDocument)
    # Content is preserved despite the partial failure.
    assert [page.text for page in result.pages] == [
        "page one recovered",
        "page two recovered",
    ]

    assert result.metadata["conversion_status"] == ConversionStatus.PARTIAL_SUCCESS.value
    reported = result.metadata["conversion_errors"]
    assert isinstance(reported, list) and len(reported) == 1
    error_entry = reported[0]
    assert error_entry["component_type"] == "model"
    assert error_entry["module_name"] == "page_assembly"
    assert error_entry["message"] == "some items could not be extracted"
    assert error_entry["page_no"] == 2


# ---------------------------------------------------------------------------
# Error boundaries
# ---------------------------------------------------------------------------


def test_docling_conversion_error_is_wrapped_with_original_cause(
    tmp_path: Path, converter_cls: MagicMock
) -> None:
    source = _make_source_file(tmp_path, "raises.pdf")
    converter_cls.return_value.convert.side_effect = ConversionError(
        "docling could not parse the document"
    )

    with pytest.raises(DocumentConversionError) as excinfo:
        ingest_document(source)

    assert "docling could not parse the document" in str(excinfo.value)
    assert isinstance(excinfo.value.__cause__, ConversionError)


def test_unexpected_exception_propagates_unwrapped(
    tmp_path: Path, converter_cls: MagicMock
) -> None:
    source = _make_source_file(tmp_path, "unexpected.pdf")
    converter_cls.return_value.convert.side_effect = RuntimeError(
        "unexpected internal error"
    )

    # No broad "except Exception" in production code: RuntimeError must surface.
    with pytest.raises(RuntimeError, match="unexpected internal error"):
        ingest_document(source)


# ---------------------------------------------------------------------------
# Metadata and identity
# ---------------------------------------------------------------------------


def test_source_metadata_from_docling_origin_is_preserved(
    tmp_path: Path, converter_cls: MagicMock
) -> None:
    source = _make_source_file(tmp_path, "origin_metadata.pdf")
    origin = DocumentOrigin(
        filename="origin_metadata.pdf",
        mimetype="application/pdf",
        binary_hash=1234567890123456789,
        uri="file:///fixtures/origin_metadata.pdf",
    )
    converter_cls.return_value.convert.return_value = _conversion_result(
        ConversionStatus.SUCCESS,
        _docling_document(
            pages={1: _page_item(1)},
            texts=[_text_item("#/texts/0", "text", 1)],
            origin=origin,
        ),
    )

    result = ingest_document(source)

    assert result.metadata["filename"] == "origin_metadata.pdf"
    assert result.metadata["mimetype"] == "application/pdf"
    assert result.metadata["binary_hash"] == 1234567890123456789
    assert result.metadata["uri"] == "file:///fixtures/origin_metadata.pdf"


def test_document_identity_is_derived_from_source_stem(
    tmp_path: Path, converter_cls: MagicMock
) -> None:
    source = _make_source_file(tmp_path, "My.Report.v2.pdf")
    converter_cls.return_value.convert.return_value = _conversion_result(
        ConversionStatus.SUCCESS, _docling_document(pages={1: _page_item(1)})
    )

    result = ingest_document(source)

    assert result.document_id == source.stem
    assert result.document_id == "My.Report.v2"
    assert result.title == "My.Report.v2"
