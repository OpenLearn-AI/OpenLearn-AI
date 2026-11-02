"""Focused schema tests for retrieval request/response validation.

Covers the strengthened ``RetrievalResult`` constraints (non-empty chunk_id,
non-empty positive-int pages without booleans, finite score) and re-covers
the untouched request contract (trim/blank/length/extra/top_k) so schema
regressions surface in one place.
"""

import uuid

import pytest
from pydantic import ValidationError

from app.schemas.retrieval import (
    MAX_QUERY_LENGTH,
    RetrievalResult,
    RetrievalSearchRequest,
)


def _result(**overrides):
    base = {
        "material_id": uuid.uuid4(),
        "chunk_id": "some-doc:0",
        "content": "chunk text",
        "pages": [1],
        "score": 0.5,
    }
    base.update(overrides)
    return base


def test_valid_retrieval_result_accepts():
    result = RetrievalResult(**_result())
    assert result.score == 0.5 and result.pages == [1]


def test_empty_chunk_id_rejected():
    with pytest.raises(ValidationError):
        RetrievalResult(**_result(chunk_id=""))


def test_empty_pages_rejected():
    """Explicitly defined: the pipeline stamps at least one page per chunk,
    so an empty ``pages`` list cannot appear in a valid retrieval result."""
    with pytest.raises(ValidationError):
        RetrievalResult(**_result(pages=[]))


@pytest.mark.parametrize("pages", [[0], [1, 0], [-1], [0, 1]])
def test_non_positive_page_numbers_rejected(pages):
    with pytest.raises(ValidationError):
        RetrievalResult(**_result(pages=pages))


@pytest.mark.parametrize("pages", [[True], [False], [1, True]])
def test_boolean_page_numbers_rejected(pages):
    # ``bool`` is an ``int`` subclass; a bare int check would let it through.
    with pytest.raises(ValidationError):
        RetrievalResult(**_result(pages=pages))


@pytest.mark.parametrize("pages", [["1"], ["1", 2], [1, "3"]])
def test_string_pages_rejected(pages):
    # Numeric strings must not coerce into page numbers.
    with pytest.raises(ValidationError):
        RetrievalResult(**_result(pages=pages))


@pytest.mark.parametrize("pages", [[1.0], [1.0, 2], [1.5]])
def test_float_pages_rejected(pages):
    # Even integral floats (1.0) are not strict integers.
    with pytest.raises(ValidationError):
        RetrievalResult(**_result(pages=pages))


@pytest.mark.parametrize("chunk_id", [123, True])
def test_non_string_chunk_id_rejected(chunk_id):
    # A strictly-str ``str`` type already rejects these in lax mode; this
    # locks that behavior against a future coercion change.
    with pytest.raises(ValidationError):
        RetrievalResult(**_result(chunk_id=chunk_id))


@pytest.mark.parametrize("score", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_scores_rejected(score):
    with pytest.raises(ValidationError):
        RetrievalResult(**_result(score=score))


@pytest.mark.parametrize("score", [True, False])
def test_boolean_score_rejected(score):
    # ``bool`` is an ``int`` subclass; a bare float check would accept it.
    with pytest.raises(ValidationError):
        RetrievalResult(**_result(score=score))


@pytest.mark.parametrize("score", ["0.5", "1", "inf"])
def test_string_score_rejected(score):
    # Numeric strings must not coerce into a score.
    with pytest.raises(ValidationError):
        RetrievalResult(**_result(score=score))


def test_integer_score_is_valid_numeric():
    # Strict numeric: real numbers pass (ints coerce to float); only
    # bools/strings/non-finites are excluded.
    assert RetrievalResult(**_result(score=1)).score == 1.0


# ---------------------------------------------------------------------------
# Request contract (unchanged; regression coverage)
# ---------------------------------------------------------------------------


def test_request_trims_query_and_defaults_top_k():
    request = RetrievalSearchRequest(query="  wind of change  ")
    assert request.query == "wind of change"
    assert request.top_k == 5  # default


@pytest.mark.parametrize("top_k", [1, 20])
def test_request_top_k_bounds_accept(top_k):
    assert RetrievalSearchRequest(query="x", top_k=top_k).top_k == top_k


@pytest.mark.parametrize("top_k", [0, 21, -1])
def test_request_top_k_bounds_reject(top_k):
    with pytest.raises(ValidationError):
        RetrievalSearchRequest(query="x", top_k=top_k)


def test_request_blank_query_rejected():
    with pytest.raises(ValidationError):
        RetrievalSearchRequest(query="   ")


def test_request_query_length_cap_applies_to_trimmed_text():
    assert len(RetrievalSearchRequest(query="x" * MAX_QUERY_LENGTH).query) == (
        MAX_QUERY_LENGTH
    )
    with pytest.raises(ValidationError):
        RetrievalSearchRequest(query="x" * (MAX_QUERY_LENGTH + 1))


def test_request_extra_fields_forbidden():
    with pytest.raises(ValidationError):
        RetrievalSearchRequest(query="x", top_k=2, material_id=uuid.uuid4())


def test_request_non_string_query_rejected():
    with pytest.raises(ValidationError):
        RetrievalSearchRequest(query=123)
