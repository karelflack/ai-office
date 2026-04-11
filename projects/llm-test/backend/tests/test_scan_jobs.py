"""Tests for /stacks/{stack_id}/scan and /scan-jobs/{job_id} endpoints."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_trigger_scan_creates_job(async_client: AsyncClient) -> None:
    """Triggering a scan should create a queued scan job and return 202."""
    create_resp = await async_client.post("/stacks", json={"name": "Scan Target"})
    assert create_resp.status_code == 201
    stack_id = create_resp.json()["id"]

    with patch("app.routers.scan_jobs.enqueue_scan_job", new_callable=AsyncMock):
        scan_resp = await async_client.post(f"/stacks/{stack_id}/scan")

    assert scan_resp.status_code == 202
    job = scan_resp.json()
    assert job["status"] == "queued"
    assert job["stack_id"] == stack_id
    assert "id" in job


@pytest.mark.asyncio
async def test_poll_scan_job(async_client: AsyncClient) -> None:
    """Polling a scan job by ID should return current status."""
    create_resp = await async_client.post("/stacks", json={"name": "Poll Target"})
    stack_id = create_resp.json()["id"]

    with patch("app.routers.scan_jobs.enqueue_scan_job", new_callable=AsyncMock):
        scan_resp = await async_client.post(f"/stacks/{stack_id}/scan")

    job_id = scan_resp.json()["id"]
    poll_resp = await async_client.get(f"/scan-jobs/{job_id}")
    assert poll_resp.status_code == 200
    assert poll_resp.json()["id"] == job_id
    assert poll_resp.json()["status"] == "queued"


@pytest.mark.asyncio
async def test_scan_nonexistent_stack(async_client: AsyncClient) -> None:
    """Triggering a scan on a non-existent stack should return 404."""
    response = await async_client.post(f"/stacks/{uuid.uuid4()}/scan")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_poll_nonexistent_job(async_client: AsyncClient) -> None:
    """Polling a non-existent job should return 404."""
    response = await async_client.get(f"/scan-jobs/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_scan_enqueue_failure_still_returns_202(async_client: AsyncClient) -> None:
    """If Redis is unavailable, the job should still be created (queued in DB)."""
    create_resp = await async_client.post("/stacks", json={"name": "Redis Down Stack"})
    stack_id = create_resp.json()["id"]

    with patch(
        "app.routers.scan_jobs.enqueue_scan_job",
        side_effect=Exception("Redis unavailable"),
    ):
        scan_resp = await async_client.post(f"/stacks/{stack_id}/scan")

    # Should still return 202 — job is persisted in DB for recovery
    assert scan_resp.status_code == 202
    assert scan_resp.json()["status"] == "queued"
