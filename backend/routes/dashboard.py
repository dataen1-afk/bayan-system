"""
Dashboard Analytics API - Provides statistics for admin dashboard widgets.

Reads from PostgreSQL ``app_documents`` (no Mongo ``db``).
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError

from auth import get_current_user
from role_permissions import UserRole
from dashboard_pg import (
    count_by_auditor,
    count_by_status,
    list_by_collection,
    list_notifications_since,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard Analytics"])

DB_UNAVAILABLE_DETAIL = "Database temporarily unavailable. Please try again shortly."

# Same policy as server.require_admin (management + functional managers), not auth.require_admin (admin-only).
_DASHBOARD_MANAGEMENT_ROLES = (
    UserRole.SYSTEM_ADMIN,
    UserRole.CEO,
    UserRole.GENERAL_MANAGER,
    UserRole.ADMIN,
)
_DASHBOARD_MANAGER_ROLES = (
    UserRole.QUALITY_MANAGER,
    UserRole.CERTIFICATION_MANAGER,
    UserRole.MARKETING_MANAGER,
    UserRole.FINANCIAL_MANAGER,
    UserRole.HR_MANAGER,
)


async def require_dashboard_access(current_user: dict = Depends(get_current_user)) -> dict:
    role = current_user.get("role")
    if role in _DASHBOARD_MANAGEMENT_ROLES or role in _DASHBOARD_MANAGER_ROLES:
        return current_user
    raise HTTPException(status_code=403, detail="Management access required")


@router.get("/stats")
async def get_dashboard_stats(current_user: dict = Depends(require_dashboard_access)):
    """Get comprehensive dashboard statistics"""
    now = datetime.now(timezone.utc)
    try:
        all_certs = await list_by_collection("certificates", 1000)
        all_forms = await list_by_collection("application_forms", 1000)
        all_proposals = await list_by_collection("proposals", 1000)
        all_auditors = await list_by_collection("auditors", 100)
        pending_approvals = await count_by_status(
            "approval_workflows", "in_progress"
        )
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        recent_notifications = await list_notifications_since(today_start, 20)
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE_DETAIL)

    expiring_30 = []
    expiring_60 = []
    expiring_90 = []

    for cert in all_certs:
        if cert.get("status") == "active" and cert.get("expiry_date"):
            try:
                expiry = (
                    datetime.fromisoformat(
                        cert["expiry_date"].replace("Z", "+00:00")
                    )
                    if isinstance(cert["expiry_date"], str)
                    else cert["expiry_date"]
                )
                if expiry.tzinfo is None:
                    expiry = expiry.replace(tzinfo=timezone.utc)

                days_until_expiry = (expiry - now).days

                cert_info = {
                    "id": cert.get("id"),
                    "certificate_number": cert.get("certificate_number"),
                    "organization_name": cert.get("organization_name"),
                    "standards": cert.get("standards", []),
                    "expiry_date": cert.get("expiry_date"),
                    "days_until_expiry": days_until_expiry,
                }

                if 0 <= days_until_expiry <= 30:
                    expiring_30.append(cert_info)
                elif 30 < days_until_expiry <= 60:
                    expiring_60.append(cert_info)
                elif 60 < days_until_expiry <= 90:
                    expiring_90.append(cert_info)
            except Exception:
                continue

    pending_forms = len([f for f in all_forms if f.get("status") == "pending"])
    submitted_forms = len([f for f in all_forms if f.get("status") == "submitted"])

    pending_proposals = len(
        [p for p in all_proposals if p.get("status") in ["pending", "sent"]]
    )

    signed_proposals = [p for p in all_proposals if p.get("status") == "agreement_signed"]
    total_revenue = sum(p.get("total_amount", 0) for p in signed_proposals)

    current_month_start = now.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    monthly_revenue = 0
    for p in signed_proposals:
        try:
            response_date = p.get("client_response_date")
            if response_date:
                if isinstance(response_date, str):
                    response_date = datetime.fromisoformat(
                        response_date.replace("Z", "+00:00")
                    )
                if response_date.tzinfo is None:
                    response_date = response_date.replace(tzinfo=timezone.utc)
                if response_date >= current_month_start:
                    monthly_revenue += p.get("total_amount", 0)
        except Exception:
            continue

    auditor_workload = []
    try:
        for auditor in all_auditors:
            auditor_name = auditor.get("name", "Unknown")
            auditor_id = auditor.get("id")

            job_count = await count_by_auditor("job_orders", str(auditor_id or ""))
            stage1_count = await count_by_auditor("stage1_audit_plans", str(auditor_id or ""))
            stage2_count = await count_by_auditor("stage2_audit_plans", str(auditor_id or ""))

            total_tasks = job_count + stage1_count + stage2_count

            auditor_workload.append(
                {
                    "id": auditor_id,
                    "name": auditor_name,
                    "name_ar": auditor.get("name_ar", auditor_name),
                    "total_tasks": total_tasks,
                    "job_orders": job_count,
                    "stage1_audits": stage1_count,
                    "stage2_audits": stage2_count,
                }
            )
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE_DETAIL)

    auditor_workload.sort(key=lambda x: x["total_tasks"], reverse=True)

    today_forms = len([f for f in all_forms if _is_today(f.get("created_at"), today_start)])
    today_proposals = len(
        [p for p in all_proposals if _is_today(p.get("issued_date"), today_start)]
    )

    return {
        "certificates": {
            "total": len(all_certs),
            "active": len([c for c in all_certs if c.get("status") == "active"]),
            "expiring_30_days": expiring_30,
            "expiring_60_days": expiring_60,
            "expiring_90_days": expiring_90,
            "expiring_count": {
                "30_days": len(expiring_30),
                "60_days": len(expiring_60),
                "90_days": len(expiring_90),
            },
        },
        "forms": {
            "total": len(all_forms),
            "pending": pending_forms,
            "submitted": submitted_forms,
        },
        "proposals": {
            "total": len(all_proposals),
            "pending": pending_proposals,
            "signed": len(signed_proposals),
        },
        "approvals": {
            "pending": pending_approvals,
        },
        "revenue": {
            "total": total_revenue,
            "monthly": monthly_revenue,
            "monthly_target": 500000,
            "currency": "SAR",
        },
        "auditor_workload": auditor_workload[:10],
        "today_activity": {
            "notifications": recent_notifications[:10],
            "new_forms": today_forms,
            "new_proposals": today_proposals,
        },
    }


def _is_today(date_value, today_start):
    """Check if a date is today"""
    if not date_value:
        return False
    try:
        if isinstance(date_value, str):
            date_value = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
        if date_value.tzinfo is None:
            date_value = date_value.replace(tzinfo=timezone.utc)
        return date_value >= today_start
    except Exception:
        return False


@router.get("/quick-actions")
async def get_quick_actions(current_user: dict = Depends(require_dashboard_access)):
    """Get counts for quick action badges"""
    try:
        pending_forms = await count_by_status("application_forms", "submitted")
        pending_approvals = await count_by_status(
            "approval_workflows", "in_progress"
        )
        pending_reviews = await count_by_status("technical_reviews", "pending")
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE_DETAIL)

    return {
        "pending_forms": pending_forms,
        "pending_approvals": pending_approvals,
        "pending_reviews": pending_reviews,
    }
