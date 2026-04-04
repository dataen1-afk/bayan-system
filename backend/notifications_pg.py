"""
PostgreSQL notifications via ``app_documents`` (collection = 'notifications').

AsyncSessionLocal + ``text()`` only — no Mongo ``db``.
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import AsyncSessionLocal

logger = logging.getLogger(__name__)

COLLECTION = "notifications"

SQL_INSERT = text(
    """
    INSERT INTO app_documents (collection, doc_id, payload, created_at)
    VALUES (:collection, :doc_id, CAST(:payload AS jsonb), :created_at)
    """
)

SQL_LIST = text(
    """
    SELECT doc_id, payload, created_at
    FROM app_documents
    WHERE collection = :collection
      AND (
        :unread_only = false
        OR NOT COALESCE((payload->>'is_read')::boolean, false)
      )
    ORDER BY created_at DESC
    LIMIT :limit
    """
)

SQL_COUNT_UNREAD = text(
    """
    SELECT COUNT(*)::bigint AS n
    FROM app_documents
    WHERE collection = :collection
      AND NOT COALESCE((payload->>'is_read')::boolean, false)
    """
)

SQL_MARK_READ = text(
    """
    UPDATE app_documents
    SET payload = jsonb_set(
            COALESCE(payload, '{}'::jsonb),
            '{is_read}',
            'true'::jsonb,
            true
        ),
        updated_at = now()
    WHERE collection = :collection AND doc_id = :doc_id
    RETURNING doc_id
    """
)

SQL_DELETE_ALL = text(
    """
    DELETE FROM app_documents
    WHERE collection = :collection
    """
)


def _parse_created_at(val: Any) -> datetime:
    if isinstance(val, datetime):
        if val.tzinfo is None:
            return val.replace(tzinfo=timezone.utc)
        return val
    if isinstance(val, str):
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    return datetime.now(timezone.utc)


def _materialize_row(doc_id: str, payload: Any, row_created_at: datetime | None) -> dict[str, Any]:
    d: dict[str, Any] = dict(payload) if isinstance(payload, dict) else {}
    if doc_id and not d.get("id"):
        d["id"] = doc_id
    if row_created_at is not None and not d.get("created_at"):
        d["created_at"] = row_created_at.isoformat()
    return d


async def insert_notification_document(doc: dict[str, Any]) -> dict[str, Any]:
    """Persist one notification; returns the stored document (JSON-friendly)."""
    d = dict(doc)
    nid = str(d.get("id") or uuid.uuid4())
    d["id"] = nid
    if "is_read" not in d:
        d["is_read"] = False

    raw_ca = d.get("created_at")
    if raw_ca is None:
        row_ts = datetime.now(timezone.utc)
        d["created_at"] = row_ts.isoformat()
    elif isinstance(raw_ca, datetime):
        row_ts = raw_ca if raw_ca.tzinfo else raw_ca.replace(tzinfo=timezone.utc)
        d["created_at"] = row_ts.isoformat()
    else:
        row_ts = _parse_created_at(str(raw_ca))
        if not isinstance(raw_ca, str):
            d["created_at"] = row_ts.isoformat()

    payload_json = json.dumps(d, default=str, ensure_ascii=False)

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(
                SQL_INSERT,
                {
                    "collection": COLLECTION,
                    "doc_id": nid,
                    "payload": payload_json,
                    "created_at": row_ts,
                },
            )
            await session.commit()
    except SQLAlchemyError as e:
        logger.warning("notifications insert: %s", e)
        raise
    return d


async def list_notifications(*, limit: int, unread_only: bool) -> tuple[list[dict[str, Any]], int]:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                SQL_LIST,
                {
                    "collection": COLLECTION,
                    "unread_only": unread_only,
                    "limit": limit,
                },
            )
            rows = result.mappings().all()
            cres = await session.execute(
                SQL_COUNT_UNREAD, {"collection": COLLECTION}
            )
            unread = int(cres.mappings().one()["n"])
    except SQLAlchemyError as e:
        logger.warning("notifications list: %s", e)
        raise
    items = [_materialize_row(str(r["doc_id"]), r["payload"], r["created_at"]) for r in rows]
    return items, unread


async def mark_notification_read(notification_id: str) -> bool:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                SQL_MARK_READ,
                {"collection": COLLECTION, "doc_id": str(notification_id).strip()},
            )
            await session.commit()
            row = result.first()
    except SQLAlchemyError as e:
        logger.warning("notifications mark read: %s", e)
        raise
    return row is not None


async def delete_all_notifications() -> None:
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(SQL_DELETE_ALL, {"collection": COLLECTION})
            await session.commit()
    except SQLAlchemyError as e:
        logger.warning("notifications delete all: %s", e)
        raise
