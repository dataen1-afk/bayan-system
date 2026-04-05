"""
PostgreSQL persistence for service ``contracts`` (legacy quotation/proposal contracts).

Uses AsyncSessionLocal + SQLAlchemy ``text()`` only — no Mongo ``db``.
Payload JSONB holds API fields: quotation_id, proposal_id, pdf_path, client_id (string).
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import AsyncSessionLocal

logger = logging.getLogger(__name__)

SQL_INSERT = text(
    """
    INSERT INTO contracts (
        contract_number, status, client_id, project_name, company_name, client_name, payload
    )
    VALUES (
        :contract_number, :status, :client_id_uuid, :project_name, :company_name, :client_name,
        CAST(:payload AS jsonb)
    )
    RETURNING id::text AS id, created_at, payload
    """
)

SQL_LIST_ALL = text(
    """
    SELECT id::text AS id, contract_number, status,
           client_id::text AS client_id_col,
           project_name, company_name, client_name,
           created_at, updated_at, payload
    FROM contracts
    ORDER BY created_at DESC
    LIMIT 2000
    """
)

SQL_LIST_FOR_CLIENT = text(
    """
    SELECT id::text AS id, contract_number, status,
           client_id::text AS client_id_col,
           project_name, company_name, client_name,
           created_at, updated_at, payload
    FROM contracts
    WHERE (payload->>'client_id') = :user_id
       OR (client_id IS NOT NULL AND client_id::text = :user_id)
    ORDER BY created_at DESC
    LIMIT 2000
    """
)

SQL_GET_BY_ID = text(
    """
    SELECT id::text AS id, contract_number, status,
           client_id::text AS client_id_col,
           project_name, company_name, client_name,
           created_at, updated_at, payload
    FROM contracts
    WHERE id = CAST(:id AS uuid)
    """
)

SQL_DELETE_ALL = text("DELETE FROM contracts")

SQL_COUNT_ALL = text("SELECT COUNT(*)::bigint AS n FROM contracts")


def _normalize_payload(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            out = json.loads(raw)
            return out if isinstance(out, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def row_to_contract_api(row: dict) -> dict[str, Any]:
    """Shape expected by ``Contract`` Pydantic model in server."""
    p = _normalize_payload(row.get("payload"))
    cid_col = row.get("client_id_col")
    legacy_cid = p.get("client_id", "")
    if legacy_cid is None:
        legacy_cid = ""
    client_id_out = legacy_cid if legacy_cid else (cid_col or "")
    created = row["created_at"]
    if isinstance(created, str):
        created = datetime.fromisoformat(created.replace("Z", "+00:00"))
    return {
        "id": str(row["id"]),
        "quotation_id": p.get("quotation_id") or "",
        "proposal_id": p.get("proposal_id") or "",
        "client_id": str(client_id_out),
        "pdf_path": p.get("pdf_path") or "",
        "created_at": created,
    }


def _parse_client_uuid(client_id_str: str) -> uuid.UUID | None:
    if not client_id_str or not str(client_id_str).strip():
        return None
    try:
        return uuid.UUID(str(client_id_str).strip())
    except ValueError:
        return None


async def insert_contract_record(
    *,
    quotation_id: str = "",
    proposal_id: str = "",
    client_id: str = "",
    pdf_path: str = "",
    contract_number: str | None = None,
    status: str | None = "active",
    project_name: str | None = None,
    company_name: str | None = None,
    client_name: str | None = None,
) -> dict[str, Any]:
    payload = {
        "quotation_id": quotation_id or "",
        "proposal_id": proposal_id or "",
        "pdf_path": pdf_path or "",
        "client_id": client_id or "",
    }
    client_uuid = _parse_client_uuid(client_id)
    params = {
        "contract_number": contract_number,
        "status": status,
        "client_id_uuid": str(client_uuid) if client_uuid else None,
        "project_name": project_name,
        "company_name": company_name,
        "client_name": client_name,
        "payload": json.dumps(payload),
    }
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(SQL_INSERT, params)
            await session.commit()
            row = result.mappings().one()
    except SQLAlchemyError as e:
        logger.warning("contracts insert: %s", e)
        raise
    d = dict(row)
    d["client_id_col"] = str(client_uuid) if client_uuid else None
    return row_to_contract_api(d)


async def list_contracts_for_user(*, is_client: bool, user_id: str) -> list[dict[str, Any]]:
    try:
        async with AsyncSessionLocal() as session:
            if is_client:
                result = await session.execute(SQL_LIST_FOR_CLIENT, {"user_id": str(user_id)})
            else:
                result = await session.execute(SQL_LIST_ALL)
            rows = result.mappings().all()
    except SQLAlchemyError as e:
        logger.warning("contracts list: %s", e)
        raise
    return [row_to_contract_api(dict(r)) for r in rows]


async def delete_all_contracts() -> int:
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(SQL_DELETE_ALL)
            await session.commit()
            n = r.rowcount
    except SQLAlchemyError as e:
        logger.warning("contracts delete_all: %s", e)
        raise
    return int(n) if n is not None and n >= 0 else 0


async def count_contracts() -> int:
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(SQL_COUNT_ALL)
            n = r.mappings().one()["n"]
    except SQLAlchemyError as e:
        logger.warning("contracts count: %s", e)
        raise
    return int(n)


async def get_contract_by_id(contract_id: str) -> dict[str, Any] | None:
    try:
        uuid.UUID(str(contract_id).strip())
    except (ValueError, TypeError):
        return None
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(SQL_GET_BY_ID, {"id": str(contract_id).strip()})
            row = result.mappings().first()
    except SQLAlchemyError as e:
        logger.warning("contracts get: %s", e)
        raise
    if not row:
        return None
    return row_to_contract_api(dict(row))


DB_UNAVAILABLE = "Database temporarily unavailable. Please try again shortly."
