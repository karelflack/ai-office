"""
pytest tests for the joke REST API.
Upstream: projects/auto-dispatch-test/output/2026-04-06-system-architecture.md (bjorn)

Run with: pytest tests/test_jokes.py -v
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

JOKE_FIELDS = {"id", "setup", "punchline", "category"}


# ---------------------------------------------------------------------------
# GET /jokes/random
# ---------------------------------------------------------------------------

class TestRandomJoke:
    def test_status_200(self):
        response = client.get("/jokes/random")
        assert response.status_code == 200

    def test_response_is_json(self):
        response = client.get("/jokes/random")
        assert response.headers["content-type"].startswith("application/json")

    def test_schema_has_all_fields(self):
        data = client.get("/jokes/random").json()
        assert JOKE_FIELDS.issubset(data.keys())

    def test_id_is_integer(self):
        data = client.get("/jokes/random").json()
        assert isinstance(data["id"], int)

    def test_setup_is_non_empty_string(self):
        data = client.get("/jokes/random").json()
        assert isinstance(data["setup"], str)
        assert len(data["setup"]) > 0

    def test_punchline_is_non_empty_string(self):
        data = client.get("/jokes/random").json()
        assert isinstance(data["punchline"], str)
        assert len(data["punchline"]) > 0

    def test_category_is_non_empty_string(self):
        data = client.get("/jokes/random").json()
        assert isinstance(data["category"], str)
        assert len(data["category"]) > 0

    def test_no_extra_fields(self):
        data = client.get("/jokes/random").json()
        assert set(data.keys()) == JOKE_FIELDS

    def test_returns_different_jokes_over_multiple_calls(self):
        """With 30 jokes in the dataset, 20 calls should not all be identical."""
        ids = {client.get("/jokes/random").json()["id"] for _ in range(20)}
        assert len(ids) > 1

    def test_id_within_known_range(self):
        data = client.get("/jokes/random").json()
        assert 1 <= data["id"] <= 30

    def test_category_is_known_value(self):
        known_categories = {
            "science", "general", "food", "animals", "sports", "technology"
        }
        data = client.get("/jokes/random").json()
        assert data["category"] in known_categories


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_status_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_response_body(self):
        data = client.get("/health").json()
        assert data == {"status": "ok"}

    def test_response_is_json(self):
        response = client.get("/health")
        assert response.headers["content-type"].startswith("application/json")


# ---------------------------------------------------------------------------
# 404 for unknown routes
# ---------------------------------------------------------------------------

class TestUnknownRoutes:
    def test_unknown_route_returns_404(self):
        response = client.get("/does-not-exist")
        assert response.status_code == 404

    def test_post_to_random_returns_405(self):
        response = client.post("/jokes/random")
        assert response.status_code == 405
