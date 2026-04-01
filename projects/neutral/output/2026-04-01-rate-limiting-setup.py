"""
rate_limiting.py — slowapi rate limiter setup for auth endpoints
Place this file at app/rate_limiting.py

Dependencies (already in requirements.txt after auth work):
  slowapi>=0.1.9
  limits>=3.0.0      (pulled in by slowapi)

Add to requirements.txt if not present:
  slowapi>=0.1.9

Usage in app/main.py:
  from .rate_limiting import limiter, rate_limit_exceeded_handler
  from slowapi.errors import RateLimitExceeded
  from slowapi import _rate_limit_exceeded_handler

  app = FastAPI(...)
  app.state.limiter = limiter
  app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

Then decorate the auth endpoints:
  @app.post("/register", ...)
  @limiter.limit(os.getenv("RATE_LIMIT_AUTH_REGISTER", "5/minute"))
  def register(request: Request, ...):
      ...

  @app.post("/login", ...)
  @limiter.limit(os.getenv("RATE_LIMIT_AUTH_LOGIN", "10/minute"))
  def login(request: Request, ...):
      ...

Note: Request must be the FIRST positional parameter of any rate-limited endpoint.
FastAPI will inject it automatically — you do not need to declare it in the route body.
"""

import os
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Use Redis as the storage backend so limits are shared across all workers/replicas.
# Falls back to in-memory storage if REDIS_URL is not set (local dev only).
REDIS_URL = os.getenv("REDIS_URL")

if REDIS_URL:
    storage_uri = REDIS_URL
else:
    # In-memory: fine for development, but counts are per-process.
    storage_uri = "memory://"

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=storage_uri,
    # Swallow errors if Redis is temporarily unavailable so the app keeps running.
    # Set to False in production if you want hard failures when Redis is down.
    swallow_errors=True,
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Return a structured 429 instead of slowapi's default plain-text response."""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. Please slow down.",
            "retry_after": str(exc.limit.reset_time) if hasattr(exc, "limit") else None,
        },
        headers={"Retry-After": "60"},
    )
