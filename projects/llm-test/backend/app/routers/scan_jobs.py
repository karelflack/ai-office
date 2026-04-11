"""
Scan jobs router — /stacks/{stack_id}/scan, /scan-jobs/{job_id}

Enqueues vulnerability scan jobs via ARQ (Redis). Creates a scan_jobs record
before enqueueing so recovery is possible if Redis is temporarily unavailable.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import AuthDep
from app.database import get_db
from app.models.models import ScanJob, Stack
from app.schemas.schemas import ScanJobOut
from app.services.audit import get_client_ip, log_event

router = APIRouter(tags=["scan_jobs"])


@router.post(
    "/stacks/{stack_id}/scan",
    response_model=ScanJobOut,
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_scan(
    stack_id: uuid.UUID,
    auth: AuthDep,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ScanJobOut:
    """
    Enqueue a vulnerability scan job for a stack.

    Creates a scan_jobs record with status='queued' before enqueueing
    so that orphaned jobs can be recovered if Redis is unavailable (bjorn ADR 4.3).
    Returns the job ID — client should poll GET /scan-jobs/{job_id} for progress.
    """
    # Verify stack belongs to team
    stack_result = await db.execute(
        select(Stack).where(Stack.id == stack_id, Stack.team_id == auth.team_id)
    )
    stack = stack_result.scalar_one_or_none()
    if stack is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stack not found")

    # Create job record first (recovery safety net)
    job = ScanJob(
        id=uuid.uuid4(),
        stack_id=stack_id,
        triggered_by=auth.user_id,
        status="queued",
    )
    db.add(job)

    await log_event(
        db,
        action="scan_triggered",
        resource_type="scan",
        resource_id=job.id,
        team_id=auth.team_id,
        actor_user_id=auth.user_id,
        actor_ip=get_client_ip(dict(request.headers)),
        metadata={"stack_id": str(stack_id)},
    )
    await db.commit()
    await db.refresh(job)

    # Enqueue the ARQ job (best-effort — job record already persisted above)
    try:
        from app.workers.scan_worker import enqueue_scan_job
        await enqueue_scan_job(str(job.id))
    except Exception:
        # Redis unavailable — job remains as 'queued' in DB for recovery
        # Log but do not fail the request; client can still poll status
        import logging
        logging.getLogger(__name__).warning(
            "Failed to enqueue scan job %s — Redis may be unavailable. "
            "Job persisted in DB for recovery.",
            job.id,
        )

    return ScanJobOut.model_validate(job)


@router.get("/scan-jobs/{job_id}", response_model=ScanJobOut)
async def get_scan_job(
    job_id: uuid.UUID,
    auth: AuthDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ScanJobOut:
    """
    Poll scan job status. Returns current status, progress counters, and
    error details if the job failed. Frontend polls this every ~3s while
    status is 'queued' or 'running' (ingrid guideline from bjorn architecture).
    """
    result = await db.execute(
        select(ScanJob)
        .join(Stack, Stack.id == ScanJob.stack_id)
        .where(ScanJob.id == job_id, Stack.team_id == auth.team_id)
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan job not found")

    return ScanJobOut.model_validate(job)
