"""Smoke tests for PostgreSQL-backed /api/contracts (requires DATABASE_URL + Postgres)."""
from __future__ import annotations

import asyncio
import os
import sys
import uuid
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


def test_get_contracts_empty_or_list(api, admin_headers):
    r = api.get("/api/contracts", headers=admin_headers)
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


def test_contract_roundtrip_insert_and_download(api, admin_headers):
    from contracts_pg import insert_contract_record

    uid = str(uuid.uuid4())
    pdf = BACKEND_ROOT / "contracts" / f"_pytest_contract_{uid[:8]}.pdf"
    pdf.parent.mkdir(parents=True, exist_ok=True)
    pdf.write_bytes(b"%PDF-1.4 pytest")

    try:
        row = asyncio.run(
            insert_contract_record(
                quotation_id="q-test",
                proposal_id="",
                client_id=uid,
                pdf_path=str(pdf),
            )
        )
        cid = row["id"]
        r = api.get(
            f"/api/contracts/{cid}/download",
            headers=admin_headers,
        )
        assert r.status_code == 200, r.text
        assert r.headers.get("content-type", "").startswith("application/pdf")
    finally:
        if pdf.exists():
            pdf.unlink()
