"""
Vulnerabilities router — /stacks/{stack_id}/vulnerabilities

Returns CVE matches for a stack, filtered to the latest scan job.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import AuthDep
from app.database import get_db
from app.models.models import CveMatch, Dependency, ScanJob, Stack
from app.schemas.schemas import CveMatchOut

router = APIRouter(tags=["vulnerabilities"])


@router.get("/stacks/{stack_id}/vulnerabilities", response_model=list[CveMatchOut])
async def list_stack_vulnerabilities(
    stack_id: uuid.UUID,
    auth: AuthDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    severity: str | None = Query(None, description="Filter by severity: CRITICAL, HIGH, MEDIUM, LOW"),
    latest_only: bool = Query(True, description="Only return results from the most recent completed scan"),
) -> list[CveMatchOut]:
    """
    Return CVE matches for all dependencies in a stack.

    By default returns only the latest completed scan's results to avoid
    showing stale/superseded CVE data (magnus F4).
    """
    # Verify stack belongs to team
    stack_result = await db.execute(
        select(Stack).where(Stack.id == stack_id, Stack.team_id == auth.team_id)
    )
    if stack_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stack not found")

    query = (
        select(CveMatch)
        .join(Dependency, Dependency.id == CveMatch.dependency_id)
        .where(Dependency.stack_id == stack_id)
    )

    if latest_only:
        # Find the most recent completed scan job for this stack
        latest_scan = await db.execute(
            select(ScanJob.id)
            .where(ScanJob.stack_id == stack_id, ScanJob.status == "completed")
            .order_by(ScanJob.completed_at.desc())
            .limit(1)
        )
        scan_id = latest_scan.scalar_one_or_none()
        if scan_id is None:
            return []
        query = query.where(CveMatch.scan_job_id == scan_id)

    if severity:
        query = query.where(CveMatch.severity == severity.upper())

    # Sort by cvss_score descending (numeric sort — bjorn's fix for text type)
    query = query.order_by(CveMatch.cvss_score.desc().nullslast())

    result = await db.execute(query)
    cves = result.scalars().all()
    return [CveMatchOut.model_validate(c) for c in cves]
