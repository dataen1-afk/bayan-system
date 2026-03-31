"""
Pytest: same flow as check_auth_flow.py (TestClient, no live HTTP server).

Run from backend/:
    pytest tests/test_auth_e2e.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture(scope="module")
def e2e_client():
    """One app lifespan per module — Motor client must not reopen after loop close."""
    from fastapi.testclient import TestClient
    from server import app

    with TestClient(app) as client:
        yield client


def test_login_returns_token(e2e_client):
    r = e2e_client.post(
        "/api/auth/login",
        json={"email": "admin@bayan.com", "password": "123456"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert "token" in data and data["token"], data
    assert "user" in data


def test_roles_with_bearer_token(e2e_client):
    r_login = e2e_client.post(
        "/api/auth/login",
        json={"email": "admin@bayan.com", "password": "123456"},
    )
    assert r_login.status_code == 200, r_login.text
    token = r_login.json()["token"]

    r_roles = e2e_client.get(
        "/api/roles",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r_roles.status_code == 200, r_roles.text
    data = r_roles.json()
    assert "roles" in data
    assert isinstance(data["roles"], list)
    assert len(data["roles"]) >= 1


def test_auth_config_reportable(e2e_client):
    """Ensures DB/JWT resolution is readable (same process as app)."""
    import auth
    from database import DB_NAME, DB_NAME_SOURCE

    auth.get_jwt_secret()
    assert DB_NAME
    assert DB_NAME_SOURCE
    assert auth.jwt_secret_source()
