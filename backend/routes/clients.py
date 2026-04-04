"""
Organization clients registry (PostgreSQL). CRUD at /api/clients.

All DB access uses SQLAlchemy ``text()`` + AsyncSessionLocal — no Mongo ``db``.
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from auth import require_admin
from database import AsyncSessionLocal

logger = logging.getLogger(__name__)

DB_UNAVAILABLE_DETAIL = "Database temporarily unavailable. Please try again shortly."

router = APIRouter(tags=["Clients"])


class ClientCreate(BaseModel):
    company_name: Optional[str] = None
    national_address: Optional[str] = None
    tax_number: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    payload: dict[str, Any] = Field(default_factory=dict)


class ClientUpdate(BaseModel):
    company_name: Optional[str] = None
    national_address: Optional[str] = None
    tax_number: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    payload: Optional[dict[str, Any]] = None


class ClientResponse(BaseModel):
    id: str
    company_name: Optional[str] = None
    national_address: Optional[str] = None
    tax_number: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    payload: dict[str, Any] = Field(default_factory=dict)


def _parse_uuid(client_id: str) -> uuid.UUID:
    try:
        return uuid.UUID(str(client_id).strip())
    except ValueError as e:
        raise HTTPException(status_code=422, detail="Invalid client id") from e


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


def _row_to_response(row: dict) -> ClientResponse:
    return ClientResponse(
        id=str(row["id"]),
        company_name=row.get("company_name"),
        national_address=row.get("national_address"),
        tax_number=row.get("tax_number"),
        mobile=row.get("mobile"),
        email=row.get("email"),
        created_at=row["created_at"],
        updated_at=row.get("updated_at"),
        payload=_normalize_payload(row.get("payload")),
    )


SQL_LIST = text(
    """
    SELECT id::text AS id, company_name, national_address, tax_number, mobile, email,
           created_at, updated_at, payload
    FROM clients
    ORDER BY created_at DESC
    """
)

SQL_INSERT = text(
    """
    INSERT INTO clients (company_name, national_address, tax_number, mobile, email, payload)
    VALUES (:company_name, :national_address, :tax_number, :mobile, :email, CAST(:payload AS jsonb))
    RETURNING id::text AS id, company_name, national_address, tax_number, mobile, email,
              created_at, updated_at, payload
    """
)

SQL_SELECT_ONE = text(
    """
    SELECT id::text AS id, company_name, national_address, tax_number, mobile, email,
           created_at, updated_at, payload
    FROM clients
    WHERE id = CAST(:id AS uuid)
    """
)

SQL_UPDATE = text(
    """
    UPDATE clients SET
        company_name = :company_name,
        national_address = :national_address,
        tax_number = :tax_number,
        mobile = :mobile,
        email = :email,
        payload = CAST(:payload AS jsonb),
        updated_at = now()
    WHERE id = CAST(:id AS uuid)
    RETURNING id::text AS id, company_name, national_address, tax_number, mobile, email,
              created_at, updated_at, payload
    """
)

SQL_DELETE = text(
    """
    DELETE FROM clients
    WHERE id = CAST(:id AS uuid)
    RETURNING id::text AS id
    """
)


@router.get("/clients", response_model=list[ClientResponse])
async def list_clients(_: dict = Depends(require_admin)):
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(SQL_LIST)
            rows = result.mappings().all()
    except SQLAlchemyError as e:
        logger.warning("clients list: %s", e)
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE_DETAIL)
    return [_row_to_response(dict(r)) for r in rows]


@router.post("/clients", response_model=ClientResponse)
async def create_client(body: ClientCreate, _: dict = Depends(require_admin)):
    payload_json = json.dumps(body.payload if body.payload is not None else {})
    params = {
        "company_name": body.company_name,
        "national_address": body.national_address,
        "tax_number": body.tax_number,
        "mobile": body.mobile,
        "email": body.email,
        "payload": payload_json,
    }
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(SQL_INSERT, params)
            await session.commit()
            row = result.mappings().one()
    except SQLAlchemyError as e:
        logger.warning("clients create: %s", e)
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE_DETAIL)
    return _row_to_response(dict(row))


@router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    body: ClientUpdate,
    _: dict = Depends(require_admin),
):
    uid = _parse_uuid(client_id)
    try:
        async with AsyncSessionLocal() as session:
            cur = await session.execute(SQL_SELECT_ONE, {"id": str(uid)})
            existing = cur.mappings().first()
            if not existing:
                raise HTTPException(status_code=404, detail="Client not found")

            merged = dict(existing)
            if body.company_name is not None:
                merged["company_name"] = body.company_name
            if body.national_address is not None:
                merged["national_address"] = body.national_address
            if body.tax_number is not None:
                merged["tax_number"] = body.tax_number
            if body.mobile is not None:
                merged["mobile"] = body.mobile
            if body.email is not None:
                merged["email"] = body.email
            if body.payload is not None:
                merged["payload"] = body.payload
            else:
                merged["payload"] = _normalize_payload(merged.get("payload"))

            params = {
                "id": str(uid),
                "company_name": merged.get("company_name"),
                "national_address": merged.get("national_address"),
                "tax_number": merged.get("tax_number"),
                "mobile": merged.get("mobile"),
                "email": merged.get("email"),
                "payload": json.dumps(merged["payload"]),
            }
            result = await session.execute(SQL_UPDATE, params)
            await session.commit()
            row = result.mappings().one()
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.warning("clients update: %s", e)
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE_DETAIL)
    return _row_to_response(dict(row))


@router.delete("/clients/{client_id}")
async def delete_client(client_id: str, _: dict = Depends(require_admin)):
    uid = _parse_uuid(client_id)
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(SQL_DELETE, {"id": str(uid)})
            await session.commit()
            row = result.first()
    except SQLAlchemyError as e:
        logger.warning("clients delete: %s", e)
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE_DETAIL)
    if not row:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Client deleted", "id": row[0]}
