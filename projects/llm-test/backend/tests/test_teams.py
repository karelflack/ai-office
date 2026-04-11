"""Tests for /teams endpoints."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import TEST_TEAM_ID, TEST_USER_ID


@pytest.mark.asyncio
async def test_get_team(async_client: AsyncClient) -> None:
    response = await async_client.get(f"/teams/{TEST_TEAM_ID}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(TEST_TEAM_ID)
    assert data["slug"] == "test-team"


@pytest.mark.asyncio
async def test_get_nonexistent_team(async_client: AsyncClient) -> None:
    response = await async_client.get(f"/teams/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_members(async_client: AsyncClient) -> None:
    response = await async_client.get(f"/teams/{TEST_TEAM_ID}/members")
    assert response.status_code == 200
    members = response.json()
    assert len(members) >= 1
    assert any(m["user_id"] == str(TEST_USER_ID) for m in members)


@pytest.mark.asyncio
async def test_invite_unknown_user(async_client: AsyncClient) -> None:
    """Inviting a user who doesn't exist should return 404."""
    response = await async_client.post(
        f"/teams/{TEST_TEAM_ID}/invite",
        json={"email": "unknown@example.com", "role": "member"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_invite_existing_member(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Inviting an existing member should return 409."""
    # The test user is already a member (owner) — try to invite them again
    from app.models.models import User

    # invite test user by email (they already exist as owner)
    response = await async_client.post(
        f"/teams/{TEST_TEAM_ID}/invite",
        json={"email": "test@stackr.io", "role": "member"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_team(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/teams", json={"name": "New Team", "slug": "new-team-xyz", "plan": "free"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == "new-team-xyz"


@pytest.mark.asyncio
async def test_create_team_duplicate_slug(async_client: AsyncClient) -> None:
    """Creating a team with an existing slug should return 409."""
    response = await async_client.post(
        "/teams", json={"name": "Dupe Team", "slug": "test-team", "plan": "free"}
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_remove_self_from_team_blocked(async_client: AsyncClient) -> None:
    """Users cannot remove themselves from a team."""
    response = await async_client.delete(
        f"/teams/{TEST_TEAM_ID}/members/{TEST_USER_ID}"
    )
    assert response.status_code == 400
