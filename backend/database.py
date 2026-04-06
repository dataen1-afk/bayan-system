"""
PostgreSQL via SQLAlchemy 2.x async + asyncpg.

``DATABASE_URL`` must be set (e.g. postgresql://… or postgres://… from Supabase).
``postgres://`` is normalized to ``postgresql://``, then to ``postgresql+asyncpg://``
for asyncpg. ``connect_args={"statement_cache_size": 0}`` matches IES Portal /
Supabase pooler (PgBouncer) expectations.

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
from sqlalchemy.dialects.postgresql import JSONB, UUID
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

        parsed = raw_url.strip()
        if parsed.startswith("postgres://"):
            parsed = "postgresql://" + parsed[len("postgres://") :]
        u = make_url(parsed.replace("postgresql+asyncpg://", "postgresql://"))
        name = u.database or "postgres"
        return name, f"from DATABASE_URL (database={name})"
    except Exception:
        return "postgresql", "from DATABASE_URL (parse failed; using generic label)"


DB_NAME, DB_NAME_SOURCE = _resolve_db_display_name()
ENV_FILE_USED = _ENV_PATH.resolve()


def _async_url(url: str) -> str:
    """Match IES Portal: accept postgres://, normalize to postgresql+asyncpg://."""
    u = url.strip()
    if u.startswith("postgres://"):
        u = "postgresql://" + u[len("postgres://") :]
    if u.startswith("postgresql+asyncpg://"):
        return u
    if u.startswith("postgresql://"):
        return "postgresql+asyncpg://" + u[len("postgresql://") :]
    raise ValueError(
        "DATABASE_URL must use postgres://, postgresql://, or postgresql+asyncpg://"
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
    # asyncpg + pgBouncer (e.g. Supabase pooler): disable server-side prepared statement cache.
    connect_args={"statement_cache_size": 0},
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


# Submodules that define additional ``Base`` subclasses must be listed here so
# ``bootstrap_postgresql_schema`` / ``import_all_declarative_models`` register
# every table on ``Base.metadata`` before ``create_all``.
_ORM_METADATA_MODULES: tuple[str, ...] = ()


def import_all_declarative_models() -> None:
    """Import modules that attach ORM models to ``Base`` (for ``metadata.create_all``)."""
    import importlib

    for name in _ORM_METADATA_MODULES:
        importlib.import_module(name)


# Columns ``UserRow`` / ``users_pg`` require on ``public.users``. ``extra`` may be
# added by ``USERS_EXTRA_COLUMN_SQL`` if the table pre-exists without it.
USERS_TABLE_CORE_COLUMNS: frozenset[str] = frozenset(
    {
        "id",
        "name",
        "email",
        "password",
        "role",
        "active",
        "created_at",
        "updated_at",
    }
)


def _users_column_type_expectations() -> dict[str, tuple[str, ...]]:
    """Lowercase substrings expected in ``pg_catalog.format_type`` output."""
    return {
        "id": ("uuid",),
        "name": ("text", "character varying", "varchar"),
        "email": ("text", "character varying", "varchar"),
        "password": ("text", "character varying", "varchar"),
        "role": ("text", "character varying", "varchar"),
        "active": ("boolean", "bool"),
        "created_at": ("timestamp",),
        "updated_at": ("timestamp",),
        "extra": ("jsonb", "json"),
    }


async def validate_public_users_table_or_raise() -> None:
    """
    If ``public.users`` already exists, ensure it matches the migrated runtime.

    ``create_all`` does not alter existing tables; a wrong manual ``users`` table
    must be dropped before bootstrap.
    """
    async with engine.connect() as conn:
        r = await conn.execute(
            text(
                """
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'users'
                """
            )
        )
        if r.scalar_one_or_none() is None:
            return

        r2 = await conn.execute(
            text(
                """
                SELECT a.attname::text AS col,
                       pg_catalog.format_type(a.atttypid, a.atttypmod) AS typ
                FROM pg_catalog.pg_attribute a
                JOIN pg_catalog.pg_class c ON a.attrelid = c.oid
                JOIN pg_catalog.pg_namespace n ON c.relnamespace = n.oid
                WHERE n.nspname = 'public' AND c.relname = 'users'
                  AND a.attnum > 0 AND NOT a.attisdropped
                """
            )
        )
        found = {row[0]: str(row[1]).lower() for row in r2.fetchall()}

        missing_core = USERS_TABLE_CORE_COLUMNS - found.keys()
        if missing_core:
            raise RuntimeError(
                "public.users exists but is missing required columns "
                f"{sorted(missing_core)}. "
                "Drop it with: DROP TABLE IF EXISTS public.users CASCADE; "
                "then re-run the schema bootstrap."
            )

        expectations = _users_column_type_expectations()
        for col in USERS_TABLE_CORE_COLUMNS:
            typ = found[col]
            allowed = expectations[col]
            if not any(a in typ for a in allowed):
                raise RuntimeError(
                    f"public.users column {col!r} has type {typ!r}; expected a type containing "
                    f"one of {allowed}. Drop the table and re-run bootstrap."
                )

        if "extra" in found:
            typ = found["extra"]
            if not any(a in typ for a in expectations["extra"]):
                raise RuntimeError(
                    f"public.users.extra has type {typ!r}; expected jsonb/json. "
                    "Drop the table and re-run bootstrap."
                )


async def bootstrap_postgresql_schema() -> None:
    """
    One-time / ops: create all ORM tables and legacy JSON/document tables used by the app.

    Safe to re-run: uses ``IF NOT EXISTS`` / ``create_all`` with checkfirst. Does not
    drop data. Run after ``DATABASE_URL`` points at the target database (e.g. Supabase).
    """
    import_all_declarative_models()
    await validate_public_users_table_or_raise()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text(USERS_EXTRA_COLUMN_SQL))
        await conn.execute(text(CLIENTS_TABLE_SQL))
        await conn.execute(text(CLIENTS_INDEX_SQL))
        await conn.execute(text(CONTRACTS_TABLE_SQL))
        await conn.execute(text(CONTRACTS_INDEX_SQL))
        await conn.execute(text(CONTRACTS_INDEX_PAYLOAD_CLIENT_SQL))
        await conn.execute(text(APP_DOCUMENTS_TABLE_SQL))
        await conn.execute(text(APP_DOCUMENTS_INDEX_SQL))
        await conn.execute(text(APP_DOCUMENTS_INDEX_STATUS_SQL))
        await conn.execute(text(APP_DOCUMENTS_INDEX_AUDITOR_SQL))
        await conn.execute(text("SELECT 1"))


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
    extra: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )


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

APP_DOCUMENTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS app_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection TEXT NOT NULL,
    doc_id TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ,
    UNIQUE (collection, doc_id)
)
"""

APP_DOCUMENTS_INDEX_SQL = (
    "CREATE INDEX IF NOT EXISTS ix_app_documents_collection_created "
    "ON app_documents (collection, created_at DESC)"
)

APP_DOCUMENTS_INDEX_STATUS_SQL = (
    "CREATE INDEX IF NOT EXISTS ix_app_documents_coll_status "
    "ON app_documents (collection, ((payload->>'status')))"
)

APP_DOCUMENTS_INDEX_AUDITOR_SQL = (
    "CREATE INDEX IF NOT EXISTS ix_app_documents_coll_auditor "
    "ON app_documents (collection, ((payload->>'auditor_id')))"
)

USERS_EXTRA_COLUMN_SQL = (
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS extra JSONB NOT NULL DEFAULT '{}'::jsonb"
)


async def connect_db() -> None:
    """
    Verify PostgreSQL connectivity.

    Full DDL (users, clients, contracts, app_documents, indexes) is applied by
    ``bootstrap_postgresql_schema()`` — run ``python scripts/bootstrap_postgres_schema.py``
    once per new database (e.g. Supabase).

    For local development against an empty database, set:
    ``BAYAN_SCHEMA_BOOTSTRAP_ON_CONNECT=1`` to run bootstrap automatically on each
    process start (not recommended for production).
    """
    boot = os.environ.get("BAYAN_SCHEMA_BOOTSTRAP_ON_CONNECT", "").strip().lower()
    if boot in ("1", "true", "yes", "on"):
        await bootstrap_postgresql_schema()
        return
    async with engine.begin() as conn:
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
    "bootstrap_postgresql_schema",
    "close_db",
    "connect_db",
    "db",
    "engine",
    "import_all_declarative_models",
    "validate_public_users_table_or_raise",
]
