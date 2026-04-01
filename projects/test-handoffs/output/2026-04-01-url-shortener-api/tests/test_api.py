import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app, follow_redirects=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def register_user(email: str = "user@example.com", password: str = "secret123") -> str:
    """Register a user and return the access token."""
    resp = client.post("/register", json={"email": email, "password": password})
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Original tests (unauthenticated shorten still works)
# ---------------------------------------------------------------------------

def test_shorten_url():
    resp = client.post("/shorten", json={"url": "https://example.com/some/long/path"})
    assert resp.status_code == 201
    data = resp.json()
    assert "code" in data
    assert data["original_url"] == "https://example.com/some/long/path"
    assert data["code"] in data["short_url"]
    # Anonymous links have no owner
    assert data["owner_id"] is None


def test_shorten_custom_code():
    resp = client.post("/shorten", json={"url": "https://example.com", "custom_code": "mycode"})
    assert resp.status_code == 201
    assert resp.json()["code"] == "mycode"


def test_shorten_duplicate_custom_code():
    client.post("/shorten", json={"url": "https://example.com", "custom_code": "dup"})
    resp = client.post("/shorten", json={"url": "https://other.com", "custom_code": "dup"})
    assert resp.status_code == 409


def test_redirect():
    code = client.post("/shorten", json={"url": "https://example.com"}).json()["code"]
    resp = client.get(f"/{code}")
    assert resp.status_code == 302
    assert resp.headers["location"] in ("https://example.com", "https://example.com/")


def test_redirect_not_found():
    resp = client.get("/nonexistent")
    assert resp.status_code == 404


def test_stats_zero_clicks():
    code = client.post("/shorten", json={"url": "https://example.com"}).json()["code"]
    resp = client.get(f"/{code}/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_clicks"] == 0
    assert data["recent_clicks"] == []


def test_stats_after_clicks():
    code = client.post("/shorten", json={"url": "https://example.com"}).json()["code"]
    client.get(f"/{code}")
    client.get(f"/{code}")
    resp = client.get(f"/{code}/stats")
    assert resp.json()["total_clicks"] == 2


# ---------------------------------------------------------------------------
# DELETE now requires auth — update the original delete tests
# ---------------------------------------------------------------------------

def test_delete():
    token = register_user()
    code = client.post("/shorten", json={"url": "https://example.com"}).json()["code"]
    # Anonymous link — any authenticated user can delete it
    resp = client.delete(f"/{code}", headers=auth_headers(token))
    assert resp.status_code == 204
    assert client.get(f"/{code}").status_code == 404


def test_delete_not_found():
    token = register_user()
    resp = client.delete("/ghost", headers=auth_headers(token))
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Auth tests
# ---------------------------------------------------------------------------

def test_register_new_user():
    resp = client.post("/register", json={"email": "alice@example.com", "password": "pass1234"})
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email():
    client.post("/register", json={"email": "bob@example.com", "password": "pass1234"})
    resp = client.post("/register", json={"email": "bob@example.com", "password": "other"})
    assert resp.status_code == 409


def test_login_valid_credentials():
    client.post("/register", json={"email": "carol@example.com", "password": "mypassword"})
    resp = client.post("/login", data={"username": "carol@example.com", "password": "mypassword"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password():
    client.post("/register", json={"email": "dave@example.com", "password": "correct"})
    resp = client.post("/login", data={"username": "dave@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_login_unknown_user():
    resp = client.post("/login", data={"username": "nobody@example.com", "password": "pass"})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Shorten as authenticated user — link is owned
# ---------------------------------------------------------------------------

def test_shorten_authenticated_sets_owner():
    token = register_user("owner@example.com")
    resp = client.post(
        "/shorten",
        json={"url": "https://example.com/owned"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["owner_id"] is not None


# ---------------------------------------------------------------------------
# GET /me/links
# ---------------------------------------------------------------------------

def test_me_links_returns_owned_links():
    token = register_user("me@example.com")
    client.post("/shorten", json={"url": "https://a.com"}, headers=auth_headers(token))
    client.post("/shorten", json={"url": "https://b.com"}, headers=auth_headers(token))
    # Create an anonymous link — should NOT appear in /me/links
    client.post("/shorten", json={"url": "https://anon.com"})

    resp = client.get("/me/links", headers=auth_headers(token))
    assert resp.status_code == 200
    links = resp.json()
    assert len(links) == 2
    urls = {l["original_url"] for l in links}
    assert urls == {"https://a.com/", "https://b.com/"}


def test_me_links_requires_auth():
    resp = client.get("/me/links")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# DELETE ownership enforcement
# ---------------------------------------------------------------------------

def test_delete_own_link():
    token = register_user("del_owner@example.com")
    code = client.post(
        "/shorten",
        json={"url": "https://example.com/owned"},
        headers=auth_headers(token),
    ).json()["code"]
    resp = client.delete(f"/{code}", headers=auth_headers(token))
    assert resp.status_code == 204


def test_delete_other_users_link_is_403():
    token_a = register_user("user_a@example.com")
    token_b = register_user("user_b@example.com")
    # User A creates a link
    code = client.post(
        "/shorten",
        json={"url": "https://example.com/user-a"},
        headers=auth_headers(token_a),
    ).json()["code"]
    # User B tries to delete it
    resp = client.delete(f"/{code}", headers=auth_headers(token_b))
    assert resp.status_code == 403


def test_delete_requires_auth():
    code = client.post("/shorten", json={"url": "https://example.com"}).json()["code"]
    resp = client.delete(f"/{code}")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# /auth/* router — register, login, refresh, me
# ---------------------------------------------------------------------------

def test_auth_register_returns_both_tokens():
    resp = client.post("/auth/register", json={"email": "auth_reg@example.com", "password": "pass1234"})
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_auth_register_duplicate_returns_409():
    client.post("/auth/register", json={"email": "dup_auth@example.com", "password": "pass"})
    resp = client.post("/auth/register", json={"email": "dup_auth@example.com", "password": "pass"})
    assert resp.status_code == 409


def test_auth_login_valid_credentials():
    client.post("/auth/register", json={"email": "auth_login@example.com", "password": "secret"})
    resp = client.post("/auth/login", data={"username": "auth_login@example.com", "password": "secret"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_auth_login_wrong_password_is_401():
    client.post("/auth/register", json={"email": "auth_bad@example.com", "password": "correct"})
    resp = client.post("/auth/login", data={"username": "auth_bad@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_auth_login_unknown_user_is_401():
    resp = client.post("/auth/login", data={"username": "ghost@example.com", "password": "x"})
    assert resp.status_code == 401


def test_auth_me_returns_user_profile():
    resp = client.post("/auth/register", json={"email": "auth_me@example.com", "password": "pass"})
    token = resp.json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    data = me.json()
    assert data["email"] == "auth_me@example.com"
    assert "id" in data
    assert "created_at" in data


def test_auth_me_requires_auth():
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_auth_refresh_issues_new_tokens():
    reg = client.post("/auth/register", json={"email": "auth_refresh@example.com", "password": "pass"})
    refresh_token = reg.json()["refresh_token"]

    resp = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # Verify the new access token actually works for a protected endpoint
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {data['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "auth_refresh@example.com"


def test_auth_refresh_with_invalid_token_is_401():
    resp = client.post("/auth/refresh", json={"refresh_token": "not.a.valid.token"})
    assert resp.status_code == 401


def test_auth_refresh_token_rejected_as_access_token():
    """A refresh token must not be accepted where an access token is required."""
    reg = client.post("/auth/register", json={"email": "auth_rt_check@example.com", "password": "pass"})
    refresh_token = reg.json()["refresh_token"]

    # Attempt to use the refresh token to hit a protected endpoint
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {refresh_token}"})
    assert resp.status_code == 401


def test_token_response_includes_refresh_token_on_legacy_register():
    """Legacy /register endpoint must also return a refresh_token field."""
    resp = client.post("/register", json={"email": "legacy_rt@example.com", "password": "pass"})
    assert resp.status_code == 201
    assert "refresh_token" in resp.json()


def test_token_response_includes_refresh_token_on_legacy_login():
    """Legacy /login endpoint must also return a refresh_token field."""
    client.post("/register", json={"email": "legacy_login@example.com", "password": "pass"})
    resp = client.post("/login", data={"username": "legacy_login@example.com", "password": "pass"})
    assert resp.status_code == 200
    assert "refresh_token" in resp.json()
