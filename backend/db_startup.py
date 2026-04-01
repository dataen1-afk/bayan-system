"""
MongoDB startup: ping, ensure collections, seed roles and default admin.

If the cluster is unreachable at process start (e.g. ServerSelectionTimeoutError),
startup logs and returns without raising so the ASGI app can still boot (health,
OpenAPI, recovery routes). DB-backed handlers will fail until Mongo is available.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from database import DB_NAME, DB_NAME_SOURCE, client, db
from auth import hash_password
from role_permissions import ROLE_PERMISSIONS

logger = logging.getLogger(__name__)

DEFAULT_ADMIN_EMAIL = "admin@bayan.com"
DEFAULT_ADMIN_PASSWORD = "123456"

# True only after ping + init completed without fatal error in this run.
mongodb_startup_succeeded: bool = False


async def run_database_startup(app_logger: Optional[logging.Logger] = None) -> None:
    global mongodb_startup_succeeded
    log = app_logger or logger
    mongodb_startup_succeeded = False

    try:
        await client.admin.command("ping")
    except Exception as e:
        log.error(
            "MongoDB unreachable at startup (ping failed). API will start without DB init; "
            "fix connectivity or wait for Atlas then retry requests. Error: %s",
            e,
            exc_info=True,
        )
        return

    try:
        log.info(
            "MongoDB OK | database=%s | %s",
            DB_NAME,
            DB_NAME_SOURCE,
        )

        existing = set(await db.list_collection_names())
        for coll in ("users", "roles", "defaults"):
            if coll not in existing:
                await db.create_collection(coll)
                log.info("Created collection: %s", coll)

        roles_count = await db.roles.count_documents({})
        if roles_count == 0:
            docs = [{"key": k, **v} for k, v in ROLE_PERMISSIONS.items()]
            if docs:
                await db.roles.insert_many(docs)
            log.info("Seeded default roles (%d roles)", len(docs))
        else:
            log.debug("Roles already seeded (%d documents); skip", roles_count)

        admin = await db.users.find_one({"email": DEFAULT_ADMIN_EMAIL})
        if not admin:
            uid = str(uuid.uuid4())
            await db.users.insert_one(
                {
                    "id": uid,
                    "name": "Administrator",
                    "email": DEFAULT_ADMIN_EMAIL,
                    "role": "admin",
                    "password": hash_password(DEFAULT_ADMIN_PASSWORD),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            log.info("Created default admin user (%s)", DEFAULT_ADMIN_EMAIL)
        else:
            log.debug("Default admin exists; skip creation")

        mongodb_startup_succeeded = True
    except Exception as e:
        log.error(
            "MongoDB ping succeeded but startup init failed (collections/seed). "
            "API continues; inspect DB permissions/schema. Error: %s",
            e,
            exc_info=True,
        )
