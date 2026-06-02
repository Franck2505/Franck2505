"""In-memory rate limiter. Replace with Redis-backed SlowAPI in production."""
import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

_counters: dict[str, list] = defaultdict(list)
RATE_LIMITS = {
    "/auth/login": (10, 60),
    "/auth/register": (5, 60),
    "default": (200, 60),
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        path = request.url.path
        limit, window = RATE_LIMITS.get(path, RATE_LIMITS["default"])
        now = time.time()
        _counters[ip] = [(ts, c) for ts, c in _counters[ip] if now - ts < window]
        if sum(c for _, c in _counters[ip]) >= limit:
            raise HTTPException(status_code=429, detail="Too many requests.")
        _counters[ip].append((now, 1))
        return await call_next(request)
