class DocumentIngestionError(Exception):
    """Base exception for document ingestion failures."""


class DocumentNotFoundError(DocumentIngestionError):
    """Raised when the requested document cannot be found."""


class UnsupportedDocumentTypeError(DocumentIngestionError):
    """Raised when a document type is not supported for ingestion."""


class DocumentConversionError(DocumentIngestionError):
    """Raised when a document fails to convert into the canonical form."""


class PageExtractionError(DocumentIngestionError):
    """Raised when a page artifact cannot be extracted from a source PDF."""
