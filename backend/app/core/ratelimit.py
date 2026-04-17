"""Simple in-process rate limiter.

Keyed per (user_id, action). Good enough for a single-instance Render deploy.
If you scale to multiple workers, move this to Redis.
"""
import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, status

_buckets: dict[tuple[str, str], list[float]] = defaultdict(list)
_lock = Lock()


def check(user_id: str, action: str, limit: int, window_seconds: int) -> None:
    now = time.time()
    key = (user_id, action)
    with _lock:
        hits = [t for t in _buckets[key] if now - t < window_seconds]
        if len(hits) >= limit:
            retry_after = int(window_seconds - (now - hits[0]))
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit — try again in {retry_after}s",
            )
        hits.append(now)
        _buckets[key] = hits
