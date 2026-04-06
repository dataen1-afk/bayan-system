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
from database import AsyncSessionLocal, UserRow, connect_db, describe_database_url_sanitized

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

    log.info(
        "bayan.db_startup: begin | %s",
        describe_database_url_sanitized(),
    )

    try:
        await connect_db()
    except Exception as e:
        log.error(
            "bayan.db_startup: connect_db FAILED (API will start without DB; auth may 503) | "
            "exc_type=%s exc_msg=%s | %s",
            type(e).__name__,
            str(e),
            describe_database_url_sanitized(),
            exc_info=True,
        )
        log.warning(
            "bayan.db_startup: SUMMARY | database_startup_succeeded=False | "
            "seed_ran=False | reason=connect_db_failed | exc_type=%s | exc_msg=%s | %s",
            type(e).__name__,
            str(e),
            describe_database_url_sanitized(),
        )
        return

    log.info(
        "bayan.db_startup: connect_db OK | %s",
        describe_database_url_sanitized(),
    )

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
        log.info(
            "bayan.db_startup: admin seed phase OK | database_startup_succeeded=True | %s",
            describe_database_url_sanitized(),
        )
        log.info(
            "bayan.db_startup: SUMMARY | database_startup_succeeded=True | seed_ran=True | "
            "reason=admin_seed_ok | exc_type=n/a | exc_msg=n/a | %s",
            describe_database_url_sanitized(),
        )
    except Exception as e:
        log.error(
            "bayan.db_startup: admin seed FAILED (connect_db had succeeded; inspect schema/permissions) | "
            "exc_type=%s exc_msg=%s | %s",
            type(e).__name__,
            str(e),
            describe_database_url_sanitized(),
            exc_info=True,
        )
        log.error(
            "bayan.db_startup: SUMMARY | database_startup_succeeded=False | seed_ran=attempted | "
            "reason=admin_seed_failed | exc_type=%s | exc_msg=%s | %s",
            type(e).__name__,
            str(e),
            describe_database_url_sanitized(),
        )
