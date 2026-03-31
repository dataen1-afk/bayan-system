#!/usr/bin/env python3
"""
One-time / ops: list users and reset admin@bayan.com password (production from local machine).

**Required env (PowerShell / bash):**
  MONGO_URL   — production Atlas URI (same as Render)
  DB_NAME     — e.g. bayan_system

**Apply guard:**
  BAYAN_ENSURE_ADMIN=1  — required for --apply

Optional: ``backend/.env`` is loaded with override=False only to fill *missing* vars
(so explicit MONGO_URL / DB_NAME in the shell always win over .env).

  cd backend
  python scripts/ensure_bayan_admin.py --list
  python scripts/ensure_bayan_admin.py --apply   # needs BAYAN_ENSURE_ADMIN=1
"""
from __future__ import annotations

import argparse
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

from dotenv import dotenv_values, load_dotenv  # noqa: E402

load_dotenv(BACKEND / ".env", override=False)

from pymongo import MongoClient  # noqa: E402

from auth import hash_password  # noqa: E402
from role_permissions import UserRole  # noqa: E402

MANAGEMENT_ROLES = {
    UserRole.SYSTEM_ADMIN,
    UserRole.CEO,
    UserRole.GENERAL_MANAGER,
    UserRole.ADMIN,
}

DEFAULT_EMAIL = "admin@bayan.com"
DEFAULT_PASSWORD = "123456"
_ENV_PATH = BACKEND / ".env"


def _resolve_db_name() -> str:
    """Process DB_NAME wins; else .env; else bayan_system (same idea as database.py)."""
    proc = os.environ.get("DB_NAME")
    if proc is not None and str(proc).strip():
        s = str(proc).strip().strip('"').strip("'")
    else:
        s = ""
        if _ENV_PATH.is_file():
            s = _normalize_db_name(dotenv_values(_ENV_PATH).get("DB_NAME"))
    if not s:
        s = "bayan_system"
    if s == "test_database":
        s = "bayan_system"
    return s


def _normalize_db_name(raw: str | None) -> str:
    if raw is None:
        return ""
    return str(raw).strip().strip('"').strip("'")


def _mongo_url() -> str:
    url = os.environ.get("MONGO_URL")
    if url and str(url).strip():
        return str(url).strip().strip('"').strip("'")
    print(
        "MONGO_URL is not set. Set it in the shell to your production URI, e.g.:",
        file=sys.stderr,
    )
    print('  $env:MONGO_URL = "mongodb+srv://..."', file=sys.stderr)
    raise SystemExit(2)


def _connect():
    return MongoClient(_mongo_url(), serverSelectionTimeoutMS=15000)


def cmd_list(mc: MongoClient, db_name: str) -> None:
    coll = mc[db_name]["users"]
    print(f"Database: {db_name}")
    print("--- users (email, role, has_string_id, password_field) ---")
    for doc in coll.find({}, {"password": 1, "email": 1, "role": 1, "name": 1, "id": 1}):
        em = doc.get("email", "")
        role = doc.get("role", "")
        hid = bool(doc.get("id"))
        pw = doc.get("password")
        pws = "set" if pw else "missing"
        mark = "  [mgmt]" if str(role).strip().lower() in {r.lower() for r in MANAGEMENT_ROLES} else ""
        print(f"  {em!r}  role={role!r}  id_field={hid}  password={pws}{mark}")


def cmd_apply(mc: MongoClient, db_name: str, email: str, password: str) -> None:
    if os.environ.get("BAYAN_ENSURE_ADMIN", "").strip().lower() not in ("1", "true", "yes", "on"):
        print(
            "Refusing --apply without BAYAN_ENSURE_ADMIN=1 "
            "(prevents accidental production resets).",
            file=sys.stderr,
        )
        sys.exit(3)

    coll = mc[db_name]["users"]
    email_norm = str(email).lower().strip()
    hpw = hash_password(password)

    doc = coll.find_one({"email": email_norm})
    if not doc:
        doc = coll.find_one({"email": email})

    now = datetime.now(timezone.utc).isoformat()

    if doc:
        oid = doc.get("_id")
        uid = doc.get("id")
        if not uid:
            uid = str(uuid.uuid4())
        update = {
            "$set": {
                "email": email_norm,
                "password": hpw,
                "role": UserRole.ADMIN,
                "id": uid,
            }
        }
        coll.update_one({"_id": oid}, update)
        print(f"Updated existing user _id={oid!s} -> email={email_norm!r} role=admin password=reset")
    else:
        uid = str(uuid.uuid4())
        coll.insert_one(
            {
                "id": uid,
                "name": "Administrator",
                "email": email_norm,
                "role": UserRole.ADMIN,
                "password": hpw,
                "created_at": now,
            }
        )
        print(f"Inserted new admin {email_norm!r} id={uid}")

    print("Done. Login with that email + password via POST /api/auth/login")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="List users and management roles")
    ap.add_argument(
        "--apply",
        action="store_true",
        help=f"Set admin password (requires BAYAN_ENSURE_ADMIN=1)",
    )
    ap.add_argument("--email", default=DEFAULT_EMAIL)
    ap.add_argument("--password", default=DEFAULT_PASSWORD)
    args = ap.parse_args()

    if not args.list and not args.apply:
        ap.print_help()
        return 1

    db_name = _resolve_db_name()
    mc = _connect()
    try:
        mc.admin.command("ping")
    except Exception as e:
        print(f"MongoDB ping failed: {e}", file=sys.stderr)
        return 2

    if args.list:
        cmd_list(mc, db_name)
    if args.apply:
        cmd_apply(mc, db_name, args.email, args.password)
    mc.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
