"""
PostgreSQL startup: ``connect_db`` (connectivity check only by default), seed default admin.

Schema DDL is **not** applied on every start. Run once per database:

    python scripts/bootstrap_postgres_schema.py

Optional: ``BAYAN_SCHEMA_BOOTSTRAP_ON_CONNECT=1`` runs bootstrap inside ``connect_db``
(local empty DB only; avoid in production).

If the database is unreachable at process start, startup logs and returns without
raising so the ASGI app can still boot (health, OpenAPI). Auth will return 503
until PostgreSQL is available.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select

from auth import hash_password
from database import AsyncSessionLocal, UserRow, connect_db

logger = logging.getLogger(__name__)

DEFAULT_ADMIN_EMAIL = "admin@bayan.com"
DEFAULT_ADMIN_PASSWORD = "123456"

# True only after connect_db + admin seed path completed without fatal error in this run.
database_startup_succeeded: bool = False

# Backward-compatible alias
mongodb_startup_succeeded = False


async def run_database_startup(app_logger: Optional[logging.Logger] = None) -> None:
    global database_startup_succeeded, mongodb_startup_succeeded
    log = app_logger or logger
    database_startup_succeeded = False
    mongodb_startup_succeeded = False

    try:
        await connect_db()
    except Exception as e:
        log.error(
            "PostgreSQL unreachable or connect_db failed at startup. "
            "API will start without DB init; fix DATABASE_URL or network then retry. Error: %s",
            e,
            exc_info=True,
        )
        return

    try:
        log.info("PostgreSQL OK | seeding default admin if missing (%s)", DEFAULT_ADMIN_EMAIL)

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserRow).where(UserRow.email == DEFAULT_ADMIN_EMAIL)
            )
            admin = result.scalar_one_or_none()
            if not admin:
                now = datetime.now(timezone.utc)
                uid = uuid.uuid4()
                session.add(
                    UserRow(
                        id=uid,
                        name="Administrator",
                        email=DEFAULT_ADMIN_EMAIL,
                        role="admin",
                        password=hash_password(DEFAULT_ADMIN_PASSWORD),
                        active=True,
                        created_at=now,
                        updated_at=now,
                        extra={},
                    )
                )
                await session.commit()
                log.info("Created default admin user (%s)", DEFAULT_ADMIN_EMAIL)
            else:
                log.debug("Default admin exists; skip creation")

        database_startup_succeeded = True
        mongodb_startup_succeeded = True
    except Exception as e:
        log.error(
            "PostgreSQL connect OK but startup seed failed. "
            "API continues; inspect DB permissions/schema. Error: %s",
            e,
            exc_info=True,
        )
