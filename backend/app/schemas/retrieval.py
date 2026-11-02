"""Request/response schemas for the Week 10 material retrieval search.

POST /v1/courses/{course_id}/materials/search
"""

import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator

#: Maximum accepted query length (validated on the trimmed value); longer
#: queries are rejected before any embedding work.
MAX_QUERY_LENGTH = 512


class RetrievalSearchRequest(BaseModel):
    """Retrieval search request for one course.

    Only the search text is accepted: material, document and metadata filters
    are derived server-side from the authorized course and are never
    client-controlled. The query is untrusted plain text — it is trimmed and
    length-checked, never interpreted or transformed.
    """

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1, max_length=MAX_QUERY_LENGTH)
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum similar chunks to return (1-20).",
    )

    @field_validator("query", mode="before")
    @classmethod
    def _trim_and_reject_blank(cls, value: object) -> object:
        """Trim first so the 1-512 limits apply to the visible query text."""
        if not isinstance(value, str):
            return value  # non-str input fails the Field check as-is
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("query must not be blank")
        return trimmed


class RetrievalResult(BaseModel):
    """One retrieved chunk with its provenance (existing page conventions)."""

    model_config = ConfigDict(extra="forbid")

    material_id: uuid.UUID
    chunk_id: str = Field(
        min_length=1,
        description=(
            "Chunker-local chunk id (document id + sequence). It is not "
            "stable across reprocessing or chunking configuration changes."
        ),
    )
    content: str = Field(description="Text of the retrieved chunk.")
    pages: list[int] = Field(
        min_length=1,  # pipeline chunks always span at least one page
        description="1-based source page numbers the chunk was drawn from.",
    )
    score: float = Field(
        allow_inf_nan=False,
        description=(
            "1 minus the cosine distance of the stored vector — a similarity "
            "(higher is closer), not a probability or confidence."
        ),
    )

    @field_validator("pages", mode="before")
    @classmethod
    def _pages_positive_ints(cls, value):
        """Strict 1-based page numbers, checked before pydantic coerces
        ``"1"``, ``1.0`` and ``True`` to ``int`` — nothing but real positives
        passes. Non-list values are left to the ``list[int]`` core schema for
        its clearer error."""
        if isinstance(value, list) and not all(
            isinstance(page, int) and not isinstance(page, bool) and page > 0
            for page in value
        ):
            raise ValueError("page numbers must be positive integers")
        return value

    @field_validator("score", mode="before")
    @classmethod
    def _score_strict_number(cls, value):
        """Reject bool/str before float coercion — only real numbers pass;
        NaN/±inf are then rejected by ``allow_inf_nan=False``."""
        if isinstance(value, (bool, str)):
            raise ValueError("score must be a number")
        return value


class RetrievalSearchResponse(BaseModel):
    """Ranked results for one course; empty list means nothing matched."""

    model_config = ConfigDict(extra="forbid")

    course_id: uuid.UUID
    results: list[RetrievalResult]
