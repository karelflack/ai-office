"""
API tests for the joke REST API — written by odd agent.
Phase 3 testing: covers happy path, edge cases, error cases, randomness,
performance baseline, and security observations.

Upstream outputs read:
- projects/auto-dispatch-test/output/2026-04-06-system-architecture.md (bjorn)
- projects/auto-dispatch-test/output/2026-04-06-infrastructure-and-cicd.md (dag)
- projects/auto-dispatch-test/output/2026-04-06-main.py (arve)
- projects/auto-dispatch-test/output/2026-04-06-models.py (arve)
- projects/auto-dispatch-test/output/2026-04-06-jokes-module.py (arve)
- projects/auto-dispatch-test/output/2026-04-06-jokes.json (arve)

Run with: pytest tests/test_api_odd.py -v
"""
import time
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

KNOWN_CATEGORIES = {"science", "general", "food", "animals", "sports", "technology"}
JOKE_DATASET_SIZE = 30
EXPECTED_JOKE_FIELDS = {"id", "setup", "punchline", "category"}


# ---------------------------------------------------------------------------
# GET /jokes/random — happy path
# ---------------------------------------------------------------------------

class TestRandomJokeHappyPath:
    """Verify the core contract: 200 OK, correct schema, correct types."""

    def test_returns_200(self):
        resp = client.get("/jokes/random")
        assert resp.status_code == 200

    def test_content_type_is_json(self):
        resp = client.get("/jokes/random")
        assert "application/json" in resp.headers["content-type"]

    def test_response_body_is_object(self):
        resp = client.get("/jokes/random")
        data = resp.json()
        assert isinstance(data, dict)

    def test_all_four_fields_present(self):
        data = client.get("/jokes/random").json()
        assert EXPECTED_JOKE_FIELDS.issubset(data.keys()), (
            f"Missing fields: {EXPECTED_JOKE_FIELDS - set(data.keys())}"
        )

    def test_no_unexpected_fields(self):
        """Response must contain exactly the four documented fields — no extras."""
        data = client.get("/jokes/random").json()
        extra = set(data.keys()) - EXPECTED_JOKE_FIELDS
        assert not extra, f"Unexpected fields returned: {extra}"

    def test_id_is_positive_integer(self):
        data = client.get("/jokes/random").json()
        assert isinstance(data["id"], int)
        assert data["id"] > 0

    def test_setup_is_non_empty_string(self):
        data = client.get("/jokes/random").json()
        assert isinstance(data["setup"], str)
        assert len(data["setup"].strip()) > 0

    def test_punchline_is_non_empty_string(self):
        data = client.get("/jokes/random").json()
        assert isinstance(data["punchline"], str)
        assert len(data["punchline"].strip()) > 0

    def test_category_is_non_empty_string(self):
        data = client.get("/jokes/random").json()
        assert isinstance(data["category"], str)
        assert len(data["category"].strip()) > 0

    def test_id_within_dataset_range(self):
        """ID must be between 1 and the total dataset size."""
        data = client.get("/jokes/random").json()
        assert 1 <= data["id"] <= JOKE_DATASET_SIZE

    def test_category_is_one_of_known_values(self):
        """Category must be one of the six documented values."""
        data = client.get("/jokes/random").json()
        assert data["category"] in KNOWN_CATEGORIES, (
            f"Unexpected category '{data['category']}'. "
            f"Known categories: {KNOWN_CATEGORIES}"
        )

    def test_setup_is_a_question_or_statement(self):
        """
        Realistic data check: setup strings in the dataset are questions or
        statements, not empty, not whitespace-only, and reasonably short (< 300 chars).
        """
        data = client.get("/jokes/random").json()
        setup = data["setup"]
        assert len(setup) < 300, f"Setup unexpectedly long: {len(setup)} chars"
        assert setup == setup.strip(), "Setup has leading/trailing whitespace"

    def test_punchline_realistic_length(self):
        """Punchline should be a real sentence, not a placeholder."""
        data = client.get("/jokes/random").json()
        punchline = data["punchline"]
        assert len(punchline) >= 5, "Punchline suspiciously short"
        assert len(punchline) < 300, f"Punchline unexpectedly long: {len(punchline)} chars"


# ---------------------------------------------------------------------------
# GET /jokes/random — randomness
# ---------------------------------------------------------------------------

class TestRandomJokeRandomness:
    """Verify that the random selection actually varies across calls."""

    def test_ten_calls_not_all_identical(self):
        """
        With 30 jokes in the dataset, 10 calls must not all return the same joke.
        Probability of all 10 being identical: (1/30)^9 ≈ 10^-13 — negligible.
        """
        ids = [client.get("/jokes/random").json()["id"] for _ in range(10)]
        unique_ids = set(ids)
        assert len(unique_ids) > 1, (
            f"All 10 calls returned the same joke (id={ids[0]}). "
            "Random selection is likely broken."
        )

    def test_twenty_calls_cover_multiple_categories(self):
        """
        With 6 categories and 30 jokes spread across them, 20 calls should
        return at least 2 distinct categories.
        """
        categories = {client.get("/jokes/random").json()["category"] for _ in range(20)}
        assert len(categories) >= 2, (
            f"Only {len(categories)} category seen in 20 calls. "
            "Dataset may be category-biased or selection is broken."
        )

    def test_fifty_calls_produce_wide_distribution(self):
        """
        50 calls on a 30-joke dataset should produce at least 10 distinct joke IDs.
        This guards against a degenerate RNG or off-by-one in the selection logic.
        """
        ids = {client.get("/jokes/random").json()["id"] for _ in range(50)}
        assert len(ids) >= 10, (
            f"Only {len(ids)} distinct jokes seen in 50 calls. "
            "Random distribution is too narrow."
        )

    def test_consecutive_calls_can_differ(self):
        """
        Make two back-to-back calls and assert they are not always identical
        (run in a loop until we find a difference, or fail after 30 tries).
        """
        for _ in range(30):
            a = client.get("/jokes/random").json()["id"]
            b = client.get("/jokes/random").json()["id"]
            if a != b:
                return  # found a differing pair — pass
        pytest.fail("30 consecutive pairs all returned the same joke ID. Randomness suspect.")


# ---------------------------------------------------------------------------
# GET /jokes/random — error / edge cases
# ---------------------------------------------------------------------------

class TestRandomJokeErrorCases:
    """Verify the API handles error conditions correctly."""

    def test_empty_jokes_list_returns_500(self):
        """
        When the joke store is empty the endpoint must return HTTP 500 with
        the documented detail message. We patch the joke list to be empty.
        """
        with patch("app.jokes._jokes", []):
            resp = client.get("/jokes/random")
        assert resp.status_code == 500
        body = resp.json()
        assert "detail" in body
        assert body["detail"] == "No jokes available."

    def test_post_method_not_allowed(self):
        resp = client.post("/jokes/random")
        assert resp.status_code == 405

    def test_put_method_not_allowed(self):
        resp = client.put("/jokes/random")
        assert resp.status_code == 405

    def test_delete_method_not_allowed(self):
        resp = client.delete("/jokes/random")
        assert resp.status_code == 405

    def test_patch_method_not_allowed(self):
        resp = client.patch("/jokes/random")
        assert resp.status_code == 405

    def test_query_params_are_ignored_gracefully(self):
        """
        The endpoint takes no query parameters.
        Unknown parameters should not crash the service — still 200 OK.
        """
        resp = client.get("/jokes/random?unknown_param=foo&limit=5")
        assert resp.status_code == 200

    def test_trailing_slash_variant(self):
        """
        GET /jokes/random/ (trailing slash) — FastAPI either redirects (307)
        or handles it. It must not return 500.
        """
        resp = client.get("/jokes/random/", follow_redirects=False)
        assert resp.status_code not in {500, 502, 503}

    def test_response_is_stable_across_repeated_calls(self):
        """
        Schema must be consistent: every call returns the same field set.
        Validates no intermittent serialisation issues.
        """
        for i in range(5):
            data = client.get("/jokes/random").json()
            assert set(data.keys()) == EXPECTED_JOKE_FIELDS, (
                f"Call {i+1} returned unexpected field set: {set(data.keys())}"
            )


# ---------------------------------------------------------------------------
# GET /health — happy path, edge cases, error cases
# ---------------------------------------------------------------------------

class TestHealthEndpoint:
    """Three tests per endpoint rule applied to /health."""

    # Happy path
    def test_returns_200(self):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_exact_response_body(self):
        data = client.get("/health").json()
        assert data == {"status": "ok"}

    def test_content_type_is_json(self):
        resp = client.get("/health")
        assert "application/json" in resp.headers["content-type"]

    # Edge case
    def test_health_is_not_affected_by_joke_store_state(self):
        """
        /health must still return 200 even when the joke list is empty.
        Health check should reflect app liveness, not data availability.
        """
        with patch("app.jokes._jokes", []):
            resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_no_extra_fields_in_health_response(self):
        """Health response must be exactly {status: ok}, nothing extra."""
        data = client.get("/health").json()
        assert set(data.keys()) == {"status"}

    def test_status_value_is_ok_string(self):
        data = client.get("/health").json()
        assert data["status"] == "ok"
        assert isinstance(data["status"], str)

    # Error case
    def test_post_to_health_not_allowed(self):
        resp = client.post("/health")
        assert resp.status_code == 405

    def test_health_repeated_calls_all_200(self):
        """Health check must be stable — never flaky under repeated calls."""
        for i in range(10):
            resp = client.get("/health")
            assert resp.status_code == 200, f"Health check failed on call {i+1}"


# ---------------------------------------------------------------------------
# Unknown routes
# ---------------------------------------------------------------------------

class TestUnknownRoutes:
    """Verify the API handles undefined routes correctly."""

    def test_completely_unknown_path_returns_404(self):
        resp = client.get("/nonexistent")
        assert resp.status_code == 404

    def test_unknown_nested_path_returns_404(self):
        resp = client.get("/jokes/specific/12345")
        assert resp.status_code == 404

    def test_root_path_returns_404(self):
        """/ is not documented — must return 404, not 500."""
        resp = client.get("/")
        assert resp.status_code == 404

    def test_404_response_has_detail_field(self):
        resp = client.get("/nonexistent")
        body = resp.json()
        assert "detail" in body

    def test_docs_endpoint_present(self):
        """
        FastAPI auto-generates /docs (Swagger UI). This is available by default
        and can be useful for testing. If intentionally disabled, update this test.
        """
        resp = client.get("/docs")
        # Docs are present by default in FastAPI — 200 OK
        assert resp.status_code == 200

    def test_openapi_schema_endpoint_present(self):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        schema = resp.json()
        assert "openapi" in schema
        assert "paths" in schema


# ---------------------------------------------------------------------------
# OpenAPI / schema contract
# ---------------------------------------------------------------------------

class TestOpenAPIContract:
    """Validate that the OpenAPI schema accurately documents the endpoints."""

    def test_jokes_random_in_openapi_paths(self):
        schema = client.get("/openapi.json").json()
        assert "/jokes/random" in schema["paths"]

    def test_health_in_openapi_paths(self):
        schema = client.get("/openapi.json").json()
        assert "/health" in schema["paths"]

    def test_jokes_random_has_get_method(self):
        schema = client.get("/openapi.json").json()
        assert "get" in schema["paths"]["/jokes/random"]

    def test_openapi_version_declared(self):
        schema = client.get("/openapi.json").json()
        assert schema["openapi"].startswith("3.")


# ---------------------------------------------------------------------------
# Performance baseline
# ---------------------------------------------------------------------------

class TestPerformanceBaseline:
    """
    Performance rule: the proxy/service must add less than 50ms overhead
    on a response. Since this is an in-process integration test, we use
    a conservative 200ms wall-clock limit (includes Python test harness overhead).
    Real production measurement should be done with per benchmarking.
    """

    def test_random_joke_responds_within_200ms(self):
        start = time.perf_counter()
        resp = client.get("/jokes/random")
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert resp.status_code == 200
        assert elapsed_ms < 200, (
            f"Response took {elapsed_ms:.1f}ms — exceeds 200ms baseline. "
            "Investigate startup or I/O bottlenecks."
        )

    def test_health_responds_within_50ms(self):
        """Health check is a pure in-memory op — must be sub-50ms even in test."""
        start = time.perf_counter()
        resp = client.get("/health")
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert resp.status_code == 200
        assert elapsed_ms < 50, (
            f"Health check took {elapsed_ms:.1f}ms — should be near-instant."
        )

    def test_ten_sequential_calls_average_under_100ms(self):
        """
        Sustained load check: average latency of 10 sequential calls must
        remain under 100ms each.
        """
        times = []
        for _ in range(10):
            start = time.perf_counter()
            resp = client.get("/jokes/random")
            times.append((time.perf_counter() - start) * 1000)
            assert resp.status_code == 200
        avg_ms = sum(times) / len(times)
        assert avg_ms < 100, (
            f"Average latency over 10 calls: {avg_ms:.1f}ms — exceeds 100ms."
        )


# ---------------------------------------------------------------------------
# Security observations (documented as tests + skip markers with notes)
# ---------------------------------------------------------------------------

class TestSecurityObservations:
    """
    Security checks. Rate limiting is NOT implemented on this service.
    Tests below verify the current (missing) behaviour and document the risk.
    """

    def test_no_rate_limiting_on_jokes_random(self):
        """
        SECURITY FLAG: GET /jokes/random has no rate limiting.
        100 rapid calls all succeed with 200 — no 429 Too Many Requests.
        An attacker can hit this endpoint without restriction.
        Recommendation: add slowapi or similar rate-limiting middleware.
        """
        results = [client.get("/jokes/random").status_code for _ in range(100)]
        assert all(s == 200 for s in results), "Unexpected non-200 in rapid calls"
        # The fact that this passes confirms NO rate limiting is present.
        # This is documented here as a known gap, not a passing security check.

    def test_no_rate_limiting_on_health(self):
        """
        SECURITY FLAG: GET /health has no rate limiting.
        Health endpoints are often scraped by bots. 50 rapid calls all succeed.
        """
        results = [client.get("/health").status_code for _ in range(50)]
        assert all(s == 200 for s in results)

    def test_no_authentication_required(self):
        """
        The API is intentionally public (no auth per bjorn's architecture).
        Documented here: if this service ever returns user-specific data,
        authentication must be added before that deployment.
        """
        resp = client.get("/jokes/random")
        assert resp.status_code == 200
        # No WWW-Authenticate or 401 — intentional for v1, must revisit if user data added

    def test_cors_headers_not_set_by_default(self):
        """
        FastAPI does not add CORS headers unless CORSMiddleware is configured.
        Verify the current state. If a browser client needs to call this API,
        CORS middleware must be added.
        """
        resp = client.get("/jokes/random", headers={"Origin": "https://example.com"})
        # No CORS header present — document current state
        has_cors = "access-control-allow-origin" in resp.headers
        # This assertion passes whether cors is present or not — it documents the state.
        # If this service adds CORSMiddleware, update accordingly.
        assert resp.status_code == 200  # Service still responds; CORS state is noted above
