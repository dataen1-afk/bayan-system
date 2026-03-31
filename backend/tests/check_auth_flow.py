#!/usr/bin/env python3
"""
End-to-end local auth check: login -> JWT -> GET /api/roles (no Swagger).

Run from the backend directory:
    python tests/check_auth_flow.py

Exit code 0 on PASS, 1 on FAIL. Requires MongoDB reachable per backend/.env and seeded admin.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent

LOGIN_EMAIL = "admin@bayan.com"
LOGIN_PASSWORD = "123456"


def _configure_path() -> None:
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))


def main() -> int:
    _configure_path()
    import os

    os.chdir(BACKEND_ROOT)

    print("=" * 64)
    print("BAYAN LOCAL AUTH FLOW CHECK")
    print("=" * 64)

    try:
        from fastapi.testclient import TestClient
        from server import app
    except Exception as e:
        print(f"[FAIL] Import server app: {type(e).__name__}: {e}")
        return 1

    try:
        with TestClient(app) as client:
            import auth
            from database import DB_NAME, DB_NAME_SOURCE, ENV_FILE_USED

            auth.get_jwt_secret()
            jwt_src = auth.jwt_secret_source()
            jwt_meta = getattr(auth, "_jwt_resolution_meta", "")

            print(f"Active DB name:        {DB_NAME}")
            print(f"DB_NAME resolution:    {DB_NAME_SOURCE}")
            print(f".env path:             {ENV_FILE_USED}")
            print(f"JWT secret source:     {jwt_src}")
            print(f"JWT resolution note:    {jwt_meta}")
            print("-" * 64)

            r_login = client.post(
                "/api/auth/login",
                json={"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD},
            )
            print(f"POST /api/auth/login   HTTP {r_login.status_code}")
            if r_login.status_code != 200:
                print(f"[FAIL] Login error body: {r_login.text[:800]}")
                print(
                    "\nHint: ensure MongoDB is running, DB_NAME matches DB with users, "
                    f"and user {LOGIN_EMAIL} exists (seeded on server startup)."
                )
                return 1

            body = r_login.json()
            token = body.get("token")
            if not token or not isinstance(token, str):
                print(f"[FAIL] Login JSON missing token: {json.dumps(body)[:400]}")
                return 1
            print(f"Token returned:        yes (length {len(token)})")

            r_roles = client.get(
                "/api/roles",
                headers={"Authorization": f"Bearer {token}"},
            )
            print(f"GET /api/roles         HTTP {r_roles.status_code}")
            if r_roles.status_code != 200:
                print(f"[FAIL] /api/roles body: {r_roles.text[:800]}")
                print(
                    "\nHint: JWT_SECRET must match between encode and decode; "
                    "check backend/.env and JWT logs."
                )
                return 1

            roles_payload = r_roles.json()
            if "roles" not in roles_payload or not isinstance(roles_payload["roles"], list):
                print(f"[FAIL] Expected {{'roles': [...]}}; got keys: {list(roles_payload.keys())}")
                return 1
            n = len(roles_payload["roles"])
            if n < 1:
                print("[FAIL] roles list is empty")
                return 1
            print(f"Roles in response:     {n}")

            print("-" * 64)
            print("[PASS] Login + Bearer token + GET /api/roles succeeded.")
            print("       Swagger/manual UI is optional; this flow proves backend auth.")
            print("=" * 64)
            return 0

    except Exception as e:
        print(f"[FAIL] {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
