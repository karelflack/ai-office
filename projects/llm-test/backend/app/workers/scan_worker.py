"""
ARQ scan worker — processes vulnerability scan jobs from the Redis queue.

This module is the entry point for the Railway worker dyno.
Run with: arq app.workers.scan_worker.WorkerSettings

Key design points (bjorn ADR 4.3):
- Uses service role key for DB access (worker bypasses RLS — acceptable for worker)
- Jobs are dequeued from Redis by ARQ, processed, and results written to cve_matches
- scan_jobs.status is updated at each stage so the API can be polled for progress
- OSV querybatch reduces HTTP round-trips (up to 100 packages per request)
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from arq import ArqRedis
from arq.connections import RedisSettings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.models import CveMatch, Dependency, ScanJob, Stack
from app.services.scanner import OSV_BATCH_SIZE, parse_osv_vulnerability, query_osv_batch

logger = logging.getLogger(__name__)


async def run_scan(ctx: dict, job_id: str) -> dict:
    """
    ARQ task: run a full vulnerability scan for a single scan job.

    Steps:
    1. Load job + stack + dependencies from DB
    2. Mark job as 'running'
    3. Batch-query OSV.dev for all dependencies
    4. Write CveMatch rows for each vulnerability found
    5. Update scan_jobs with final counts and status
    6. Update stack.last_scanned_at
    """
    job_uuid = uuid.UUID(job_id)

    async with AsyncSessionLocal() as db:
        return await _execute_scan(db, job_uuid)


async def _execute_scan(db: AsyncSession, job_id: uuid.UUID) -> dict:
    # Load job
    result = await db.execute(select(ScanJob).where(ScanJob.id == job_id))
    job = result.scalar_one_or_none()
    if job is None:
        logger.error("Scan job %s not found", job_id)
        return {"status": "not_found"}

    if job.status not in ("queued",):
        logger.warning("Scan job %s already in status %s, skipping", job_id, job.status)
        return {"status": "skipped"}

    # Mark running
    job.status = "running"
    job.started_at = datetime.now(timezone.utc)
    await db.commit()

    try:
        # Load dependencies
        dep_result = await db.execute(
            select(Dependency).where(Dependency.stack_id == job.stack_id)
        )
        dependencies = dep_result.scalars().all()

        if not dependencies:
            job.status = "completed"
            job.completed_at = datetime.now(timezone.utc)
            job.dependencies_scanned = 0
            job.vulnerabilities_found = 0
            await db.commit()
            return {"status": "completed", "deps": 0, "vulns": 0}

        # Process in batches
        total_vulns = 0
        total_scanned = 0

        for batch_start in range(0, len(dependencies), OSV_BATCH_SIZE):
            batch = dependencies[batch_start : batch_start + OSV_BATCH_SIZE]

            packages = [
                {"name": dep.name, "version": dep.version, "ecosystem": dep.ecosystem}
                for dep in batch
            ]

            try:
                results = await query_osv_batch(packages)
            except Exception as exc:
                logger.exception("OSV batch query failed: %s", exc)
                # Mark individual batch as failed but continue with remaining batches
                continue

            for dep, vulns in zip(batch, results):
                total_scanned += 1
                for osv_vuln in vulns:
                    parsed = parse_osv_vulnerability(osv_vuln, dep.ecosystem)
                    cve_match = CveMatch(
                        id=uuid.uuid4(),
                        dependency_id=dep.id,
                        scan_job_id=job_id,
                        **parsed,
                    )
                    db.add(cve_match)
                    total_vulns += 1

            await db.flush()

        # Update scan job
        job.status = "completed"
        job.completed_at = datetime.now(timezone.utc)
        job.dependencies_scanned = total_scanned
        job.vulnerabilities_found = total_vulns

        # Update stack.last_scanned_at
        stack_result = await db.execute(select(Stack).where(Stack.id == job.stack_id))
        stack = stack_result.scalar_one_or_none()
        if stack:
            stack.last_scanned_at = datetime.now(timezone.utc)

        await db.commit()
        logger.info(
            "Scan job %s completed: %d deps, %d vulns", job_id, total_scanned, total_vulns
        )
        return {"status": "completed", "deps": total_scanned, "vulns": total_vulns}

    except Exception as exc:
        logger.exception("Scan job %s failed: %s", job_id, exc)
        job.status = "failed"
        job.error_message = str(exc)
        job.completed_at = datetime.now(timezone.utc)
        await db.commit()
        return {"status": "failed", "error": str(exc)}


async def enqueue_scan_job(job_id: str) -> None:
    """Enqueue a scan job into the ARQ Redis queue."""
    redis = await get_redis_pool()
    await redis.enqueue_job("run_scan", job_id)


async def get_redis_pool() -> ArqRedis:
    from arq import create_pool

    return await create_pool(RedisSettings.from_dsn(settings.redis_url))


# ---------------------------------------------------------------------------
# ARQ WorkerSettings — used by `arq app.workers.scan_worker.WorkerSettings`
# ---------------------------------------------------------------------------


class WorkerSettings:
    functions = [run_scan]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = 10
    job_timeout = 300  # 5 min max per scan job
    keep_result = 3600  # keep job results in Redis for 1 hour
    retry_jobs = True
    max_tries = 3
