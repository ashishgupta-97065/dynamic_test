"""
Tests for Ticket #4: GET /ping endpoint with optional message parameter.

Covers:
  AC1 - GET /ping (no param)       → 200 {"message": "pong"}
  AC2 - GET /ping?msg=hello        → 200 {"message": "pong: hello"}
  AC3 - GET /ping?msg=<any string> → 200 {"message": "pong: <that string>"}  (generalised)
  AC4 - No auth / no request body required (implicit in all tests; also explicit test)
  AC5 - ≥3 tests in this file

Error paths:
  - POST /ping  → 405 Method Not Allowed
  - DELETE /ping → 405 Method Not Allowed

Edge cases:
  - Empty string query param: ?msg= → {"message": "pong: "}
"""

import sys
import os

# Ensure repo root is on the path so `from main import app` resolves correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# AC1 — GET /ping with no query parameter
# ---------------------------------------------------------------------------

def test_ping_no_message_returns_200():
    """AC1: GET /ping returns HTTP 200."""
    response = client.get("/ping")
    assert response.status_code == 200


def test_ping_no_message_returns_pong_body():
    """AC1: GET /ping body is exactly {"message": "pong"}."""
    response = client.get("/ping")
    assert response.json() == {"message": "pong"}


# ---------------------------------------------------------------------------
# AC2 — GET /ping?msg=hello
# ---------------------------------------------------------------------------

def test_ping_with_hello_returns_200():
    """AC2: GET /ping?msg=hello returns HTTP 200."""
    response = client.get("/ping", params={"msg": "hello"})
    assert response.status_code == 200


def test_ping_with_hello_returns_correct_body():
    """AC2: GET /ping?msg=hello body is {"message": "pong: hello"}."""
    response = client.get("/ping", params={"msg": "hello"})
    assert response.json() == {"message": "pong: hello"}


# ---------------------------------------------------------------------------
# AC3 — Generalised: any msg string is echoed back with "pong: " prefix
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("msg,expected_message", [
    ("world-42",      "pong: world-42"),
    ("test string",   "pong: test string"),
    ("foo",           "pong: foo"),
    ("123",           "pong: 123"),
    ("hello world!",  "pong: hello world!"),
])
def test_ping_with_arbitrary_message(msg, expected_message):
    """AC3: GET /ping?msg=<any string> returns 200 with {"message": "pong: <that string>"}."""
    response = client.get("/ping", params={"msg": msg})
    assert response.status_code == 200
    assert response.json() == {"message": expected_message}


# ---------------------------------------------------------------------------
# AC4 — No authentication or request body required
# ---------------------------------------------------------------------------

def test_ping_no_auth_header_required():
    """AC4: The endpoint is public — no Authorization header is needed."""
    # Explicitly send no auth header; request must succeed.
    response = client.get("/ping")
    assert response.status_code == 200
    assert "message" in response.json()


def test_ping_no_request_body_required():
    """AC4: GET /ping with no body (standard GET) still returns 200."""
    # TestClient GET sends no body by default; asserting that this works.
    response = client.get("/ping")
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Response shape — no envelope wrappers, no extra fields
# ---------------------------------------------------------------------------

def test_ping_response_has_only_message_field():
    """Response JSON must contain exactly one field: 'message'. No envelope wrappers."""
    response = client.get("/ping")
    body = response.json()
    assert set(body.keys()) == {"message"}


def test_ping_with_msg_response_has_only_message_field():
    """With ?msg provided, response still contains only 'message' — no extra fields."""
    response = client.get("/ping", params={"msg": "check-shape"})
    body = response.json()
    assert set(body.keys()) == {"message"}


# ---------------------------------------------------------------------------
# Response content-type
# ---------------------------------------------------------------------------

def test_ping_response_content_type_is_json():
    """Response Content-Type must be application/json."""
    response = client.get("/ping")
    assert "application/json" in response.headers.get("content-type", "")


# ---------------------------------------------------------------------------
# Error paths — wrong HTTP methods
# ---------------------------------------------------------------------------

def test_ping_post_returns_405():
    """Architecture spec: POST /ping → 405 Method Not Allowed (only GET is registered)."""
    response = client.post("/ping")
    assert response.status_code == 405


def test_ping_delete_returns_405():
    """Architecture spec: DELETE /ping → 405 Method Not Allowed."""
    response = client.delete("/ping")
    assert response.status_code == 405


def test_ping_put_returns_405():
    """Architecture spec: PUT /ping → 405 Method Not Allowed."""
    response = client.put("/ping")
    assert response.status_code == 405


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_ping_empty_string_msg_returns_pong_colon_space():
    """Edge: ?msg= (empty string) → {"message": "pong: "} (no special-casing of empty string)."""
    response = client.get("/ping?msg=")
    assert response.status_code == 200
    assert response.json() == {"message": "pong: "}


def test_ping_separator_is_colon_space():
    """The separator between 'pong' and the echoed message must be ': ' (colon + single space)."""
    msg = "separator-check"
    response = client.get("/ping", params={"msg": msg})
    body = response.json()
    assert body["message"] == f"pong: {msg}"
    # Verify colon-space is the separator, not colon-only or double-space
    assert body["message"].startswith("pong: ")
