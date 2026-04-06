#!/usr/bin/env python3
"""
One-time PostgreSQL schema bootstrap for Bayan (Supabase or any Postgres).

Creates:
- ORM tables from ``database.Base.metadata`` (today: ``public.users`` / ``UserRow``)
- JSON/document tables defined in ``database.py`` (``clients``, ``contracts``, ``app_documents``)
- Indexes and ``users.extra`` column when needed

**Prerequisites**
- ``DATABASE_URL`` set to ``postgresql://...`` or ``postgresql+asyncpg://...``
  (same as the running API). ``database`` loads ``backend/.env`` if present.

**Run (from ``backend/``):**

  cd backend
  set DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/postgres
  python scripts/bootstrap_postgres_schema.py

PowerShell:

  cd backend
  $env:DATABASE_URL = "postgresql://USER:PASSWORD@HOST:5432/postgres"
  python scripts/bootstrap_postgres_schema.py

If ``public.users`` already exists with the wrong shape, the script aborts with
instructions to ``DROP TABLE public.users CASCADE`` and retry.
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)


async def _main() -> None:
    from database import DB_NAME, DB_NAME_SOURCE, bootstrap_postgresql_schema

    print(f"Bayan schema bootstrap | database={DB_NAME} | {DB_NAME_SOURCE}")
    await bootstrap_postgresql_schema()
    print("Done: ORM tables + clients + contracts + app_documents (+ indexes).")


if __name__ == "__main__":
    asyncio.run(_main())
