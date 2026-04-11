"""
Pytest configuration and shared fixtures.

Uses an in-memory SQLite database (via aiosqlite) for test isolation.
Each test gets a clean database via function-scoped fixtures.
JWT tokens are mocked — no live Supabase connection required.
"""

import uuid
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ---------------------------------------------------------------------------
# Test database setup
# ---------------------------------------------------------------------------

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    # SQLite doesn't support all Postgres types — patch models to use compatible types
    from app.database import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session


# ---------------------------------------------------------------------------
# Test data helpers
# ---------------------------------------------------------------------------

TEST_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
TEST_TEAM_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
TEST_USER_EMAIL = "test@stackr.io"

MOCK_JWT_PAYLOAD = {
    "sub": str(TEST_USER_ID),
    "email": TEST_USER_EMAIL,
    "exp": 9999999999,
    "aud": "authenticated",
}


@pytest_asyncio.fixture
async def seed_user_and_team(db_session: AsyncSession):
    """Create a test user, team, and owner membership in the test DB."""
    from app.models.models import Team, TeamMember, User

    user = User(id=TEST_USER_ID, email=TEST_USER_EMAIL, name="Test User")
    team = Team(id=TEST_TEAM_ID, name="Test Team", slug="test-team", plan="free")
    db_session.add(user)
    db_session.add(team)
    await db_session.flush()

    membership = TeamMember(
        id=uuid.uuid4(),
        team_id=TEST_TEAM_ID,
        user_id=TEST_USER_ID,
        role="owner",
    )
    db_session.add(membership)
    await db_session.commit()

    return user, team, membership


# ---------------------------------------------------------------------------
# Test client with mocked auth
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession, seed_user_and_team) -> AsyncGenerator[AsyncClient, None]:
    """
    Async test client with:
    - DB dependency overridden to use in-memory test DB
    - JWT validation mocked to return MOCK_JWT_PAYLOAD
    """
    from app.database import get_db
    from app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with patch("app.auth.dependencies._decode_supabase_jwt", return_value=MOCK_JWT_PAYLOAD):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
            headers={
                "Authorization": "Bearer fake-test-token",
                "X-Team-Id": str(TEST_TEAM_ID),
            },
        ) as client:
            yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client_no_team(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Test client without team header — for testing missing-header errors."""
    from app.database import get_db
    from app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with patch("app.auth.dependencies._decode_supabase_jwt", return_value=MOCK_JWT_PAYLOAD):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
            headers={"Authorization": "Bearer fake-test-token"},
        ) as client:
            yield client

    app.dependency_overrides.clear()
