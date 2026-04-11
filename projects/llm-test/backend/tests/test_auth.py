"""Tests for /auth endpoints."""

import uuid
from unittest.mock import patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient) -> None:
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_get_me_returns_user(async_client: AsyncClient) -> None:
    response = await async_client.get("/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@stackr.io"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_me_without_auth_fails(async_client: AsyncClient) -> None:
    """Requests without Authorization header should be rejected."""
    response = await async_client.get("/auth/me", headers={"Authorization": ""})
    # HTTPBearer with auto_error=True returns 403 on missing/invalid scheme
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_missing_team_header_rejected(async_client_no_team: AsyncClient) -> None:
    """Requests without X-Team-Id header should be rejected with 400."""
    response = await async_client_no_team.get("/stacks")
    assert response.status_code == 400
    assert "X-Team-Id" in response.json()["detail"]


@pytest.mark.asyncio
async def test_exchange_token(db_session, seed_user_and_team) -> None:
    """POST /auth/token should return user ID and team IDs."""
    from app.database import get_db
    from app.main import app
    from httpx import ASGITransport, AsyncClient
    from tests.conftest import MOCK_JWT_PAYLOAD, TEST_TEAM_ID, TEST_USER_ID

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with patch("app.auth.dependencies._decode_supabase_jwt", return_value=MOCK_JWT_PAYLOAD):
        with patch("app.auth.router._decode_supabase_jwt", return_value=MOCK_JWT_PAYLOAD):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://testserver"
            ) as client:
                response = await client.post(
                    "/auth/token",
                    json={"supabase_access_token": "fake-valid-token"},
                )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(TEST_USER_ID)
    assert str(TEST_TEAM_ID) in data["team_ids"]
