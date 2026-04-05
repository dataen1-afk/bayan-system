"""
PostgreSQL ``users`` table (AsyncSessionLocal + ``sqlalchemy.text``).

Legacy Mongo user documents map to columns plus JSONB ``extra`` for profile/calendar fields.
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

SQL_SELECT_BY_ID = text(
    """
    SELECT id::text AS id, name, email, password, role, active,
           created_at, updated_at, COALESCE(extra, '{}'::jsonb) AS extra
    FROM users
    WHERE id = CAST(:id AS uuid)
    """
)

SQL_SELECT_BY_EMAIL = text(
    """
    SELECT id::text AS id, name, email, password, role, active,
           created_at, updated_at, COALESCE(extra, '{}'::jsonb) AS extra
    FROM users
    WHERE lower(trim(email)) = lower(trim(:email_norm))
       OR email = :email_raw
    LIMIT 1
    """
)

SQL_LIST_ALL = text(
    """
    SELECT id::text AS id, name, email, password, role, active,
           created_at, updated_at, COALESCE(extra, '{}'::jsonb) AS extra
    FROM users
    ORDER BY created_at DESC
    LIMIT 1000
    """
)

SQL_LIST_BY_ROLE = text(
    """
    SELECT id::text AS id, name, email, password, role, active,
           created_at, updated_at, COALESCE(extra, '{}'::jsonb) AS extra
    FROM users
    WHERE role = :role
    ORDER BY created_at DESC
    LIMIT 1000
    """
)

SQL_COUNT = text("SELECT COUNT(*)::bigint AS n FROM users")

SQL_DELETE_BY_ID = text("DELETE FROM users WHERE id = CAST(:id AS uuid)")

SQL_INSERT = text(
    """
    INSERT INTO users (id, name, email, password, role, active, created_at, updated_at, extra)
    VALUES (
        CAST(:id AS uuid), :name, :email, :password, :role, :active,
        :created_at, :updated_at, CAST(:extra AS jsonb)
    )
    """
)

SQL_UPDATE_ROLE = text(
    """
    UPDATE users SET role = :role, updated_at = :updated_at
    WHERE id = CAST(:id AS uuid)
    """
)

SQL_UPDATE_FULL = text(
    """
    UPDATE users
    SET name = :name, email = :email, password = :password, role = :role,
        updated_at = :updated_at, extra = CAST(:extra AS jsonb)
    WHERE id = CAST(:id AS uuid)
    """
)

SQL_UPDATE_GOOGLE_TOKENS = text(
    """
    UPDATE users
    SET extra = jsonb_set(
            COALESCE(extra, '{}'::jsonb),
            '{google_tokens}',
            CAST(:tokens AS jsonb),
            true
        ),
        updated_at = :updated_at
    WHERE lower(trim(email)) = lower(trim(:email_norm))
       OR email = :email_raw
    """
)

SQL_CLEAR_GOOGLE_TOKENS = text(
    """
    UPDATE users
    SET extra = COALESCE(extra, '{}'::jsonb) - 'google_tokens',
        updated_at = :updated_at
    WHERE lower(trim(email)) = lower(trim(:email_norm))
       OR email = :email_raw
    """
)


def _normalize_extra(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return dict(raw)
    if isinstance(raw, str):
        try:
            o = json.loads(raw)
            return dict(o) if isinstance(o, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def _iso(dt: Any) -> str | None:
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    if isinstance(dt, datetime):
        return dt.isoformat()
    return str(dt)


def mapping_to_legacy_user(m: dict[str, Any], *, include_password: bool) -> dict[str, Any]:
    extra = _normalize_extra(m.get("extra"))
    d: dict[str, Any] = {
        "id": str(m["id"]),
        "name": m["name"],
        "email": m["email"],
        "role": m["role"],
        "active": m.get("active", True),
        "created_at": _iso(m.get("created_at")),
        "updated_at": _iso(m.get("updated_at")),
    }
    for k, v in extra.items():
        if k in d:
            continue
        d[k] = v
    if include_password:
        d["password"] = m.get("password") or ""
    return d


async def list_users(*, include_password: bool = False) -> list[dict[str, Any]]:
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(SQL_LIST_ALL)
            rows = r.mappings().all()
    except SQLAlchemyError:
        raise
    out = []
    for row in rows:
        d = mapping_to_legacy_user(dict(row), include_password=include_password)
        if not include_password:
            d.pop("password", None)
        out.append(d)
    return out


async def list_users_by_role(
    role: str, *, include_password: bool = False
) -> list[dict[str, Any]]:
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(SQL_LIST_BY_ROLE, {"role": role})
            rows = r.mappings().all()
    except SQLAlchemyError:
        raise
    out = []
    for row in rows:
        d = mapping_to_legacy_user(dict(row), include_password=include_password)
        if not include_password:
            d.pop("password", None)
        out.append(d)
    return out


async def get_by_id(user_id: str, *, include_password: bool = True) -> dict[str, Any] | None:
    try:
        uuid.UUID(str(user_id).strip())
    except (ValueError, TypeError):
        return None
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(SQL_SELECT_BY_ID, {"id": str(user_id).strip()})
            row = r.mappings().first()
    except SQLAlchemyError:
        raise
    if not row:
        return None
    return mapping_to_legacy_user(dict(row), include_password=include_password)


async def get_by_email(email: str, *, include_password: bool = True) -> dict[str, Any] | None:
    email_raw = str(email).strip()
    email_norm = email_raw.lower()
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(
                SQL_SELECT_BY_EMAIL,
                {"email_norm": email_norm, "email_raw": email_raw},
            )
            row = r.mappings().first()
    except SQLAlchemyError:
        raise
    if not row:
        return None
    return mapping_to_legacy_user(dict(row), include_password=include_password)


async def count_users() -> int:
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(SQL_COUNT)
            n = r.mappings().one()["n"]
    except SQLAlchemyError:
        raise
    return int(n)


async def delete_user(user_id: str) -> bool:
    try:
        uuid.UUID(str(user_id).strip())
    except (ValueError, TypeError):
        return False
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(SQL_DELETE_BY_ID, {"id": str(user_id).strip()})
            await session.commit()
            n = r.rowcount
    except SQLAlchemyError:
        raise
    return bool(n and n > 0)


async def insert_user_legacy(doc: dict[str, Any]) -> None:
    """Insert from a legacy-shaped document (flat keys; profile fields go into ``extra``)."""
    uid = str(doc.get("id") or uuid.uuid4())
    try:
        uuid.UUID(uid)
    except (ValueError, TypeError):
        uid = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    created_raw = doc.get("created_at")
    if isinstance(created_raw, str):
        try:
            created_at = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
        except ValueError:
            created_at = now
    elif isinstance(created_raw, datetime):
        created_at = created_raw
    else:
        created_at = now
    extra_keys = (
        "name_ar",
        "phone",
        "department",
        "created_by",
        "google_tokens",
    )
    extra = {k: doc[k] for k in extra_keys if k in doc and doc[k] is not None}
    active = doc.get("active")
    if active is None:
        active = True
    updated_at = doc.get("updated_at") or created_at
    if isinstance(updated_at, str):
        try:
            updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        except ValueError:
            updated_at = created_at
    elif not isinstance(updated_at, datetime):
        updated_at = created_at
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(
                SQL_INSERT,
                {
                    "id": uid,
                    "name": doc.get("name") or "",
                    "email": str(doc.get("email") or "").lower().strip(),
                    "password": doc.get("password") or "",
                    "role": doc.get("role") or "client",
                    "active": active,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "extra": json.dumps(extra, default=str, ensure_ascii=False),
                },
            )
            await session.commit()
    except SQLAlchemyError:
        logger.warning(
            "users_pg.insert_user_legacy failed id=%s email=%s",
            uid,
            doc.get("email"),
            exc_info=True,
        )
        raise


async def update_role(user_id: str, new_role: str) -> bool:
    try:
        uuid.UUID(str(user_id).strip())
    except (ValueError, TypeError):
        return False
    now = datetime.now(timezone.utc)
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(
                SQL_UPDATE_ROLE,
                {"id": str(user_id).strip(), "role": new_role, "updated_at": now},
            )
            await session.commit()
            n = r.rowcount
    except SQLAlchemyError:
        raise
    return bool(n and n > 0)


async def update_user_merged(
    user_id: str,
    *,
    top_updates: dict[str, Any],
    extra_updates: dict[str, Any],
    new_password_hash: str | None,
) -> bool:
    cur = await get_by_id(user_id, include_password=True)
    if not cur:
        return False
    name = top_updates.get("name", cur.get("name"))
    email = str(top_updates.get("email", cur.get("email") or "")).lower().strip()
    role = top_updates.get("role", cur.get("role"))
    pwd = new_password_hash if new_password_hash is not None else cur.get("password") or ""
    now = datetime.now(timezone.utc)
    extra_keys = (
        "name_ar",
        "phone",
        "department",
        "created_by",
        "google_tokens",
    )
    extra = {k: cur[k] for k in extra_keys if k in cur}
    for k, v in extra_updates.items():
        if v is not None:
            extra[k] = v
    if "google_tokens" in top_updates:
        extra["google_tokens"] = top_updates["google_tokens"]
    try:
        async with AsyncSessionLocal() as session:
            r = await session.execute(
                SQL_UPDATE_FULL,
                {
                    "id": str(user_id).strip(),
                    "name": name,
                    "email": email,
                    "password": pwd,
                    "role": role,
                    "updated_at": now,
                    "extra": json.dumps(extra, default=str, ensure_ascii=False),
                },
            )
            await session.commit()
            n = r.rowcount
    except SQLAlchemyError:
        raise
    return bool(n and n > 0)


async def set_google_tokens_by_email(google_account_email: str, tokens: dict[str, Any]) -> None:
    email_raw = str(google_account_email).strip()
    email_norm = email_raw.lower()
    now = datetime.now(timezone.utc)
    tokens_json = json.dumps(tokens, default=str, ensure_ascii=False)
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(
                SQL_UPDATE_GOOGLE_TOKENS,
                {
                    "email_norm": email_norm,
                    "email_raw": email_raw,
                    "tokens": tokens_json,
                    "updated_at": now,
                },
            )
            await session.commit()
    except SQLAlchemyError:
        raise


async def clear_google_tokens_by_email(bayan_email: str) -> None:
    email_raw = str(bayan_email).strip()
    email_norm = email_raw.lower()
    now = datetime.now(timezone.utc)
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(
                SQL_CLEAR_GOOGLE_TOKENS,
                {"email_norm": email_norm, "email_raw": email_raw, "updated_at": now},
            )
            await session.commit()
    except SQLAlchemyError:
        raise


async def email_exists(email: str) -> bool:
    return (await get_by_email(email, include_password=False)) is not None


async def upsert_reset_admin(*, email: str, password_hash: str, role: str) -> None:
    """Internal reset: ensure admin row exists with given password and role."""
    email_norm = str(email).lower().strip()
    existing = await get_by_email(email_norm, include_password=True)
    now = datetime.now(timezone.utc)
    if existing:
        await update_user_merged(
            existing["id"],
            top_updates={"email": email_norm, "role": role},
            extra_updates={},
            new_password_hash=password_hash,
        )
        return
    await insert_user_legacy(
        {
            "id": str(uuid.uuid4()),
            "name": "Administrator",
            "email": email_norm,
            "role": role,
            "password": password_hash,
            "created_at": now.isoformat(),
            "active": True,
        }
    )
