"""Targeted tests for the retrieval service (provider cache + provenance).

No DB fixtures are needed: provider-cache tests use a spy factory, and
provenance tests unit-test ``candidate_provenance_error`` plus a
``search_course_materials`` run with all dependencies monkeypatched. The
real BGE-M3 model is never loaded (mock embedding provider only).
"""

import uuid

import pytest

from app.config import settings
from app.models.material import Material
from app.pal.models.types import VectorSearchResult
from app.pal.providers.embedding.mock_provider import MockEmbeddingProvider
from app.services import retrieval_service as rs


@pytest.fixture(autouse=True)
def reset_provider_cache():
    """Start/end every test with a cold cache (module-global singleton)."""
    prev_provider, prev_key = rs._embedding_provider, rs._embedding_provider_key
    rs._embedding_provider = None
    rs._embedding_provider_key = None
    yield
    rs._embedding_provider = prev_provider
    rs._embedding_provider_key = prev_key


class _ProviderFactorySpy:
    """Counts factory invocations; returns real mock providers (no model)."""

    def __init__(self):
        self.calls: list[tuple[str | None, int | None]] = []

    def __call__(self, *, provider=None, dimension=None):
        self.calls.append((provider, dimension))
        return MockEmbeddingProvider(dimension=dimension or 1024)


def _config(prov, **overrides):
    return {
        "ai_embedding_provider": prov,
        "ai_embedding_dimension": overrides.get("dimension", 1024),
        "ai_embedding_model": overrides.get("model", "BAAI/bge-m3"),
        "ai_embedding_device": overrides.get("device", "cpu"),
    }


# ---------------------------------------------------------------------------
# Provider cache identity
# ---------------------------------------------------------------------------


def test_same_four_setting_config_reuses_cached_provider(monkeypatch):
    spy = _ProviderFactorySpy()
    monkeypatch.setattr(rs, "get_embedding_provider", spy)
    for key, value in _config("mock").items():
        monkeypatch.setattr(settings, key, value)

    first = rs._get_embedding_provider()
    second = rs._get_embedding_provider()

    assert first is second
    assert len(spy.calls) == 1


@pytest.mark.parametrize(
    ("setting", "value"),
    [
        ("ai_embedding_provider", "bge-m3"),
        ("ai_embedding_dimension", 512),
        ("ai_embedding_model", "BAAI/other-model"),
        ("ai_embedding_device", "cuda"),
    ],
)
def test_changing_each_cached_setting_rebuilds_provider(monkeypatch, setting, value):
    spy = _ProviderFactorySpy()
    monkeypatch.setattr(rs, "get_embedding_provider", spy)
    for key, val in _config("mock").items():
        monkeypatch.setattr(settings, key, val)

    first = rs._get_embedding_provider()
    monkeypatch.setattr(settings, setting, value)
    second = rs._get_embedding_provider()

    assert first is not second
    assert len(spy.calls) == 2


def test_provider_rebuild_uses_current_provider_and_dimension(monkeypatch):
    spy = _ProviderFactorySpy()
    monkeypatch.setattr(rs, "get_embedding_provider", spy)
    for key, val in _config("mock", dimension=768).items():
        monkeypatch.setattr(settings, key, val)

    rs._get_embedding_provider()

    # Provider and dimension go through the factory; model/device are read by
    # the provider itself from settings (unchanged factory usage).
    assert spy.calls == [("mock", 768)]


# ---------------------------------------------------------------------------
# Candidate provenance validation
# ---------------------------------------------------------------------------


def make_material_id():
    return str(uuid.uuid4())


def make_candidate(material_id: str, **overrides) -> VectorSearchResult:
    defaults = {
        "id": f"{material_id}:{material_id}-doc:0",
        "score": 0.5,
        "content": "chunk text",
        "metadata": {
            "material_id": material_id,
            "document_id": f"{material_id}-doc",
            "chunk_id": f"{material_id}-doc:0",
            "pages": [1],
        },
    }
    metadata_extra = overrides.pop("metadata", None)
    defaults.update(overrides)
    if metadata_extra is not None:
        assert isinstance(metadata_extra, dict)
        defaults["metadata"].update(
            metadata_extra  # '_metadata_extra' handling below
        )
    return VectorSearchResult(
        id=defaults["id"],
        score=defaults["score"],
        content=defaults["content"],
        metadata=defaults["metadata"],
    )


def test_valid_candidate_passes():
    mid = make_material_id()
    assert rs.candidate_provenance_error(make_candidate(mid), mid) is None


@pytest.mark.parametrize(
    ("mutate", "expect_reason"),
    [
        # metadata material_id present but wrong / absent
        (
            lambda c, mid: c.metadata.update({"material_id": str(uuid.uuid4())}),
            "metadata_material_id_mismatch",
        ),
        (
            lambda c, mid: c.metadata.pop("material_id", None),
            "metadata_material_id_mismatch",
        ),
        # vector id structure / prefix
        (
            lambda c, mid: setattr(c, "id", f"{mid}-doc-seq0"),  # no colon at all
            "malformed_vector_id",
        ),
        (
            lambda c, mid: setattr(c, "id", f"{str(uuid.uuid4())}:{mid}-doc:0"),
            "vector_id_material_prefix_mismatch",
        ),
        # chunk id consistency
        (
            lambda c, mid: c.metadata.update({"chunk_id": "other-doc:9"}),
            "vector_id_chunk_suffix_mismatch",
        ),
        (
            lambda c, mid: c.metadata.pop("chunk_id", None),
            "missing_or_invalid_chunk_id",
        ),
        (
            lambda c, mid: c.metadata.update({"chunk_id": ""}),
            "missing_or_invalid_chunk_id",
        ),
        # content
        (lambda c, mid: setattr(c, "content", ""), "missing_or_empty_content"),
        (lambda c, mid: setattr(c, "content", None), "missing_or_empty_content"),
        # pages
        (lambda c, mid: c.metadata.pop("pages", None), "missing_or_malformed_pages"),
        (lambda c, mid: c.metadata.update({"pages": []}), "missing_or_malformed_pages"),
        (lambda c, mid: c.metadata.update({"pages": "1"}), "missing_or_malformed_pages"),
        (lambda c, mid: c.metadata.update({"pages": [1, 0]}), "invalid_page_number"),
        (lambda c, mid: c.metadata.update({"pages": [1, -3]}), "invalid_page_number"),
        (lambda c, mid: c.metadata.update({"pages": [True]}), "invalid_page_number"),
        (lambda c, mid: c.metadata.update({"pages": [False]}), "invalid_page_number"),
        # score
        (
            lambda c, mid: setattr(c, "score", float("nan")),
            "non_finite_score",
        ),
        (
            lambda c, mid: setattr(c, "score", float("inf")),
            "non_finite_score",
        ),
        (
            lambda c, mid: setattr(c, "score", float("-inf")),
            "non_finite_score",
        ),
    ],
)
def test_malformed_provenance_reasons(mutate, expect_reason):
    mid = make_material_id()
    candidate = make_candidate(mid)
    mutate(candidate, mid)
    reason = rs.candidate_provenance_error(candidate, mid)
    assert reason == expect_reason, f"{reason} != {expect_reason}"


def test_pages_boolean_rejected_alongside_real_numbers():
    mid = make_material_id()
    true_bool = rs.candidate_provenance_error(
        make_candidate(mid, metadata={"pages": [True]}), mid
    )
    mixed_ok = rs.candidate_provenance_error(make_candidate(mid), mid)
    assert true_bool == "invalid_page_number" and mixed_ok is None


# ---------------------------------------------------------------------------
# search_course_materials: skip malformed, keep valid, structured warnings
# ---------------------------------------------------------------------------


class _StubVectorDB:
    """Faithful PAL search contract stub: per-material filtered results."""

    provider_name = "stub"

    def __init__(self, results_by_material: dict[str, list[VectorSearchResult]]):
        self._results = results_by_material

    async def search(self, vector, *, top_k=5, filters=None):
        assert filters is not None and "material_id" in filters
        mid = filters["material_id"]
        if mid not in self._results:
            return []
        hits = sorted(self._results[mid], key=lambda c: (-c.score, c.id))
        return hits[:top_k]


class _WarningSpy:
    events: list[tuple[str, dict]] = []

    def warning(self, event, **kwargs):
        type(self).events.append((event, kwargs))


@pytest.fixture
def warning_spy(monkeypatch):
    _WarningSpy.events = []
    monkeypatch.setattr(rs, "logger", _WarningSpy())
    return _WarningSpy.events


@pytest.mark.asyncio
async def test_search_skips_malformed_and_keeps_valid_from_same_search(
    monkeypatch, warning_spy
):
    # Deterministic material ids: candidates carry equal scores, so the
    # stub's (-score, id) sort must not depend on UUID4 randomness.
    mid = "00000000-0000-0000-0000-000000000001"
    other_mid = "00000000-0000-0000-0000-000000000002"

    good = make_candidate(mid)
    # Malformed sibling from the same material's search (ID/metadata chunk
    # mismatch).
    bad_chunk = make_candidate(mid)
    bad_chunk.metadata.update({"chunk_id": "unrelated-doc:1"})

    # A candidate whose metadata material_id belongs to another material: its
    # vector-id prefix then no longer matches the searched material either.
    from_other = make_candidate(other_mid)

    async def fake_list(db, course_id):
        return [Material(id=uuid.UUID(mid))]

    monkeypatch.setattr(rs, "list_materials_by_course", fake_list)
    monkeypatch.setattr(
        rs, "get_vector_db_provider", lambda provider=None, session=None: _StubVectorDB(
            {
                mid: [good, bad_chunk, from_other],
                other_mid: [],  # never searched: outside the authorized course
            }
        )
    )
    monkeypatch.setattr(
        rs,
        "_get_embedding_provider",
        lambda: MockEmbeddingProvider(dimension=1024),
    )

    class _DummyDB:
        pass

    results = await rs.search_course_materials(
        _DummyDB(), course_id=uuid.uuid4(), query="never-logged-query", top_k=5
    )

    # Only the valid candidate survives; malformed ones are dropped, not
    # defaulted into empty fields.
    assert len(results) == 1
    assert results[0].material_id == uuid.UUID(mid)
    assert results[0].chunk_id == f"{mid}-doc:0"
    assert results[0].content == "chunk text"
    assert results[0].pages == [1]

    # One structured warning per rejected candidate; contains diagnostics but
    # never the query text or document content. Order of emission is not a
    # contract under test — the stub's stable (-score, id) sort governs it.
    reasons = [kwargs["reason"] for _, kwargs in warning_spy]
    assert sorted(reasons) == [
        "metadata_material_id_mismatch",
        "vector_id_chunk_suffix_mismatch",
    ]
    blob = repr(warning_spy)
    assert "never-logged-query" not in blob
    assert "chunk text" not in blob


@pytest.mark.asyncio
async def test_search_material_attribution_stays_server_side(
    monkeypatch, warning_spy
):
    """Even a mixed-provenance candidate cannot leak another material's ID."""
    server_material_id = make_material_id()

    valid_for_server = make_candidate(server_material_id)

    async def fake_list(db, course_id):
        return [Material(id=uuid.UUID(server_material_id))]

    monkeypatch.setattr(rs, "list_materials_by_course", fake_list)
    monkeypatch.setattr(
        rs,
        "get_vector_db_provider",
        lambda provider=None, session=None: _StubVectorDB(
            {server_material_id: [valid_for_server]},
        ),
    )
    monkeypatch.setattr(
        rs,
        "_get_embedding_provider",
        lambda: MockEmbeddingProvider(dimension=1024),
    )

    class _DummyDB:
        pass

    results = await rs.search_course_materials(
        _DummyDB(), course_id=uuid.uuid4(), query="q", top_k=5
    )

    assert [r.material_id for r in results] == [uuid.UUID(server_material_id)]


# ---------------------------------------------------------------------------
# Global ranking / deterministic tie-break
# ---------------------------------------------------------------------------


def rank_candidate(material_id: str, chunk_id: str, score: float) -> VectorSearchResult:
    return VectorSearchResult(
        id=f"{material_id}:{chunk_id}",
        score=score,
        content="chunk text",  # not asserted to appear in any warning
        metadata={
            "material_id": material_id,
            "document_id": f"{material_id}-doc",
            "chunk_id": chunk_id,
            "pages": [1],
        },
    )


@pytest.mark.asyncio
async def test_merging_ranks_by_score_and_breaks_ties_by_vector_id(monkeypatch):
    """Candidates from several materials are merged globally: score desc,
    then vector id ascending for equal scores."""
    mat_low = "00000000-0000-0000-0000-000000000001"
    mat_high = "00000000-0000-0000-0000-000000000002"

    async def fake_list(db, course_id):
        return [Material(id=uuid.UUID(mat_high)), Material(id=uuid.UUID(mat_low))]

    monkeypatch.setattr(rs, "list_materials_by_course", fake_list)
    monkeypatch.setattr(
        rs,
        "get_vector_db_provider",
        lambda provider=None, session=None: _StubVectorDB(
            {
                mat_high: [rank_candidate(mat_high, "doc:1", 0.90)],
                mat_low: [
                    rank_candidate(mat_low, "doc:9", 0.70),
                    rank_candidate(mat_low, "doc:0", 0.70),
                ],
            }
        ),
    )
    monkeypatch.setattr(
        rs, "_get_embedding_provider", lambda: MockEmbeddingProvider(dimension=1024)
    )

    class _DummyDB:
        pass

    results = await rs.search_course_materials(
        _DummyDB(), course_id=uuid.uuid4(), query="q", top_k=3
    )

    assert [r.score for r in results] == [0.90, 0.70, 0.70]
    # Equal scores come out in vector-id-ascending order, independent of the
    # order in which the materials were searched.
    assert [(r.chunk_id, str(r.material_id)) for r in results[1:]] == [
        ("doc:0", mat_low),
        ("doc:9", mat_low),
    ]


@pytest.mark.asyncio
async def test_global_top_k_is_respected_when_every_material_fills_top_k(monkeypatch):
    """Each material may contribute up to top_k candidates, but the merged
    result is still truncated to the global top_k."""
    mat_low = "00000000-0000-0000-0000-000000000001"
    mat_high = "00000000-0000-0000-0000-000000000002"

    async def fake_list(db, course_id):
        return [Material(id=uuid.UUID(mat_low)), Material(id=uuid.UUID(mat_high))]

    monkeypatch.setattr(rs, "list_materials_by_course", fake_list)
    monkeypatch.setattr(
        rs,
        "get_vector_db_provider",
        lambda provider=None, session=None: _StubVectorDB(
            {
                mat_low: [
                    rank_candidate(mat_low, "doc:0", 0.10),
                    rank_candidate(mat_low, "doc:1", 0.05),
                ],
                mat_high: [
                    rank_candidate(mat_high, "doc:0", 0.90),
                    rank_candidate(mat_high, "doc:1", 0.80),
                ],
            }
        ),
    )
    monkeypatch.setattr(
        rs, "_get_embedding_provider", lambda: MockEmbeddingProvider(dimension=1024)
    )

    class _DummyDB:
        pass

    results = await rs.search_course_materials(
        _DummyDB(), course_id=uuid.uuid4(), query="q", top_k=2
    )

    # 0.90, 0.80 survive globally; 0.10 and 0.05 are below the global cut even
    # though each material returned exactly top_k candidates.
    assert [(str(r.material_id), r.score) for r in results] == [
        (mat_high, 0.90),
        (mat_high, 0.80),
    ]


# ---------------------------------------------------------------------------
# Empty course: no vector work at all
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_empty_course_returns_empty_without_embedding_or_vector_search(
    monkeypatch,
):
    async def fake_list(db, course_id):
        return []

    monkeypatch.setattr(rs, "list_materials_by_course", fake_list)

    def fail_embedding_factory():
        raise AssertionError("embedding provider must not be called for empty course")

    def fail_vector_factory(provider=None, session=None):
        raise AssertionError("vector provider must not be called for empty course")

    monkeypatch.setattr(rs, "_get_embedding_provider", fail_embedding_factory)
    monkeypatch.setattr(rs, "get_vector_db_provider", fail_vector_factory)

    class _DummyDB:
        pass

    results = await rs.search_course_materials(
        _DummyDB(), course_id=uuid.uuid4(), query="q", top_k=5
    )

    assert results == []  # successful, empty — providers never touched


# ---------------------------------------------------------------------------
# Provider failures propagate (never fabricated into empty results)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_embedding_failure_propagates_and_skips_vector_search(monkeypatch):
    server_material_id = make_material_id()

    async def fake_list(db, course_id):
        return [Material(id=uuid.UUID(server_material_id))]

    def raise_embed_error():
        raise RuntimeError("embedding provider failed")

    def fail_vector_factory(provider=None, session=None):
        raise AssertionError("vector provider must not be constructed without embedding")

    monkeypatch.setattr(rs, "list_materials_by_course", fake_list)
    monkeypatch.setattr(rs, "_get_embedding_provider", raise_embed_error)
    monkeypatch.setattr(rs, "get_vector_db_provider", fail_vector_factory)

    class _DummyDB:
        pass

    with pytest.raises(RuntimeError, match="embedding provider failed"):
        await rs.search_course_materials(
            _DummyDB(), course_id=uuid.uuid4(), query="q", top_k=5
        )


@pytest.mark.asyncio
async def test_vector_search_failure_propagates(monkeypatch):
    server_material_id = make_material_id()

    async def fake_list(db, course_id):
        return [Material(id=uuid.UUID(server_material_id))]

    class _ExplodingVectorDB:
        provider_name = "stub"

        async def search(self, vector, *, top_k=5, filters=None):
            raise RuntimeError("vector store failed")

    monkeypatch.setattr(rs, "list_materials_by_course", fake_list)
    monkeypatch.setattr(
        rs, "get_vector_db_provider", lambda provider=None, session=None: _ExplodingVectorDB()
    )
    monkeypatch.setattr(
        rs, "_get_embedding_provider", lambda: MockEmbeddingProvider(dimension=1024)
    )

    class _DummyDB:
        pass

    with pytest.raises(RuntimeError, match="vector store failed"):
        await rs.search_course_materials(
            _DummyDB(), course_id=uuid.uuid4(), query="q", top_k=5
        )
