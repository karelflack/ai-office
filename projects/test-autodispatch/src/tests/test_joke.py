"""Tests for the joke API.

Unit tests cover service-layer logic directly.
Integration tests use FastAPI's TestClient to exercise the full HTTP stack.
"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_JOKES = [
    {"id": 1, "setup": "Setup one", "punchline": "Punchline one", "category": "general"},
    {"id": 2, "setup": "Setup two", "punchline": "Punchline two", "category": "science"},
    {"id": 3, "setup": "Setup three", "punchline": "Punchline three", "category": "general"},
]


@pytest.fixture(autouse=True)
def reset_service():
    """Reset service module state between tests."""
    import services.joke_service as svc
    original_jokes = svc._jokes[:]
    original_index = dict(svc._index)
    yield
    svc._jokes = original_jokes
    svc._index = original_index


@pytest.fixture()
def loaded_service(tmp_path):
    """Load sample jokes into the service via a temp file."""
    import services.joke_service as svc
    jokes_file = tmp_path / "jokes.json"
    jokes_file.write_text(json.dumps(SAMPLE_JOKES))
    svc.load_jokes(path=jokes_file)
    return svc


@pytest.fixture()
def client(loaded_service):
    """TestClient with jokes already loaded."""
    from main import app
    return TestClient(app)


# ---------------------------------------------------------------------------
# Unit tests — service layer
# ---------------------------------------------------------------------------


class TestLoadJokes:
    def test_loads_valid_file(self, loaded_service):
        assert len(loaded_service._jokes) == 3

    def test_builds_index(self, loaded_service):
        assert loaded_service._index[1]["setup"] == "Setup one"
        assert loaded_service._index[2]["setup"] == "Setup two"

    def test_raises_on_empty_list(self, tmp_path):
        import services.joke_service as svc
        empty_file = tmp_path / "empty.json"
        empty_file.write_text("[]")
        with pytest.raises(ValueError):
            svc.load_jokes(path=empty_file)

    def test_raises_on_missing_file(self):
        import services.joke_service as svc
        with pytest.raises(FileNotFoundError):
            svc.load_jokes(path=Path("/nonexistent/jokes.json"))


class TestGetRandomJoke:
    def test_returns_a_joke(self, loaded_service):
        joke = loaded_service.get_random_joke()
        assert joke is not None
        assert joke["id"] in {1, 2, 3}

    def test_returns_none_when_empty(self):
        import services.joke_service as svc
        svc._jokes = []
        assert svc.get_random_joke() is None

    def test_random_choice_used(self, loaded_service):
        with patch("services.joke_service.random.choice", return_value=SAMPLE_JOKES[0]) as mock_choice:
            result = loaded_service.get_random_joke()
        mock_choice.assert_called_once()
        assert result["id"] == 1


class TestGetJokeById:
    def test_returns_correct_joke(self, loaded_service):
        joke = loaded_service.get_joke_by_id(2)
        assert joke["setup"] == "Setup two"

    def test_returns_none_for_missing_id(self, loaded_service):
        assert loaded_service.get_joke_by_id(999) is None


class TestGetAllJokes:
    def test_returns_all_without_filter(self, loaded_service):
        jokes = loaded_service.get_all_jokes()
        assert len(jokes) == 3

    def test_filters_by_category(self, loaded_service):
        jokes = loaded_service.get_all_jokes(category="general")
        assert len(jokes) == 2
        assert all(j["category"] == "general" for j in jokes)

    def test_filter_is_case_insensitive(self, loaded_service):
        jokes = loaded_service.get_all_jokes(category="SCIENCE")
        assert len(jokes) == 1

    def test_returns_empty_list_for_unknown_category(self, loaded_service):
        jokes = loaded_service.get_all_jokes(category="unknown")
        assert jokes == []


# ---------------------------------------------------------------------------
# Integration tests — HTTP endpoints
# ---------------------------------------------------------------------------


class TestGetRandomJokeEndpoint:
    def test_returns_200(self, client):
        resp = client.get("/joke")
        assert resp.status_code == 200

    def test_response_shape(self, client):
        resp = client.get("/joke")
        body = resp.json()
        assert {"id", "setup", "punchline", "category"} == set(body.keys())
        assert isinstance(body["id"], int)

    def test_returns_500_when_no_jokes(self, client):
        import services.joke_service as svc
        svc._jokes = []
        resp = client.get("/joke")
        assert resp.status_code == 500
        assert resp.json()["detail"] == "Joke source unavailable."


class TestGetJokeByIdEndpoint:
    def test_returns_correct_joke(self, client):
        resp = client.get("/joke/1")
        assert resp.status_code == 200
        assert resp.json()["id"] == 1

    def test_returns_404_for_unknown_id(self, client):
        resp = client.get("/joke/999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Joke not found."

    def test_returns_422_for_non_integer_id(self, client):
        resp = client.get("/joke/abc")
        assert resp.status_code == 422


class TestGetJokesListEndpoint:
    def test_returns_all_jokes(self, client):
        resp = client.get("/jokes")
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_filters_by_category(self, client):
        resp = client.get("/jokes?category=general")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_empty_list_for_unknown_category(self, client):
        resp = client.get("/jokes?category=nonsense")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_each_joke_has_required_fields(self, client):
        resp = client.get("/jokes")
        for joke in resp.json():
            assert {"id", "setup", "punchline", "category"} == set(joke.keys())


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
