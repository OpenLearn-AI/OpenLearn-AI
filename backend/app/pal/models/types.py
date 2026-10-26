from typing import Any

from pydantic import BaseModel, Field, model_validator


class HealthStatus(BaseModel):
    """Standard health-check result for a PAL provider."""

    healthy: bool
    provider: str
    message: str | None = None
    latency_ms: float | None = Field(default=None, ge=0)


class BoundingBox(BaseModel):
    """Axis-aligned bounding box for an OCR text region."""

    x1: float = Field(ge=0)
    y1: float = Field(ge=0)
    x2: float = Field(ge=0)
    y2: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_coordinates(self) -> "BoundingBox":
        if self.x1 > self.x2:
            raise ValueError(f"x1 ({self.x1}) must be <= x2 ({self.x2})")
        if self.y1 > self.y2:
            raise ValueError(f"y1 ({self.y1}) must be <= y2 ({self.y2})")
        return self


class OCRRegion(BaseModel):
    """A recognized text region returned by an OCR provider."""

    text: str
    bounding_box: BoundingBox | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    page_number: int | None = Field(default=None, ge=1)


class OCRResult(BaseModel):
    """Normalized OCR output independent of the underlying provider."""

    text: str
    regions: list[OCRRegion] = Field(default_factory=list)
    provider: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class EmbeddingResult(BaseModel):
    """Normalized embedding output."""

    vector: list[float]
    dimension: int = Field(gt=0)
    model: str
    provider: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_dimension(self) -> "EmbeddingResult":
        if len(self.vector) != self.dimension:
            raise ValueError(
                f"Embedding vector length ({len(self.vector)}) does not match declared dimension ({self.dimension})"
            )
        return self


class TokenUsage(BaseModel):
    """Token usage reported by an LLM provider when available."""

    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)


class ChatMessage(BaseModel):
    """A single chat message in a multi-turn conversation."""

    role: str
    content: str


class ReasoningChunk(BaseModel):
    """A streamed reasoning token or delta chunk."""

    text: str
    finish_reason: str | None = None
    usage: TokenUsage | None = None


class ReasoningResult(BaseModel):
    """Normalized reasoning/generation output."""

    text: str
    model: str
    provider: str
    usage: TokenUsage | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class VectorRecord(BaseModel):
    """A vector record to insert or upsert into the vector store."""

    id: str
    vector: list[float]
    content: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class VectorSearchResult(BaseModel):
    """A single vector-search result."""

    id: str
    score: float
    content: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RankingResult(BaseModel):
    """A ranked item returned by the ranking layer."""

    id: str
    score: float
    content: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

