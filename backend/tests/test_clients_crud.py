"""
CRUD tests for GET/POST/PUT/DELETE /api/clients (PostgreSQL).

Run from backend/ with DATABASE_URL and JWT_SECRET set, PostgreSQL running:
    pytest tests/test_clients_crud.py -v
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL", "").strip(),
    reason="DATABASE_URL not set",
)


@pytest.fixture(scope="module")
def api():
    from fastapi.testclient import TestClient
    from server import app

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def admin_headers(api):
    r = api.post(
        "/api/auth/login",
        json={"email": "admin@bayan.com", "password": "123456"},
    )
    if r.status_code != 200:
        pytest.skip(f"admin login failed: {r.status_code} {r.text[:200]}")
    token = r.json().get("token")
    return {"Authorization": f"Bearer {token}"}


def test_clients_crud_flow(api, admin_headers):
    h = admin_headers

    r0 = api.get("/api/clients", headers=h)
    assert r0.status_code == 200, r0.text
    n0 = len(r0.json())

    r1 = api.post(
        "/api/clients",
        headers=h,
        json={
            "company_name": "ACME Co",
            "national_address": "Riyadh",
            "tax_number": "300000000000003",
            "mobile": "+966500000000",
            "email": "contact@acme.test",
            "payload": {"segment": "industrial"},
        },
    )
    assert r1.status_code == 200, r1.text
    data = r1.json()
    cid = data["id"]
    assert data["company_name"] == "ACME Co"
    assert data["payload"].get("segment") == "industrial"

    r2 = api.get("/api/clients", headers=h)
    assert r2.status_code == 200
    assert len(r2.json()) == n0 + 1

    r3 = api.put(
        f"/api/clients/{cid}",
        headers=h,
        json={"company_name": "ACME Updated", "payload": {"segment": "services"}},
    )
    assert r3.status_code == 200, r3.text
    assert r3.json()["company_name"] == "ACME Updated"
    assert r3.json()["payload"].get("segment") == "services"

    r4 = api.delete(f"/api/clients/{cid}", headers=h)
    assert r4.status_code == 200, r4.text
    assert r4.json().get("id") == cid

    r5 = api.delete(f"/api/clients/{cid}", headers=h)
    assert r5.status_code == 404
