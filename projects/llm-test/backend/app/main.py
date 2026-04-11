"""
Stackr FastAPI application entry point.

Mounts all routers and configures:
- CORS (origins from settings)
- Global exception handlers
- Health check endpoint
- Internal cron endpoint (Railway cron → trigger daily scans)
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth.router import router as auth_router
from app.config import settings
from app.routers.dependencies import router as dependencies_router
from app.routers.scan_jobs import router as scan_jobs_router
from app.routers.stacks import router as stacks_router
from app.routers.teams import router as teams_router
from app.routers.vulnerabilities import router as vulnerabilities_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Stackr API",
    description="Track your tech stack, dependencies, and CVEs in one dashboard.",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth_router)
app.include_router(teams_router)
app.include_router(stacks_router)
app.include_router(dependencies_router)
app.include_router(vulnerabilities_router)
app.include_router(scan_jobs_router)

# ---------------------------------------------------------------------------
# Health check (unauthenticated)
# ---------------------------------------------------------------------------


@app.get("/health", tags=["internal"])
async def health() -> dict:
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Internal cron endpoint — Railway cron calls this to trigger daily scans
# Protected by a shared secret in the header
# ---------------------------------------------------------------------------


@app.post("/internal/cron/scan", tags=["internal"])
async def cron_scan(request: Request) -> dict:
    """
    Daily scan trigger — called by Railway cron.
    Enqueues scan jobs for all stacks not scanned in the last 24 hours.
    Protected by X-Cron-Secret header.
    """
    from datetime import datetime, timedelta, timezone

    from sqlalchemy import select

    from app.database import AsyncSessionLocal
    from app.models.models import ScanJob, Stack

    cron_secret = request.headers.get("X-Cron-Secret")
    if cron_secret != settings.supabase_service_key:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Unauthorized"})

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    enqueued = 0

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Stack).where(
                (Stack.last_scanned_at == None) | (Stack.last_scanned_at < cutoff)  # noqa: E711
            )
        )
        stacks = result.scalars().all()

        for stack in stacks:
            job = ScanJob(
                stack_id=stack.id,
                triggered_by=None,
                status="queued",
            )
            db.add(job)
            await db.flush()

            try:
                from app.workers.scan_worker import enqueue_scan_job
                await enqueue_scan_job(str(job.id))
                enqueued += 1
            except Exception:
                logger.warning("Failed to enqueue cron scan job for stack %s", stack.id)

        await db.commit()

    return {"enqueued": enqueued}


# ---------------------------------------------------------------------------
# Global error handler — ensure JSON responses on unexpected errors
# ---------------------------------------------------------------------------


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
