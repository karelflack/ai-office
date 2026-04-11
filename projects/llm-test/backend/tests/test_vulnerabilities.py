"""Tests for /stacks/{stack_id}/vulnerabilities and /dependencies/{dep_id}/cves."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import TEST_TEAM_ID


async def _setup_stack_with_scan(db_session: AsyncSession, async_client: AsyncClient):
    """Create a stack with a dependency and completed scan + CVE matches."""
    from app.models.models import CveMatch, Dependency, ScanJob, Stack

    stack = Stack(
        id=uuid.uuid4(),
        team_id=TEST_TEAM_ID,
        name="Vulnerable Stack",
        ecosystem="npm",
    )
    db_session.add(stack)
    await db_session.flush()

    dep = Dependency(
        id=uuid.uuid4(),
        stack_id=stack.id,
        name="lodash",
        version="4.17.20",
        ecosystem="npm",
    )
    db_session.add(dep)
    await db_session.flush()

    job = ScanJob(
        id=uuid.uuid4(),
        stack_id=stack.id,
        triggered_by=None,
        status="completed",
        dependencies_scanned=1,
        vulnerabilities_found=1,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
    )
    db_session.add(job)
    await db_session.flush()

    cve = CveMatch(
        id=uuid.uuid4(),
        dependency_id=dep.id,
        scan_job_id=job.id,
        osv_id="GHSA-1234-5678-xxxx",
        cve_id="CVE-2021-23337",
        severity="HIGH",
        cvss_score=Decimal("7.2"),
        summary="Prototype pollution in lodash",
        fixed_in_version="4.17.21",
    )
    db_session.add(cve)
    await db_session.commit()

    return stack, dep, job, cve


@pytest.mark.asyncio
async def test_list_vulnerabilities_latest_scan(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    stack, dep, job, cve = await _setup_stack_with_scan(db_session, async_client)
    response = await async_client.get(f"/stacks/{stack.id}/vulnerabilities")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["osv_id"] == "GHSA-1234-5678-xxxx"
    assert data[0]["severity"] == "HIGH"
    assert data[0]["cve_id"] == "CVE-2021-23337"


@pytest.mark.asyncio
async def test_list_vulnerabilities_severity_filter(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    stack, dep, job, cve = await _setup_stack_with_scan(db_session, async_client)

    # Filter for CRITICAL — should return empty
    response = await async_client.get(f"/stacks/{stack.id}/vulnerabilities?severity=CRITICAL")
    assert response.status_code == 200
    assert response.json() == []

    # Filter for HIGH — should return the CVE
    response = await async_client.get(f"/stacks/{stack.id}/vulnerabilities?severity=HIGH")
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_list_vulnerabilities_no_scan(async_client: AsyncClient) -> None:
    """Stack with no completed scan should return empty list."""
    create_resp = await async_client.post("/stacks", json={"name": "Clean Stack", "ecosystem": "npm"})
    stack_id = create_resp.json()["id"]

    response = await async_client.get(f"/stacks/{stack_id}/vulnerabilities")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_dependency_cves(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    stack, dep, job, cve = await _setup_stack_with_scan(db_session, async_client)
    response = await async_client.get(f"/dependencies/{dep.id}/cves")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["cve_id"] == "CVE-2021-23337"


@pytest.mark.asyncio
async def test_get_cves_unknown_dependency(async_client: AsyncClient) -> None:
    response = await async_client.get(f"/dependencies/{uuid.uuid4()}/cves")
    assert response.status_code == 404
