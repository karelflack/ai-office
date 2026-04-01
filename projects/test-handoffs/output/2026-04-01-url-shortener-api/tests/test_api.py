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


def test_shorten_url():
    resp = client.post("/shorten", json={"url": "https://example.com/some/long/path"})
    assert resp.status_code == 201
    data = resp.json()
    assert "code" in data
    assert data["original_url"] == "https://example.com/some/long/path"
    assert data["code"] in data["short_url"]


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


def test_delete():
    code = client.post("/shorten", json={"url": "https://example.com"}).json()["code"]
    resp = client.delete(f"/{code}")
    assert resp.status_code == 204
    assert client.get(f"/{code}").status_code == 404


def test_delete_not_found():
    resp = client.delete("/ghost")
    assert resp.status_code == 404
