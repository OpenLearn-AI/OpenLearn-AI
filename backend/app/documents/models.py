from pydantic import BaseModel, Field


class Page(BaseModel):
    """A single page of extracted document content."""

    page_number: int = Field(ge=1)
    text: str
    metadata: dict[str, object] = Field(default_factory=dict)


class CanonicalDocument(BaseModel):
    """Application-owned normalized document, independent of any ingestion engine."""

    document_id: str
    source: str
    title: str | None = None
    language: str | None = None
    pages: list[Page] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)