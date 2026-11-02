"""Unit tests for the in-process per-user rate limiter (review finding B-16).

Covers the retrieval/write budget isolation, disabled-limit semantics, the
fixed-window expiry (with a controlled monotonic clock — no wall-clock
sleeps) and the reset helper used by the test harness itself.

The limiter is exercised through ``limit_writes`` / ``limit_retrieval``
directly with a stub user: the FastAPI wiring (``Depends(get_current_user)``
rejecting unauthenticated requests first) is covered by the endpoint tests.
"""

import uuid
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api import rate_limit as rl
from app.config import settings


class _User:
    def __init__(self):
        self.id = uuid.uuid4()


def _limit(settings_name: str, value: int, monkeypatch) -> None:
    monkeypatch.setattr(settings, settings_name, value)


def test_retrieval_exhausts_only_retrieval_budget(monkeypatch):
    _limit("rate_limit_retrieval_per_minute", 1, monkeypatch)
    _limit("rate_limit_writes_per_minute", 1, monkeypatch)
    user = _User()

    rl.limit_retrieval(user)  # consumes the one retrieval slot
    with pytest.raises(HTTPException) as retrieval_blocked:
        rl.limit_retrieval(user)
    assert retrieval_blocked.value.status_code == 429

    # The write namespace is untouched by the exhausted retrieval budget.
    rl.limit_writes(user)


def test_exhausting_writes_does_not_exhaust_retrieval(monkeypatch):
    _limit("rate_limit_writes_per_minute", 2, monkeypatch)
    _limit("rate_limit_retrieval_per_minute", 2, monkeypatch)
    user = _User()

    rl.limit_writes(user)
    rl.limit_writes(user)
    with pytest.raises(HTTPException) as writes_blocked:
        rl.limit_writes(user)
    assert writes_blocked.value.status_code == 429

    # Retrieval still has its own full budget after writes are exhausted.
    rl.limit_retrieval(user)
    rl.limit_retrieval(user)
    with pytest.raises(HTTPException) as retrieval_blocked:
        rl.limit_retrieval(user)

    assert retrieval_blocked.value.status_code == 429


def test_zero_disables_the_limit_entirely(monkeypatch):
    _limit("rate_limit_writes_per_minute", 0, monkeypatch)
    _limit("rate_limit_retrieval_per_minute", 0, monkeypatch)
    user = _User()

    for _ in range(20):
        rl.limit_writes(user)
        rl.limit_retrieval(user)  # no HTTPException raised


def test_fixed_window_expires_on_controlled_clock(monkeypatch):
    _limit("rate_limit_retrieval_per_minute", 1, monkeypatch)
    user = _User()
    clock = {"now": 1_000.0}
    # Controlled time: `_consume` reads time.monotonic through the module's
    # imported ``time`` — advancing the fake clock replaces wall-clock waits.
    monkeypatch.setattr(rl.time, "monotonic", lambda: clock["now"])

    rl.limit_retrieval(user)
    clock["now"] += 10.0  # same fixed window -> over the limit
    with pytest.raises(HTTPException) as blocked:
        rl.limit_retrieval(user)
    assert blocked.value.status_code == 429
    retry_after = int(blocked.value.headers["Retry-After"])
    assert 1 <= retry_after <= 60

    clock["now"] = 1_001.0 + 60.0  # window fully elapsed -> fresh budget
    rl.limit_retrieval(user)


def test_reset_rate_limits_clears_both_namespaces(monkeypatch):
    _limit("rate_limit_writes_per_minute", 1, monkeypatch)
    _limit("rate_limit_retrieval_per_minute", 1, monkeypatch)
    user = _User()

    rl.limit_writes(user)
    rl.limit_retrieval(user)
    with pytest.raises(HTTPException):
        rl.limit_writes(user)
    with pytest.raises(HTTPException):
        rl.limit_retrieval(user)

    rl.reset_rate_limits()

    rl.limit_writes(user)  # both counters are fresh again
    rl.limit_retrieval(user)


def test_counters_are_per_user(monkeypatch):
    _limit("rate_limit_retrieval_per_minute", 1, monkeypatch)
    first, second = _User(), _User()

    rl.limit_retrieval(first)
    rl.limit_retrieval(second)  # separate user, separate counter
    with pytest.raises(HTTPException):
        rl.limit_retrieval(first)
