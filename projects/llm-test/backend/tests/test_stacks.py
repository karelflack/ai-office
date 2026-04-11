"""Tests for /stacks endpoints."""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_stacks_empty(async_client: AsyncClient) -> None:
    response = await async_client.get("/stacks")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_stack(async_client: AsyncClient) -> None:
    payload = {
        "name": "My API",
        "description": "Backend services",
        "ecosystem": "npm",
    }
    response = await async_client.post("/stacks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My API"
    assert data["ecosystem"] == "npm"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_and_list_stack(async_client: AsyncClient) -> None:
    await async_client.post("/stacks", json={"name": "Stack A", "ecosystem": "pypi"})
    await async_client.post("/stacks", json={"name": "Stack B", "ecosystem": "go"})

    response = await async_client.get("/stacks")
    assert response.status_code == 200
    names = [s["name"] for s in response.json()]
    assert "Stack A" in names
    assert "Stack B" in names


@pytest.mark.asyncio
async def test_get_stack(async_client: AsyncClient) -> None:
    create_resp = await async_client.post("/stacks", json={"name": "Detailed Stack"})
    stack_id = create_resp.json()["id"]

    get_resp = await async_client.get(f"/stacks/{stack_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == stack_id


@pytest.mark.asyncio
async def test_get_nonexistent_stack_returns_404(async_client: AsyncClient) -> None:
    response = await async_client.get(f"/stacks/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_stack(async_client: AsyncClient) -> None:
    create_resp = await async_client.post("/stacks", json={"name": "Old Name"})
    stack_id = create_resp.json()["id"]

    patch_resp = await async_client.patch(
        f"/stacks/{stack_id}", json={"name": "New Name", "description": "Updated"}
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["name"] == "New Name"
    assert patch_resp.json()["description"] == "Updated"


@pytest.mark.asyncio
async def test_delete_stack(async_client: AsyncClient) -> None:
    create_resp = await async_client.post("/stacks", json={"name": "To Delete"})
    stack_id = create_resp.json()["id"]

    del_resp = await async_client.delete(f"/stacks/{stack_id}")
    assert del_resp.status_code == 200

    get_resp = await async_client.get(f"/stacks/{stack_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_invalid_ecosystem_rejected(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/stacks", json={"name": "Bad Stack", "ecosystem": "invalid_ecosystem"}
    )
    assert response.status_code == 422
