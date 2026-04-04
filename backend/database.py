"""
PostgreSQL via SQLAlchemy 2.x async + asyncpg.

``DATABASE_URL`` must be set (e.g. postgresql://user:pass@host:5432/dbname).
Internally normalized to postgresql+asyncpg:// for the async driver.

Legacy code still imports ``db`` for Mongo-style collections; those attributes
return stubs that raise until each area is migrated.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import Boolean, DateTime, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

ROOT_DIR = Path(__file__).parent
_ENV_PATH = ROOT_DIR / ".env"
load_dotenv(_ENV_PATH)


def _resolve_db_display_name() -> tuple[str, str]:
    """Human-readable database name for logs (from URL path)."""
    raw_url = os.environ.get("DATABASE_URL", "")
    if not raw_url:
        return "unset", "DATABASE_URL missing"
    try:
        from sqlalchemy.engine import make_url

        u = make_url(raw_url.replace("postgresql+asyncpg://", "postgresql://"))
        name = u.database or "postgres"
        return name, f"from DATABASE_URL (database={name})"
    except Exception:
        return "postgresql", "from DATABASE_URL (parse failed; using generic label)"


DB_NAME, DB_NAME_SOURCE = _resolve_db_display_name()
ENV_FILE_USED = _ENV_PATH.resolve()


def _async_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url[len("postgresql://") :]
    raise ValueError(
        "DATABASE_URL must start with postgresql:// or postgresql+asyncpg://"
    )


DATABASE_URL_RAW = os.environ.get("DATABASE_URL", "").strip()
if not DATABASE_URL_RAW:
    raise RuntimeError(
        "DATABASE_URL is required (e.g. postgresql://user:pass@host:5432/bayan_system)"
    )

DATABASE_URL = _async_url(DATABASE_URL_RAW)

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


class UserRow(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


# --- Legacy Mongo ``db`` stub (monolith + unmigrated routes) -----------------

_UNMIGRATED = (
    "This endpoint still expects the legacy MongoDB API; it is not migrated to "
    "PostgreSQL yet."
)


class _UnmigratedCursor:
    def __init__(self, coll: str) -> None:
        self._coll = coll

    def sort(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def skip(self, *args, **kwargs):
        return self

    async def to_list(self, *args, **kwargs):
        raise RuntimeError(_UNMIGRATED)

    def __getattr__(self, name):
        async def _boom(*args, **kwargs):
            raise RuntimeError(_UNMIGRATED)

        return _boom


class _UnmigratedCollection:
    def __init__(self, name: str) -> None:
        self._name = name

    def find(self, *args, **kwargs):
        return _UnmigratedCursor(self._name)

    def aggregate(self, *args, **kwargs):
        return _UnmigratedCursor(self._name)

    async def find_one(self, *args, **kwargs):
        raise RuntimeError(_UNMIGRATED)

    async def insert_one(self, *args, **kwargs):
        raise RuntimeError(_UNMIGRATED)

    async def insert_many(self, *args, **kwargs):
        raise RuntimeError(_UNMIGRATED)

    async def update_one(self, *args, **kwargs):
        raise RuntimeError(_UNMIGRATED)

    async def update_many(self, *args, **kwargs):
        raise RuntimeError(_UNMIGRATED)

    async def replace_one(self, *args, **kwargs):
        raise RuntimeError(_UNMIGRATED)

    async def delete_one(self, *args, **kwargs):
        raise RuntimeError(_UNMIGRATED)

    async def delete_many(self, *args, **kwargs):
        raise RuntimeError(_UNMIGRATED)

    async def count_documents(self, *args, **kwargs):
        raise RuntimeError(_UNMIGRATED)

    def __getattr__(self, name):
        async def _boom(*args, **kwargs):
            raise RuntimeError(_UNMIGRATED)

        return _boom


class _UnmigratedDb:
    def __getattr__(self, name: str):
        return _UnmigratedCollection(name)


db = _UnmigratedDb()


CLIENTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name TEXT,
    national_address TEXT,
    tax_number TEXT,
    mobile TEXT,
    email TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb
)
"""

CLIENTS_INDEX_SQL = (
    "CREATE INDEX IF NOT EXISTS ix_clients_created_at ON clients (created_at DESC)"
)

CONTRACTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_number TEXT,
    status TEXT,
    client_id UUID,
    project_name TEXT,
    company_name TEXT,
    client_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb
)
"""

CONTRACTS_INDEX_SQL = (
    "CREATE INDEX IF NOT EXISTS ix_contracts_created_at ON contracts (created_at DESC)"
)

CONTRACTS_INDEX_PAYLOAD_CLIENT_SQL = (
    "CREATE INDEX IF NOT EXISTS ix_contracts_payload_client_id "
    "ON contracts ((payload->>'client_id'))"
)


async def connect_db() -> None:
    """
    Create tables if missing and verify connectivity (SELECT 1).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text(CLIENTS_TABLE_SQL))
        await conn.execute(text(CLIENTS_INDEX_SQL))
        await conn.execute(text(CONTRACTS_TABLE_SQL))
        await conn.execute(text(CONTRACTS_INDEX_SQL))
        await conn.execute(text(CONTRACTS_INDEX_PAYLOAD_CLIENT_SQL))
        await conn.execute(text("SELECT 1"))


async def close_db() -> None:
    await engine.dispose()


__all__ = [
    "AsyncSessionLocal",
    "AsyncSession",
    "Base",
    "DB_NAME",
    "DB_NAME_SOURCE",
    "DATABASE_URL",
    "ENV_FILE_USED",
    "UserRow",
    "SQLAlchemyError",
    "close_db",
    "connect_db",
    "db",
    "engine",
]
