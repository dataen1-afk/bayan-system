"""
Auditor records in PostgreSQL via ``app_documents`` (collection ``auditors``).
"""
from __future__ import annotations

from typing import Optional

import app_documents_pg as doc_pg


async def list_auditors_filtered(
    *,
    status: Optional[str] = None,
    specialization: Optional[str] = None,
    sort_by_name: bool = True,
    fetch_limit: int = 5000,
    max_results: Optional[int] = None,
) -> list[dict]:
    """Load up to ``fetch_limit`` rows from PG, filter, optionally sort by name, then cap at ``max_results``."""
    rows = await doc_pg.list_ordered(doc_pg.C_AUDITORS, fetch_limit)
    if status:
        rows = [a for a in rows if a.get("status") == status]
    if specialization:
        rows = [a for a in rows if specialization in (a.get("specializations") or [])]
    if sort_by_name:
        rows = sorted(rows, key=lambda a: str(a.get("name", "")).lower())
    if max_results is not None:
        rows = rows[:max_results]
    return rows


async def adjust_current_assignments_delta(auditor_id: str, delta: int) -> None:
    aid = str(auditor_id).strip()
    if not aid:
        return
    aud = await doc_pg.get_by_doc_id(doc_pg.C_AUDITORS, aid)
    if not aud:
        return
    n = int(aud.get("current_assignments") or 0) + delta
    await doc_pg.merge_set_by_doc_id(doc_pg.C_AUDITORS, aid, {"current_assignments": n})
