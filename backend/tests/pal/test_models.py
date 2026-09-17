import pytest
from pydantic import ValidationError

from app.pal.models.types import (
    BoundingBox,
    ChatMessage,
    EmbeddingResult,
    OCRRegion,
    ReasoningChunk,
    ReasoningResult,
    TokenUsage,
    VectorRecord,
    VectorSearchResult,
)



def test_embedding_result_valid_dimension():
    vec = [0.1, 0.2, 0.3, 0.4]
    res = EmbeddingResult(
        vector=vec,
        dimension=4,
        model="test-model",
        provider="test-provider",
    )
    assert res.dimension == 4
    assert len(res.vector) == 4


def test_embedding_result_dimension_mismatch_raises():
    vec = [0.1, 0.2, 0.3]
    with pytest.raises(ValidationError, match="does not match declared dimension"):
        EmbeddingResult(
            vector=vec,
            dimension=4,
            model="test-model",
            provider="test-provider",
        )


def test_bounding_box_valid():
    bb = BoundingBox(x1=0.0, y1=10.0, x2=100.0, y2=50.0)
    assert bb.x1 == 0.0
    assert bb.x2 == 100.0
    assert bb.y1 == 10.0
    assert bb.y2 == 50.0


def test_bounding_box_x1_greater_than_x2_raises():
    with pytest.raises(ValidationError, match="x1 .* must be <= x2"):
        BoundingBox(x1=100.0, y1=0.0, x2=50.0, y2=10.0)


def test_bounding_box_y1_greater_than_y2_raises():
    with pytest.raises(ValidationError, match="y1 .* must be <= y2"):
        BoundingBox(x1=0.0, y1=50.0, x2=10.0, y2=20.0)


def test_bounding_box_negative_raises():
    with pytest.raises(ValidationError):
        BoundingBox(x1=-1.0, y1=0.0, x2=10.0, y2=10.0)


def test_ocr_region_confidence_valid():
    region = OCRRegion(
        text="Sample",
        bounding_box=BoundingBox(x1=0, y1=0, x2=10, y2=10),
        confidence=0.95,
        page_number=1,
    )
    assert region.confidence == 0.95
    assert region.page_number == 1


def test_ocr_region_confidence_out_of_range():
    with pytest.raises(ValidationError):
        OCRRegion(text="Sample", confidence=1.5)

    with pytest.raises(ValidationError):
        OCRRegion(text="Sample", confidence=-0.1)


def test_token_usage_validation():
    usage = TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
    assert usage.total_tokens == 30

    with pytest.raises(ValidationError):
        TokenUsage(prompt_tokens=-1)


def test_reasoning_models():
    msg = ChatMessage(role="user", content="Hello")
    assert msg.role == "user"

    chunk = ReasoningChunk(text="token", finish_reason=None)
    assert chunk.text == "token"

    res = ReasoningResult(
        text="Full response",
        model="test",
        provider="mock",
        usage=TokenUsage(prompt_tokens=5, completion_tokens=5, total_tokens=10),
    )
    assert res.text == "Full response"
    assert res.usage.total_tokens == 10


def test_vector_models():
    rec = VectorRecord(id="doc:1", vector=[0.1, 0.2], content="text", metadata={"page": 1})
    assert rec.id == "doc:1"
    assert rec.metadata["page"] == 1

    search_res = VectorSearchResult(id="doc:1", score=0.95, content="text")
    assert search_res.score == 0.95
