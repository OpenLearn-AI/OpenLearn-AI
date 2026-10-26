import pytest

from app.pal.exceptions import InvalidInputError
from app.pal.models.types import ChatMessage, VectorRecord
from app.pal.providers.embedding.mock_provider import MockEmbeddingProvider
from app.pal.providers.ocr.mock_provider import MockOCRProvider
from app.pal.providers.reasoning.mock_provider import MockReasoningProvider
from app.pal.providers.vector_db.mock_provider import MockVectorDBProvider



@pytest.mark.asyncio
async def test_mock_ocr_provider():
    provider = MockOCRProvider()
    health = await provider.health_check()
    assert health.healthy is True
    assert health.provider == "mock"

    res = await provider.extract_text("sample.pdf")
    assert "Mock OCR result for: sample.pdf" in res.text
    assert res.metadata["source"] == "sample.pdf"

    batch_res = await provider.extract_text_batch(["p1.png", "p2.png"])
    assert len(batch_res) == 2
    assert "p1.png" in batch_res[0].text
    assert "p2.png" in batch_res[1].text


@pytest.mark.asyncio
async def test_mock_embedding_provider_dimension():
    provider = MockEmbeddingProvider(dimension=512)
    assert provider.dimension == 512

    health = await provider.health_check()
    assert health.healthy is True

    res = await provider.embed("hello world")
    assert res.dimension == 512
    assert len(res.vector) == 512

    batch_res = await provider.embed_batch(["text1", "text2"])
    assert len(batch_res) == 2
    assert len(batch_res[0].vector) == 512
    assert len(batch_res[1].vector) == 512


@pytest.mark.asyncio
async def test_mock_reasoning_provider():
    provider = MockReasoningProvider()
    health = await provider.health_check()
    assert health.healthy is True

    # Single string prompt
    res = await provider.reason("Explain quantum physics")
    assert "Mock response to: Explain quantum physics" in res.text
    assert res.usage is not None
    assert res.usage.total_tokens > 0

    # Chat messages input
    messages = [
        ChatMessage(role="system", content="You are a tutor."),
        ChatMessage(role="user", content="What is 2+2?"),
    ]
    res_chat = await provider.reason(messages)
    assert "What is 2+2?" in res_chat.text

    # Compatibility generate()
    gen_res = await provider.generate("Simple prompt")
    assert "Simple prompt" in gen_res.text


@pytest.mark.asyncio
async def test_mock_reasoning_provider_streaming():
    provider = MockReasoningProvider()
    chunks = []
    async for chunk in provider.reason_stream("Test prompt"):
        chunks.append(chunk)

    assert len(chunks) > 0
    full_text = "".join(c.text for c in chunks)
    assert "Mock response to: Test prompt" in full_text
    # Last chunk has stop finish_reason
    assert chunks[-1].finish_reason == "stop"


@pytest.mark.asyncio
async def test_mock_vector_db_provider_crud():
    provider = MockVectorDBProvider()
    health = await provider.health_check()
    assert health.healthy is True

    records = [
        VectorRecord(
            id="doc1:chunk1",
            vector=[1.0, 0.0],
            content="First chunk of doc1",
            metadata={"document_id": "doc1", "page": 1},
        ),
        VectorRecord(
            id="doc1:chunk2",
            vector=[0.0, 1.0],
            content="Second chunk of doc1",
            metadata={"document_id": "doc1", "page": 2},
        ),
        VectorRecord(
            id="doc2:chunk1",
            vector=[0.5, 0.5],
            content="First chunk of doc2",
            metadata={"document_id": "doc2", "page": 1},
        ),
    ]

    # Upsert
    await provider.upsert(records)

    # Get
    rec = await provider.get("doc1:chunk1")
    assert rec is not None
    assert rec.content == "First chunk of doc1"

    # Search with filters
    search_res = await provider.search(
        vector=[1.0, 0.0],
        top_k=2,
        filters={"document_id": "doc1"},
    )
    assert len(search_res) == 2
    assert search_res[0].id == "doc1:chunk1"

    # Delete by document_id filter
    deleted = await provider.delete(filters={"document_id": "doc1"})
    assert deleted == 2

    # Verify doc1 records deleted
    assert await provider.get("doc1:chunk1") is None
    assert await provider.get("doc1:chunk2") is None

    # doc2 still exists
    assert await provider.get("doc2:chunk1") is not None

    # Delete by ID
    deleted_id = await provider.delete(ids=["doc2:chunk1"])
    assert deleted_id == 1
    assert await provider.get("doc2:chunk1") is None


@pytest.mark.asyncio
async def test_mock_vector_db_cosine_similarity_ordering():
    provider = MockVectorDBProvider()

    records = [
        VectorRecord(id="orthogonal", vector=[0.0, 1.0], content="Orthogonal"),
        VectorRecord(id="opposite", vector=[-1.0, 0.0], content="Opposite"),
        VectorRecord(id="identical", vector=[1.0, 0.0], content="Identical"),
        VectorRecord(id="diagonal", vector=[1.0, 1.0], content="Diagonal (45 deg)"),
    ]
    await provider.upsert(records)

    query = [1.0, 0.0]
    results = await provider.search(query, top_k=4)

    assert len(results) == 4
    # Expected ordering: identical (~1.0), diagonal (~0.707), orthogonal (~0.0), opposite (~ -1.0)
    assert results[0].id == "identical"
    assert results[0].score == pytest.approx(1.0)

    assert results[1].id == "diagonal"
    assert results[1].score == pytest.approx(0.7071, rel=1e-3)

    assert results[2].id == "orthogonal"
    assert results[2].score == pytest.approx(0.0)

    assert results[3].id == "opposite"
    assert results[3].score == pytest.approx(-1.0)


@pytest.mark.asyncio
async def test_mock_vector_db_zero_similarity_and_zero_vector():
    provider = MockVectorDBProvider()

    records = [
        VectorRecord(id="ortho", vector=[0.0, 1.0]),
        VectorRecord(id="zero", vector=[0.0, 0.0]),
    ]
    await provider.upsert(records)

    # Orthogonal query must get 0.0, NOT 1.0
    results = await provider.search([1.0, 0.0], top_k=2)
    assert len(results) == 2
    for r in results:
        assert r.score == pytest.approx(0.0)

    # Zero query vector must return 0.0
    zero_results = await provider.search([0.0, 0.0], top_k=2)
    assert len(zero_results) == 2
    for r in zero_results:
        assert r.score == pytest.approx(0.0)


@pytest.mark.asyncio
async def test_mock_vector_db_dimension_mismatch_raises():
    provider = MockVectorDBProvider()
    await provider.upsert([VectorRecord(id="r1", vector=[1.0, 0.0])])

    with pytest.raises(InvalidInputError, match="dimension .* does not match"):
        await provider.search([1.0, 0.0, 0.0], top_k=5)

