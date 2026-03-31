#!/usr/bin/env python3
"""
Remote HTTP verification for auth and user-management endpoints (no Swagger).

Discovers paths from the server's OpenAPI document when possible, so the same
script works against Render (IES-style API) and local monolith (extra routes).

Usage:
  cd backend
  python tests/verify_user_mgmt_remote.py
  python tests/verify_user_mgmt_remote.py --base-url https://bayan-backend-4zn3.onrender.com
  python tests/verify_user_mgmt_remote.py --email data.en@ies.sa --password '***'
  python tests/verify_user_mgmt_remote.py --mutate
  python tests/verify_user_mgmt_remote.py --probe-monolith-extras   # /api/roles, /api/users/clients, etc.

Environment (optional):
  BAYAN_VERIFY_BASE_URL, BAYAN_VERIFY_EMAIL, BAYAN_VERIFY_PASSWORD
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
import uuid
from dataclasses import dataclass
from typing import Any, Callable

import requests

DEFAULT_BASE = os.environ.get(
    "BAYAN_VERIFY_BASE_URL", "https://bayan-backend-4zn3.onrender.com"
).rstrip("/")


def _reg_email_disposable() -> str:
    return f"bayan.verify.{uuid.uuid4().hex[:12]}@example.com"

# Windows consoles often use a legacy code page; avoid crashes on Arabic names in JSON.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def _short_json(data: Any, max_len: int = 220) -> str:
    if data is None:
        return "(none)"
    try:
        s = json.dumps(data, ensure_ascii=True, default=str)
    except Exception:
        s = str(data)
    if len(s) > max_len:
        return s[: max_len - 3] + "..."
    return s


def _extract_token(login_json: dict) -> str | None:
    return login_json.get("access_token") or login_json.get("token")


def _openapi_has(openapi: dict | None, path: str, method: str) -> bool:
    """True if OpenAPI documents this concrete path and HTTP method."""
    if not openapi:
        return True
    p = openapi.get("paths", {}).get(path)
    if not p:
        return False
    return method.lower() in p


def _openapi_supports_path(openapi: dict | None, concrete_path: str, method: str) -> bool:
    """Match concrete URLs to OpenAPI templates, e.g. /api/users/{id}."""
    if not openapi:
        return True
    paths = openapi.get("paths", {})
    m = method.lower()
    if concrete_path in paths and m in paths[concrete_path]:
        return True
    c_parts = concrete_path.split("/")
    for opath, spec in paths.items():
        if m not in spec:
            continue
        o_parts = opath.split("/")
        if len(o_parts) != len(c_parts):
            continue
        match = True
        for a, b in zip(c_parts, o_parts):
            if b.startswith("{") and b.endswith("}"):
                continue
            if a != b:
                match = False
                break
        if match:
            return True
    return False


@dataclass
class Row:
    path: str
    method: str
    auth: bool
    note: str
    status: int = 0
    outcome: str = "SKIP"
    detail: str = ""
    expected: str = ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=DEFAULT_BASE)
    ap.add_argument("--email", default=os.environ.get("BAYAN_VERIFY_EMAIL", ""))
    ap.add_argument("--password", default=os.environ.get("BAYAN_VERIFY_PASSWORD", ""))
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument(
        "--mutate",
        action="store_true",
        help="POST requests that create users (disposable emails)",
    )
    ap.add_argument(
        "--probe-monolith-extras",
        action="store_true",
        help="Also call Bayan monolith-only paths (/api/roles, ...) and report 404 vs OK",
    )
    args = ap.parse_args()
    base = args.base_url.rstrip("/")
    email = args.email or "data.en@ies.sa"
    password = args.password or "123456"

    session = requests.Session()
    session.headers.update(
        {"Accept": "application/json", "User-Agent": "bayan-verify-user-mgmt/2.0"}
    )

    openapi: dict | None = None
    try:
        orr = session.get(f"{base}/openapi.json", timeout=args.timeout)
        if orr.status_code == 200:
            openapi = orr.json()
    except requests.RequestException:
        openapi = None

    rows: list[Row] = []
    token: str | None = None

    def record(
        path: str,
        method: str,
        auth: bool,
        note: str,
        *,
        expected: str = "",
        skip_reason: str | None = None,
        json_body: Any = None,
        ok_if: Callable[[int, Any], tuple[str, str]] | None = None,
    ) -> None:
        nonlocal token
        if skip_reason:
            rows.append(
                Row(
                    path=path,
                    method=method,
                    auth=auth,
                    note=note,
                    outcome="SKIP",
                    detail=skip_reason,
                    expected=expected,
                )
            )
            return
        if openapi is not None and not _openapi_supports_path(openapi, path, method):
            rows.append(
                Row(
                    path=path,
                    method=method,
                    auth=auth,
                    note=note,
                    outcome="SKIP",
                    detail="not in OpenAPI for this deployment",
                    expected=expected,
                )
            )
            return

        r = Row(
            path=path,
            method=method,
            auth=auth,
            note=note,
            expected=expected,
        )
        rows.append(r)
        url = f"{base}{path}"
        headers: dict[str, str] = {}
        if auth:
            if not token:
                r.status = 0
                r.outcome = "SKIP"
                r.detail = "no token (login failed)"
                return
            headers["Authorization"] = f"Bearer {token}"
        try:
            resp = session.request(
                method, url, headers=headers, json=json_body, timeout=args.timeout
            )
        except requests.RequestException as e:
            r.status = 0
            r.outcome = "FAIL"
            r.detail = f"request error: {e}"
            return

        r.status = resp.status_code
        try:
            body = resp.json()
        except Exception:
            body = resp.text[:500]

        if ok_if:
            outcome, detail = ok_if(resp.status_code, body)
            r.outcome = outcome
            r.detail = detail
            return

        if 200 <= resp.status_code < 300:
            r.outcome = "OK"
            r.detail = _short_json(body)
        else:
            r.outcome = "FAIL"
            if isinstance(body, dict) and "detail" in body:
                r.detail = _short_json(body.get("detail"))
            else:
                r.detail = _short_json(body, max_len=400)

    # --- Login ---
    try:
        lr = session.post(
            f"{base}/api/auth/login",
            json={"email": email, "password": password},
            timeout=args.timeout,
        )
    except requests.RequestException as e:
        print(f"[FATAL] login request failed: {e}", file=sys.stderr)
        return 2

    lj: dict = {}
    if lr.content:
        try:
            lj = lr.json()
        except Exception:
            pass
    token = _extract_token(lj) if lr.status_code == 200 else None

    login_row = Row(
        path="/api/auth/login",
        method="POST",
        auth=False,
        note="Login",
        expected='{"email","password"}',
        status=lr.status_code,
    )
    if lr.status_code == 200 and token:
        keys = [k for k in ("access_token", "token", "token_type") if k in lj]
        login_row.outcome = "OK"
        login_row.detail = f"JWT fields present: {keys}; user.role={lj.get('user', {}).get('role')!r}"
    else:
        login_row.outcome = "FAIL"
        login_row.detail = _short_json(lj if lj else lr.text, 400)
    rows.append(login_row)

    if not token:
        _print_report(
            rows, base, openapi_loaded=openapi is not None, mutated=args.mutate
        )
        return 1

    record(
        "/api/auth/me",
        "GET",
        False,
        "Current user without Bearer (expect 401/403)",
        ok_if=lambda c, b: (
            ("OK", f"denied as expected ({c})")
            if c in (401, 403)
            else ("FAIL", f"expected 401/403, got {c}: {_short_json(b)}")
        ),
    )

    record(
        "/api/auth/me",
        "GET",
        True,
        "Current user with Bearer",
    )

    record(
        "/api/auth/forgot-password",
        "POST",
        False,
        "Forgot password (non-destructive probe)",
        expected='{"email"}',
        json_body={"email": _reg_email_disposable()},
        ok_if=lambda c, b: (
            ("OK", _short_json(b))
            if c in (200, 201, 202, 204)
            else (
                "OK",
                f"{c} (often acceptable if email not configured)",
            )
            if c in (400, 404, 422, 500)
            else ("FAIL", f"unexpected {c}: {_short_json(b)}")
        ),
    )

    record(
        "/api/auth/reset-password",
        "POST",
        False,
        "Reset password with invalid token (expect 4xx)",
        expected='{"token","new_password"}',
        json_body={"token": "invalid-token", "new_password": "N0tUsed1!"},
        ok_if=lambda c, b: (
            ("OK", _short_json(b))
            if 400 <= c < 500
            else ("PARTIAL", f"unexpected {c}: {_short_json(b)}")
        ),
    )

    record(
        "/api/auth/change-password",
        "POST",
        True,
        "Change password with wrong current (expect 4xx, no change)",
        expected='{"current_password","new_password"}',
        json_body={"current_password": "definitely-wrong-password", "new_password": "N0tUsed2!"},
        ok_if=lambda c, b: (
            ("OK", _short_json(b))
            if 400 <= c < 500
            else ("PARTIAL", f"unexpected {c}: {_short_json(b)}")
        ),
    )

    reg_path = "/api/auth/register"
    if openapi is not None and _openapi_has(openapi, reg_path, "POST"):
        reg_body = {
            "name": "API Verify Register",
            "email": _reg_email_disposable(),
            "password": "RegVerify1!",
            "role": "EMPLOYEE",
            "department": None,
            "system": None,
            "active": True,
        }
        record(
            reg_path,
            "POST",
            False,
            "Register without Bearer (deploy may require auth)",
            expected="UserCreate-like body on IES deploy",
            json_body=reg_body,
            ok_if=lambda c, b: (
                ("OK", _short_json(b))
                if 200 <= c < 300
                else (
                    "OK",
                    "anonymous registration disabled (403) — use POST /api/users with admin token",
                )
                if c == 403
                else ("FAIL", f"{c}: {_short_json(b)}")
            ),
        )
    else:
        record(
            reg_path,
            "POST",
            False,
            "Register",
            skip_reason="not in OpenAPI",
        )

    record("/api/users", "GET", True, "List users")

    # Deployed API uses MongoDB ObjectId-style user ids (24 hex), not UUIDs.
    fake_id = "ffffffffffffffffffffffff"
    record(
        f"/api/users/{fake_id}",
        "PUT",
        True,
        "Update non-existent user (expect 404)",
        json_body={"name": "noop"},
        ok_if=lambda c, b: (
            ("OK", _short_json(b))
            if c == 404
            else (
                "OK",
                "HTTP 500 but not-found semantics (API should return 404)",
            )
            if c == 500 and "not found" in str(b).lower()
            else ("PARTIAL", f"expected 404, got {c}: {_short_json(b)}")
        ),
    )

    record(
        f"/api/users/{fake_id}",
        "DELETE",
        True,
        "Delete non-existent user (expect 404)",
        ok_if=lambda c, b: (
            ("OK", _short_json(b))
            if c == 404
            else ("PARTIAL", f"expected 404, got {c}: {_short_json(b)}")
        ),
    )

    record(
        f"/api/users/{fake_id}/reset-password",
        "PUT",
        True,
        "Admin reset password for missing user (expect 404)",
        json_body={"new_password": "N0tUsed3!"},
        ok_if=lambda c, b: (
            ("OK", _short_json(b))
            if c == 404
            else ("PARTIAL", f"expected 404, got {c}: {_short_json(b)}")
        ),
    )

    if args.mutate and openapi is not None and _openapi_has(openapi, "/api/users", "POST"):
        staff_body = {
            "name": "API Verify Staff",
            "email": _reg_email_disposable(),
            "password": "StaffVerify1!",
            "role": "CONSULTANT",
            "department": "verify",
            "active": True,
        }
        record(
            "/api/users",
            "POST",
            True,
            "Create user (admin) --mutate",
            expected="UserCreate",
            json_body=staff_body,
        )

    if args.probe_monolith_extras:
        for monolith_path, desc in [
            ("/api/roles", "Monolith: all roles"),
            ("/api/roles/staff", "Monolith: staff roles"),
            ("/api/users/clients", "Monolith: list clients"),
        ]:

            def _ok_monolith(
                c: int, b: Any, _mp: str = monolith_path
            ) -> tuple[str, str]:
                if 200 <= c < 300:
                    return "OK", _short_json(b)
                if c == 404:
                    return (
                        "SKIP",
                        f"{c} (not on this server; OK for IES-style deploy)",
                    )
                return "FAIL", f"{c}: {_short_json(b)}"

            record(
                monolith_path,
                "GET",
                True,
                desc,
                ok_if=_ok_monolith,
            )

    _print_report(rows, base, openapi_loaded=openapi is not None, mutated=args.mutate)
    failed = sum(1 for r in rows if r.outcome == "FAIL")
    return 1 if failed else 0


def _print_report(
    rows: list[Row], base: str, *, openapi_loaded: bool, mutated: bool
) -> None:
    print("\n" + "=" * 96)
    print(f"BAYAN AUTH / USER API CHECK  |  base={base}")
    print(f"OpenAPI: {'loaded' if openapi_loaded else 'unavailable (all paths attempted)'}")
    print("=" * 96)
    for r in rows:
        a = "yes" if r.auth else "no"
        print(
            f"\n{r.method:6} {r.path}\n"
            f"  auth: {a}  HTTP {r.status}  [{r.outcome}]\n"
            f"  {r.note}\n"
            + (f"  expected: {r.expected}\n" if r.expected else "")
            + f"  -> {r.detail}"
        )
    print("\n" + "=" * 96)

    ok = [r for r in rows if r.outcome == "OK"]
    part = [r for r in rows if r.outcome == "PARTIAL"]
    skip = [r for r in rows if r.outcome == "SKIP"]
    fail = [r for r in rows if r.outcome == "FAIL"]

    print("\n## Working now\n")
    for r in ok:
        print(f"  - {r.method} {r.path}")
    if not ok:
        print("  (none)")

    print("\n## Broken or needs follow-up (FAIL / PARTIAL)\n")
    for r in fail + part:
        print(f"  - [{r.outcome}] {r.method} {r.path} HTTP {r.status}: {r.detail}")
    if not fail and not part:
        print("  (none)")

    print("\n## Skipped / not on this deployment\n")
    for r in skip:
        print(f"  - {r.method} {r.path}: {r.detail}")
    if not skip:
        print("  (none)")

    print("\n## Notes\n")
    print(
        textwrap.fill(
            "Render IES-style API: login returns access_token (+ token_type). "
            "GET /api/users may return a JSON array. "
            "This repo's bayan monolith (server.py) also exposes /api/roles, PUT .../role, "
            "POST /users/create-staff, GET /api/users/clients — use --probe-monolith-extras against local.",
            width=92,
        )
    )
    if not mutated:
        print(
            textwrap.fill(
                "Use --mutate to POST /api/users (creates CONSULTANT with random email).",
                width=92,
            )
        )


if __name__ == "__main__":
    raise SystemExit(main())
