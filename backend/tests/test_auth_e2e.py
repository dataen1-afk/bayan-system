"""
Pytest: same flow as check_auth_flow.py (TestClient, no live HTTP server).

Run from backend/:
    pytest tests/test_auth_e2e.py -v

Requires DATABASE_URL pointing at PostgreSQL (e.g. local bayan_system DB).
"""
from __future__ import annotations

import asyncio
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture(scope="module")
def e2e_client():
    """One app lifespan per module."""
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


@pytest.mark.skip(reason="GET /api/roles still uses legacy Mongo stub until roles are migrated")
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


@pytest.mark.skip(reason="/api/setup-admin still uses legacy Mongo stub")
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


async def _seed_user_direct(email: str, password: str) -> None:
    from auth import hash_password
    from database import AsyncSessionLocal, UserRow

    now = datetime.now(timezone.utc)
    async with AsyncSessionLocal() as session:
        from sqlalchemy import delete

        await session.execute(delete(UserRow).where(UserRow.email == email))
        session.add(
            UserRow(
                id=uuid.uuid4(),
                name="PG Direct",
                email=email,
                role="admin",
                password=hash_password(password),
                active=True,
                created_at=now,
                updated_at=now,
            )
        )
        await session.commit()


def test_login_user_inserted_via_postgres(e2e_client):
    """Users created directly in PostgreSQL (UUID id) must log in and /me works."""
    email = "e2e_pg_direct@example.com"
    password = "pw_test_99"
    asyncio.run(_seed_user_direct(email, password))
    try:
        r = e2e_client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
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
        asyncio.run(_cleanup_user(email))


async def _cleanup_user(email: str) -> None:
    from database import AsyncSessionLocal, UserRow
    from sqlalchemy import delete

    async with AsyncSessionLocal() as session:
        await session.execute(delete(UserRow).where(UserRow.email == email))
        await session.commit()


@pytest.mark.skip(reason="/api/users/create-staff still uses legacy Mongo stub")
def test_create_staff_after_login(e2e_client):
    r_login = e2e_client.post(
        "/api/auth/login",
        json={"email": "admin@bayan.com", "password": "123456"},
    )
    assert r_login.status_code == 200, r_login.text
    token = r_login.json()["token"]
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
