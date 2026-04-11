"""Tests for /stacks/{stack_id}/dependencies endpoints."""

import uuid

import pytest
from httpx import AsyncClient


async def _create_stack(client: AsyncClient, name: str = "Test Stack") -> str:
    resp = await client.post("/stacks", json={"name": name, "ecosystem": "npm"})
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_list_dependencies_empty(async_client: AsyncClient) -> None:
    stack_id = await _create_stack(async_client)
    response = await async_client.get(f"/stacks/{stack_id}/dependencies")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_add_dependency(async_client: AsyncClient) -> None:
    stack_id = await _create_stack(async_client)
    payload = {
        "name": "express",
        "version": "4.18.2",
        "ecosystem": "npm",
        "is_dev_dependency": False,
    }
    response = await async_client.post(f"/stacks/{stack_id}/dependencies", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "express"
    assert data["version"] == "4.18.2"
    assert data["stack_id"] == stack_id


@pytest.mark.asyncio
async def test_list_dependencies(async_client: AsyncClient) -> None:
    stack_id = await _create_stack(async_client)
    await async_client.post(
        f"/stacks/{stack_id}/dependencies",
        json={"name": "react", "version": "18.2.0", "ecosystem": "npm"},
    )
    await async_client.post(
        f"/stacks/{stack_id}/dependencies",
        json={"name": "typescript", "version": "5.0.0", "ecosystem": "npm", "is_dev_dependency": True},
    )

    response = await async_client.get(f"/stacks/{stack_id}/dependencies")
    assert response.status_code == 200
    names = [d["name"] for d in response.json()]
    assert "react" in names
    assert "typescript" in names


@pytest.mark.asyncio
async def test_remove_dependency(async_client: AsyncClient) -> None:
    stack_id = await _create_stack(async_client)
    add_resp = await async_client.post(
        f"/stacks/{stack_id}/dependencies",
        json={"name": "lodash", "version": "4.17.21", "ecosystem": "npm"},
    )
    dep_id = add_resp.json()["id"]

    del_resp = await async_client.delete(f"/stacks/{stack_id}/dependencies/{dep_id}")
    assert del_resp.status_code == 200

    list_resp = await async_client.get(f"/stacks/{stack_id}/dependencies")
    assert all(d["id"] != dep_id for d in list_resp.json())


@pytest.mark.asyncio
async def test_remove_nonexistent_dependency(async_client: AsyncClient) -> None:
    stack_id = await _create_stack(async_client)
    response = await async_client.delete(f"/stacks/{stack_id}/dependencies/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_dependency_on_nonexistent_stack(async_client: AsyncClient) -> None:
    fake_stack_id = str(uuid.uuid4())
    response = await async_client.get(f"/stacks/{fake_stack_id}/dependencies")
    assert response.status_code == 404
