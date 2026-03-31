"""
MongoDB startup: ping, ensure collections, seed roles and default admin.
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


async def run_database_startup(app_logger: Optional[logging.Logger] = None) -> None:
    log = app_logger or logger
    try:
        await client.admin.command("ping")
    except Exception as e:
        log.error("MongoDB connection failed: %s", e, exc_info=True)
        raise
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
