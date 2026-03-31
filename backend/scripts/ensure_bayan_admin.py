#!/usr/bin/env python3
"""
One-time / ops: list management users and ensure admin@bayan.com can log in.

Uses backend/.env for MONGO_URL and DB_NAME (same resolution as database.py).

  cd backend
  python scripts/ensure_bayan_admin.py --list
  BAYAN_ENSURE_ADMIN=1 python scripts/ensure_bayan_admin.py --apply

--apply sets password for admin@bayan.com to the given --password (default: 123456),
bcrypt-hashed like the app. Creates the user if missing; updates password + role + id if present.
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

from dotenv import load_dotenv  # noqa: E402

load_dotenv(BACKEND / ".env", override=False)

from pymongo import MongoClient  # noqa: E402

from auth import hash_password  # noqa: E402
from database import DB_NAME  # noqa: E402
from role_permissions import UserRole  # noqa: E402

MANAGEMENT_ROLES = {
    UserRole.SYSTEM_ADMIN,
    UserRole.CEO,
    UserRole.GENERAL_MANAGER,
    UserRole.ADMIN,
}

DEFAULT_EMAIL = "admin@bayan.com"
DEFAULT_PASSWORD = "123456"


def _connect():
    url = os.environ.get("MONGO_URL")
    if not url:
        print("MONGO_URL missing (set in backend/.env)", file=sys.stderr)
        sys.exit(2)
    return MongoClient(url, serverSelectionTimeoutMS=15000)


def cmd_list(mc: MongoClient) -> None:
    coll = mc[DB_NAME]["users"]
    print(f"Database: {DB_NAME}")
    print("--- users (email, role, has_string_id, password_field) ---")
    for doc in coll.find({}, {"password": 1, "email": 1, "role": 1, "name": 1, "id": 1}):
        em = doc.get("email", "")
        role = doc.get("role", "")
        hid = bool(doc.get("id"))
        pw = doc.get("password")
        pws = "set" if pw else "missing"
        mark = "  [mgmt]" if str(role).strip().lower() in {r.lower() for r in MANAGEMENT_ROLES} else ""
        print(f"  {em!r}  role={role!r}  id_field={hid}  password={pws}{mark}")


def cmd_apply(mc: MongoClient, email: str, password: str) -> None:
    if os.environ.get("BAYAN_ENSURE_ADMIN", "").strip() not in ("1", "true", "yes", "on"):
        print(
            "Refusing --apply without BAYAN_ENSURE_ADMIN=1 "
            "(prevents accidental production resets).",
            file=sys.stderr,
        )
        sys.exit(3)

    coll = mc[DB_NAME]["users"]
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
        help=f"Set {DEFAULT_EMAIL!r} password (requires BAYAN_ENSURE_ADMIN=1)",
    )
    ap.add_argument("--email", default=DEFAULT_EMAIL)
    ap.add_argument("--password", default=DEFAULT_PASSWORD)
    args = ap.parse_args()

    if not args.list and not args.apply:
        ap.print_help()
        return 1

    mc = _connect()
    try:
        mc.admin.command("ping")
    except Exception as e:
        print(f"MongoDB ping failed: {e}", file=sys.stderr)
        return 2

    if args.list:
        cmd_list(mc)
    if args.apply:
        cmd_apply(mc, args.email, args.password)
    mc.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
