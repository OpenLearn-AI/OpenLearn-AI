"""Minimal per-user rate limit for the expensive write and retrieval
endpoints (review finding B-16).

A fixed-window counter kept in process memory and keyed by the authenticated
local user id, used as a FastAPI dependency::

    @router.post("", dependencies=[Depends(limit_writes)])
    @router.post("/search", dependencies=[Depends(limit_retrieval)])

Writes and retrieval use independent budgets (namespaced counters), so a
burst of searches can never starve material registration and vice versa.
It is deliberately small: the limit is per API process (a multi-process or
multi-replica deployment would need a shared store such as Redis, or a limit
at the reverse proxy), and both limits are disabled at ``0``
(``settings.rate_limit_writes_per_minute``,
``settings.rate_limit_retrieval_per_minute``). Retrieval is metered because
every search request runs embedding inference plus one vector query per
material on the server. Unauthenticated requests are rejected by
``get_current_user`` before they reach the counter.
"""

import time

from fastapi import Depends, HTTPException, status as http_status

from app.api.deps import get_current_user
from app.config import settings
from app.models.user import User

_WINDOW_SECONDS = 60
#: Drop expired counters when this many users are tracked (bounds memory).
_PRUNE_THRESHOLD = 10_000

# namespaced key (e.g. "write:<user id>") -> (window start, requests in window)
_windows: dict[str, tuple[float, int]] = {}


def reset_rate_limits() -> None:
    """Forget all counters (used by tests)."""
    _windows.clear()


def _prune(now: float) -> None:
    expired = [
        key for key, (start, _) in _windows.items() if now - start >= _WINDOW_SECONDS
    ]
    for key in expired:
        del _windows[key]


def _consume(key: str, limit: int) -> None:
    """Apply one fixed-window counter to ``key``; 429 once over ``limit``."""
    if limit <= 0:
        return

    now = time.monotonic()
    if len(_windows) >= _PRUNE_THRESHOLD:
        _prune(now)

    start, count = _windows.get(key, (now, 0))
    if now - start >= _WINDOW_SECONDS:
        start, count = now, 0
    if count >= limit:
        retry_after = max(1, int(_WINDOW_SECONDS - (now - start)))
        raise HTTPException(
            status_code=http_status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests; slow down and retry shortly",
            headers={"Retry-After": str(retry_after)},
        )
    _windows[key] = (start, count + 1)


def limit_writes(user: User = Depends(get_current_user)) -> None:
    """Reject with 429 when the user exceeds the per-minute write limit."""
    _consume(f"write:{user.id}", settings.rate_limit_writes_per_minute)


def limit_retrieval(user: User = Depends(get_current_user)) -> None:
    """Reject with 429 over the per-minute retrieval limit (its own budget)."""
    _consume(f"retrieval:{user.id}", settings.rate_limit_retrieval_per_minute)
