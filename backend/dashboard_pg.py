"""
PostgreSQL-backed reads for dashboard analytics.

Stores denormalized documents in ``app_documents`` (collection + doc_id + payload JSONB).
Uses AsyncSessionLocal + ``text()`` only — no Mongo ``db``.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import AsyncSessionLocal

logger = logging.getLogger(__name__)

SQL_LIST = text(
    """
    SELECT doc_id, payload, created_at
    FROM app_documents
    WHERE collection = :collection
    ORDER BY created_at DESC
    LIMIT :limit
    """
)

SQL_COUNT_STATUS = text(
    """
    SELECT COUNT(*)::bigint AS n
    FROM app_documents
    WHERE collection = :collection
      AND (payload->>'status') = :status
    """
)

SQL_COUNT_AUDITOR = text(
    """
    SELECT COUNT(*)::bigint AS n
    FROM app_documents
    WHERE collection = :collection
      AND (payload->>'auditor_id') = :auditor_id
    """
)

SQL_LIST_NOTIFICATIONS = text(
    """
    SELECT doc_id, payload, created_at
    FROM app_documents
    WHERE collection = 'notifications'
      AND created_at >= :since
    ORDER BY created_at DESC
    LIMIT :limit
    """
)


def _materialize(doc_id: str, payload: Any, created_at: datetime | None) -> dict[str, Any]:
    d: dict[str, Any] = dict(payload) if isinstance(payload, dict) else {}
    if doc_id and not d.get("id"):
        d["id"] = doc_id
    if created_at is not None and d.get("created_at") is None:
        if created_at.tzinfo is not None:
            d["created_at"] = created_at.isoformat()
        else:
            d["created_at"] = created_at.replace(tzinfo=None).isoformat() + "Z"
    return d


async def list_by_collection(collection: str, limit: int) -> list[dict[str, Any]]:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                SQL_LIST, {"collection": collection, "limit": limit}
            )
            rows = result.mappings().all()
    except SQLAlchemyError as e:
        logger.warning("dashboard list %s: %s", collection, e)
        raise
    out: list[dict[str, Any]] = []
    for r in rows:
        out.append(_materialize(str(r["doc_id"]), r["payload"], r["created_at"]))
    return out


async def count_by_status(collection: str, status: str) -> int:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                SQL_COUNT_STATUS, {"collection": collection, "status": status}
            )
            row = result.mappings().one()
    except SQLAlchemyError as e:
        logger.warning("dashboard count %s %s: %s", collection, status, e)
        raise
    return int(row["n"])


async def count_by_auditor(collection: str, auditor_id: str) -> int:
    if auditor_id is None:
        return 0
    aid = str(auditor_id)
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                SQL_COUNT_AUDITOR, {"collection": collection, "auditor_id": aid}
            )
            row = result.mappings().one()
    except SQLAlchemyError as e:
        logger.warning("dashboard count auditor %s: %s", collection, e)
        raise
    return int(row["n"])


async def list_notifications_since(since: datetime, limit: int) -> list[dict[str, Any]]:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                SQL_LIST_NOTIFICATIONS, {"since": since, "limit": limit}
            )
            rows = result.mappings().all()
    except SQLAlchemyError as e:
        logger.warning("dashboard notifications: %s", e)
        raise
    out: list[dict[str, Any]] = []
    for r in rows:
        out.append(_materialize(str(r["doc_id"]), r["payload"], r["created_at"]))
    return out
