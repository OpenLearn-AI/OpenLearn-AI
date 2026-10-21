"""Minimal per-user rate limit for the write endpoints (review finding B-16).

A fixed-window counter kept in process memory and keyed by the authenticated
local user id, used as a FastAPI dependency::

    @router.post("", dependencies=[Depends(limit_writes)])

It is deliberately small: the limit is per API process (a multi-process or
multi-replica deployment would need a shared store such as Redis, or a limit at
the reverse proxy), and ``settings.rate_limit_writes_per_minute = 0`` turns it
off. Unauthenticated requests are rejected by ``get_current_user`` before they
reach the counter.
"""

import time

from fastapi import Depends, HTTPException, status as http_status

from app.api.deps import get_current_user
from app.config import settings
from app.models.user import User

_WINDOW_SECONDS = 60
#: Drop expired counters when this many users are tracked (bounds memory).
_PRUNE_THRESHOLD = 10_000

# user id -> (window start, requests in window)
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


def limit_writes(user: User = Depends(get_current_user)) -> None:
    """Reject with 429 when the user exceeds the per-minute write limit."""
    limit = settings.rate_limit_writes_per_minute
    if limit <= 0:
        return

    now = time.monotonic()
    if len(_windows) >= _PRUNE_THRESHOLD:
        _prune(now)

    key = str(user.id)
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
