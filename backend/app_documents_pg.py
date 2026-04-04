"""
Generic PostgreSQL document store using ``app_documents`` (collection + doc_id + JSONB payload).

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

SQL_INSERT = text(
    """
    INSERT INTO app_documents (collection, doc_id, payload, created_at)
    VALUES (:collection, :doc_id, CAST(:payload AS jsonb), :created_at)
    """
)

SQL_GET_BY_DOC_ID = text(
    """
    SELECT doc_id, payload, created_at
    FROM app_documents
    WHERE collection = :collection AND doc_id = :doc_id
    """
)

_PAYLOAD_FIELD_WHITELIST = frozenset(
    {
        "access_token",
        "application_form_id",
        "proposal_access_token",
        "proposal_id",
        "audit_id",
        "auditor_id",
        "email",
        "job_order_id",
        "stage1_plan_id",
        "stage2_plan_id",
    }
)


def _sql_payload_field(field: str) -> str:
    if field not in _PAYLOAD_FIELD_WHITELIST:
        raise ValueError(f"app_documents: unsupported payload field {field!r}")
    return field

SQL_LIST_ORDERED = text(
    """
    SELECT doc_id, payload, created_at
    FROM app_documents
    WHERE collection = :collection
    ORDER BY created_at DESC
    LIMIT :limit
    """
)

SQL_LIST_CLIENT_INFO = text(
    """
    SELECT doc_id, payload, created_at
    FROM app_documents
    WHERE collection = :collection
      AND payload ? 'client_info'
    ORDER BY created_at DESC
    LIMIT :limit
    """
)

SQL_UPDATE_PAYLOAD = text(
    """
    UPDATE app_documents
    SET payload = CAST(:payload AS jsonb), updated_at = now()
    WHERE collection = :collection AND doc_id = :doc_id
    RETURNING doc_id
    """
)

SQL_COUNT_ALL = text(
    """
    SELECT COUNT(*)::bigint AS n FROM app_documents WHERE collection = :collection
    """
)

SQL_COUNT_STATUS = text(
    """
    SELECT COUNT(*)::bigint AS n
    FROM app_documents
    WHERE collection = :collection AND (payload->>'status') = :status
    """
)

SQL_COUNT_CREATED_BETWEEN = text(
    """
    SELECT COUNT(*)::bigint AS n
    FROM app_documents
    WHERE collection = :collection
      AND (payload->>'created_at') >= :start_iso
      AND (payload->>'created_at') < :end_iso
    """
)

SQL_DELETE_BY_COLLECTION = text(
    """
    DELETE FROM app_documents WHERE collection = :collection
    """
)

SQL_DELETE_BY_DOC_ID = text(
    """
    DELETE FROM app_documents
    WHERE collection = :collection AND doc_id = :doc_id
    """
)


def _json_safe(obj: Any) -> Any:
    return json.loads(json.dumps(obj, default=str))


def _coerce_row_ts(d: dict) -> datetime:
    raw = d.get("created_at")
    if isinstance(raw, datetime):
        return raw if raw.tzinfo else raw.replace(tzinfo=timezone.utc)
    if isinstance(raw, str):
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    return datetime.now(timezone.utc)


def materialize(doc_id: str, payload: Any, row_created_at: datetime | None) -> dict[str, Any]:
    p: dict[str, Any] = dict(payload) if isinstance(payload, dict) else {}
    if doc_id and not p.get("id"):
        p["id"] = doc_id
    return p


def row_to_doc(row: dict) -> dict[str, Any]:
    return materialize(str(row["doc_id"]), row["payload"], row["created_at"])


async def insert_document(collection: str, doc: dict[str, Any]) -> None:
    d = _json_safe(doc)
    if not d.get("id"):
        d["id"] = str(uuid.uuid4())
    doc_id = str(d["id"])
    row_ts = _coerce_row_ts(d)
    payload_json = json.dumps(d, default=str, ensure_ascii=False)
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(
                SQL_INSERT,
                {
                    "collection": collection,
                    "doc_id": doc_id,
                    "payload": payload_json,
                    "created_at": row_ts,
                },
            )
            await session.commit()
    except SQLAlchemyError as e:
        logger.warning("app_documents insert %s: %s", collection, e)
        raise


async def get_by_doc_id(collection: str, doc_id: str) -> dict[str, Any] | None:
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(
                SQL_GET_BY_DOC_ID,
                {"collection": collection, "doc_id": str(doc_id).strip()},
            )
            row = r.mappings().first()
    except SQLAlchemyError as e:
        logger.warning("app_documents get_by_doc_id %s: %s", collection, e)
        raise
    if not row:
        return None
    return row_to_doc(dict(row))


async def get_by_payload_field(
    collection: str, field: str, value: str
) -> dict[str, Any] | None:
    f = _sql_payload_field(field)
    q = text(
        f"""
        SELECT doc_id, payload, created_at
        FROM app_documents
        WHERE collection = :collection AND (payload->>'{f}') = :value
        LIMIT 1
        """
    )
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(
                q, {"collection": collection, "value": str(value)}
            )
            row = r.mappings().first()
    except SQLAlchemyError as e:
        logger.warning("app_documents get_by_field %s: %s", collection, e)
        raise
    if not row:
        return None
    return row_to_doc(dict(row))


async def list_by_payload_field(
    collection: str, field: str, value: str, limit: int = 500
) -> list[dict[str, Any]]:
    """List documents where ``payload->>field`` equals ``value`` (field must be whitelisted)."""
    f = _sql_payload_field(field)
    q = text(
        f"""
        SELECT doc_id, payload, created_at
        FROM app_documents
        WHERE collection = :collection AND (payload->>'{f}') = :value
        ORDER BY created_at DESC
        LIMIT :limit
        """
    )
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(
                q,
                {"collection": collection, "value": str(value), "limit": limit},
            )
            rows = r.mappings().all()
    except SQLAlchemyError as e:
        logger.warning("app_documents list_by_field %s: %s", collection, e)
        raise
    return [row_to_doc(dict(x)) for x in rows]


async def list_ordered(collection: str, limit: int = 1000) -> list[dict[str, Any]]:
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(
                SQL_LIST_ORDERED, {"collection": collection, "limit": limit}
            )
            rows = r.mappings().all()
    except SQLAlchemyError as e:
        logger.warning("app_documents list %s: %s", collection, e)
        raise
    return [row_to_doc(dict(x)) for x in rows]


async def list_with_client_info(collection: str, limit: int = 1000) -> list[dict[str, Any]]:
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(
                SQL_LIST_CLIENT_INFO, {"collection": collection, "limit": limit}
            )
            rows = r.mappings().all()
    except SQLAlchemyError as e:
        logger.warning("app_documents list client_info %s: %s", collection, e)
        raise
    return [row_to_doc(dict(x)) for x in rows]


async def replace_payload(collection: str, doc_id: str, new_payload: dict[str, Any]) -> bool:
    d = _json_safe(new_payload)
    d["id"] = str(d.get("id") or doc_id)
    payload_json = json.dumps(d, default=str, ensure_ascii=False)
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(
                SQL_UPDATE_PAYLOAD,
                {
                    "collection": collection,
                    "doc_id": str(doc_id),
                    "payload": payload_json,
                },
            )
            await session.commit()
            row = r.first()
    except SQLAlchemyError as e:
        logger.warning("app_documents replace %s: %s", collection, e)
        raise
    return row is not None


async def merge_set_by_doc_id(
    collection: str, doc_id: str, set_fields: dict[str, Any]
) -> bool:
    cur = await get_by_doc_id(collection, doc_id)
    if not cur:
        return False
    merged = {**cur, **set_fields}
    return await replace_payload(collection, doc_id, merged)


async def merge_set_by_payload_field(
    collection: str, field: str, value: str, set_fields: dict[str, Any]
) -> bool:
    cur = await get_by_payload_field(collection, field, value)
    if not cur:
        return False
    did = str(cur.get("id") or "")
    if not did:
        return False
    merged = {**cur, **set_fields}
    return await replace_payload(collection, did, merged)


async def count_all(collection: str) -> int:
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(SQL_COUNT_ALL, {"collection": collection})
            n = r.mappings().one()["n"]
    except SQLAlchemyError as e:
        logger.warning("app_documents count_all %s: %s", collection, e)
        raise
    return int(n)


async def count_status(collection: str, status: str) -> int:
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(
                SQL_COUNT_STATUS, {"collection": collection, "status": status}
            )
            n = r.mappings().one()["n"]
    except SQLAlchemyError as e:
        logger.warning("app_documents count_status %s: %s", collection, e)
        raise
    return int(n)


async def count_status_in(collection: str, statuses: list[str]) -> int:
    if not statuses:
        return 0
    total = 0
    for s in statuses:
        total += await count_status(collection, s)
    return total


async def delete_by_doc_id(collection: str, doc_id: str) -> bool:
    """Delete a single document by collection + doc_id."""
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(
                SQL_DELETE_BY_DOC_ID,
                {"collection": collection, "doc_id": str(doc_id).strip()},
            )
            await session.commit()
            n = r.rowcount
    except SQLAlchemyError as e:
        logger.warning("app_documents delete_one %s: %s", collection, e)
        raise
    return bool(n and n > 0)


async def delete_all_in_collection(collection: str) -> int:
    """Delete all app_documents rows for a collection; returns deleted row count."""
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(SQL_DELETE_BY_COLLECTION, {"collection": collection})
            await session.commit()
            n = r.rowcount
    except SQLAlchemyError as e:
        logger.warning("app_documents delete_all %s: %s", collection, e)
        raise
    return int(n) if n is not None and n >= 0 else 0


async def count_created_between(
    collection: str, start_iso: str, end_iso: str
) -> int:
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(
                SQL_COUNT_CREATED_BETWEEN,
                {
                    "collection": collection,
                    "start_iso": start_iso,
                    "end_iso": end_iso,
                },
            )
            n = r.mappings().one()["n"]
    except SQLAlchemyError as e:
        logger.warning("app_documents count_created %s: %s", collection, e)
        raise
    return int(n)


# Collection name constants
C_APPLICATION_FORMS = "application_forms"
C_PROPOSALS = "proposals"
C_CERTIFICATION_AGREEMENTS = "certification_agreements"
C_AUDIT_SCHEDULES = "audit_schedules"
C_AUDIT_ASSIGNMENTS = "audit_assignments"
C_SITES = "sites"
C_AUDITORS = "auditors"
C_JOB_ORDERS = "job_orders"
C_STAGE1_AUDIT_PLANS = "stage1_audit_plans"
C_STAGE1_AUDIT_REPORTS = "stage1_audit_reports"
C_STAGE2_AUDIT_PLANS = "stage2_audit_plans"
C_STAGE2_AUDIT_REPORTS = "stage2_audit_reports"
C_OPENING_CLOSING_MEETINGS = "opening_closing_meetings"
C_AUDITOR_NOTES = "auditor_notes"
C_NONCONFORMITY_REPORTS = "nonconformity_reports"
