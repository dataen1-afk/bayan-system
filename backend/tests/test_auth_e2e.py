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


def test_verify_password_invalid_hash_safe():
    """passlib raises on bad/empty hashes; login must not 500."""
    import auth as auth_mod

    assert auth_mod.verify_password("x", "") is False
    assert auth_mod.verify_password("x", None) is False  # type: ignore[arg-type]
    assert auth_mod.verify_password("x", "plaintext-not-bcrypt") is False


def test_setup_admin_conflict_when_users_exist(e2e_client):
    r = e2e_client.post(
        "/api/setup-admin",
        json={
            "name": "Should Not Create",
            "email": "bootstrap_conflict@example.com",
            "password": "longpassword1",
        },
    )
    assert r.status_code == 409, r.text


def test_login_user_with_only_mongodb_id(e2e_client):
    """Users without string ``id`` (only ``_id``) must still log in."""
    import os

    from auth import hash_password
    from bson import ObjectId
    from database import DB_NAME
    from pymongo import MongoClient

    email = "e2e_objectid_only@example.com"
    mc = MongoClient(os.environ["MONGO_URL"])
    coll = mc[DB_NAME]["users"]
    coll.delete_many({"email": email})
    coll.insert_one(
        {
            "_id": ObjectId(),
            "email": email,
            "name": "OID Only",
            "role": "admin",
            "password": hash_password("pw_test_99"),
            "created_at": "2020-01-01T00:00:00+00:00",
        }
    )
    try:
        r = e2e_client.post(
            "/api/auth/login",
            json={"email": email, "password": "pw_test_99"},
        )
        assert r.status_code == 200, r.text
        tok = r.json().get("token")
        assert tok
        r_me = e2e_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {tok}"},
        )
        assert r_me.status_code == 200, r_me.text
        assert r_me.json().get("email") == email
    finally:
        coll.delete_many({"email": email})
        mc.close()


def test_create_staff_after_login(e2e_client):
    r_login = e2e_client.post(
        "/api/auth/login",
        json={"email": "admin@bayan.com", "password": "123456"},
    )
    assert r_login.status_code == 200, r_login.text
    token = r_login.json()["token"]
    import uuid

    em = f"staff_e2e_{uuid.uuid4().hex[:10]}@example.com"
    r = e2e_client.post(
        "/api/users/create-staff",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "E2E Staff",
            "email": em,
            "password": "StaffPw1!",
            "role": "auditor",
        },
    )
    assert r.status_code == 200, r.text
    assert r.json().get("email") == em
