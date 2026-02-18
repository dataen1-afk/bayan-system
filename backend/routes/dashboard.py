"""
Dashboard Analytics API - Provides statistics for admin dashboard widgets
"""
from fastapi import APIRouter, Depends
from datetime import datetime, timezone, timedelta
from typing import Optional

from database import db
from auth import require_admin

router = APIRouter(prefix="/dashboard", tags=["Dashboard Analytics"])


@router.get("/stats")
async def get_dashboard_stats(current_user: dict = Depends(require_admin)):
    """Get comprehensive dashboard statistics"""
    now = datetime.now(timezone.utc)
    
    # Certificate Statistics
    all_certs = await db.certificates.find({}, {"_id": 0}).to_list(1000)
    
    # Certificates expiring in 30/60/90 days
    expiring_30 = []
    expiring_60 = []
    expiring_90 = []
    
    for cert in all_certs:
        if cert.get("status") == "active" and cert.get("expiry_date"):
            try:
                expiry = datetime.fromisoformat(cert["expiry_date"].replace("Z", "+00:00")) if isinstance(cert["expiry_date"], str) else cert["expiry_date"]
                if expiry.tzinfo is None:
                    expiry = expiry.replace(tzinfo=timezone.utc)
                
                days_until_expiry = (expiry - now).days
                
                cert_info = {
                    "id": cert.get("id"),
                    "certificate_number": cert.get("certificate_number"),
                    "organization_name": cert.get("organization_name"),
                    "standards": cert.get("standards", []),
                    "expiry_date": cert.get("expiry_date"),
                    "days_until_expiry": days_until_expiry
                }
                
                if 0 <= days_until_expiry <= 30:
                    expiring_30.append(cert_info)
                elif 30 < days_until_expiry <= 60:
                    expiring_60.append(cert_info)
                elif 60 < days_until_expiry <= 90:
                    expiring_90.append(cert_info)
            except Exception as e:
                continue
    
    # Application Forms Statistics
    all_forms = await db.application_forms.find({}, {"_id": 0}).to_list(1000)
    pending_forms = len([f for f in all_forms if f.get("status") == "pending"])
    submitted_forms = len([f for f in all_forms if f.get("status") == "submitted"])
    
    # Proposals Statistics
    all_proposals = await db.proposals.find({}, {"_id": 0}).to_list(1000)
    pending_proposals = len([p for p in all_proposals if p.get("status") in ["pending", "sent"]])
    
    # Pending Approvals
    pending_approvals = await db.approvals.count_documents({"status": "pending"})
    
    # Revenue Statistics
    signed_proposals = [p for p in all_proposals if p.get("status") == "agreement_signed"]
    total_revenue = sum(p.get("total_amount", 0) for p in signed_proposals)
    
    # Monthly revenue (current month)
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = 0
    for p in signed_proposals:
        try:
            response_date = p.get("client_response_date")
            if response_date:
                if isinstance(response_date, str):
                    response_date = datetime.fromisoformat(response_date.replace("Z", "+00:00"))
                if response_date.tzinfo is None:
                    response_date = response_date.replace(tzinfo=timezone.utc)
                if response_date >= current_month_start:
                    monthly_revenue += p.get("total_amount", 0)
        except Exception:
            continue
    
    # Auditor workload (count assigned audits per auditor)
    all_auditors = await db.auditors.find({}, {"_id": 0}).to_list(100)
    auditor_workload = []
    for auditor in all_auditors:
        # Count active assignments (job orders, audit plans assigned to this auditor)
        auditor_name = auditor.get("name", "Unknown")
        auditor_id = auditor.get("id")
        
        # Count from job orders
        job_count = await db.job_orders.count_documents({"auditor_id": auditor_id})
        
        # Count from stage 1 audit plans
        stage1_count = await db.stage1_audit_plans.count_documents({"auditor_id": auditor_id})
        
        # Count from stage 2 audit plans  
        stage2_count = await db.stage2_audit_plans.count_documents({"auditor_id": auditor_id})
        
        total_tasks = job_count + stage1_count + stage2_count
        
        auditor_workload.append({
            "id": auditor_id,
            "name": auditor_name,
            "name_ar": auditor.get("name_ar", auditor_name),
            "total_tasks": total_tasks,
            "job_orders": job_count,
            "stage1_audits": stage1_count,
            "stage2_audits": stage2_count
        })
    
    # Sort by total tasks descending
    auditor_workload.sort(key=lambda x: x["total_tasks"], reverse=True)
    
    # Today's Activity
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Recent notifications (last 24 hours as activity feed)
    recent_notifications = await db.notifications.find(
        {"created_at": {"$gte": today_start.isoformat()}},
        {"_id": 0}
    ).sort("created_at", -1).to_list(20)
    
    # Count today's activities by type
    today_forms = len([f for f in all_forms if _is_today(f.get("created_at"), today_start)])
    today_proposals = len([p for p in all_proposals if _is_today(p.get("issued_date"), today_start)])
    
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
                "90_days": len(expiring_90)
            }
        },
        "forms": {
            "total": len(all_forms),
            "pending": pending_forms,
            "submitted": submitted_forms
        },
        "proposals": {
            "total": len(all_proposals),
            "pending": pending_proposals,
            "signed": len(signed_proposals)
        },
        "approvals": {
            "pending": pending_approvals
        },
        "revenue": {
            "total": total_revenue,
            "monthly": monthly_revenue,
            "monthly_target": 500000,  # Configurable target
            "currency": "SAR"
        },
        "auditor_workload": auditor_workload[:10],  # Top 10 auditors
        "today_activity": {
            "notifications": recent_notifications[:10],
            "new_forms": today_forms,
            "new_proposals": today_proposals
        }
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
async def get_quick_actions(current_user: dict = Depends(require_admin)):
    """Get counts for quick action badges"""
    
    pending_forms = await db.application_forms.count_documents({"status": "submitted"})
    pending_approvals = await db.approvals.count_documents({"status": "pending"})
    pending_reviews = await db.technical_reviews.count_documents({"status": "pending"})
    
    return {
        "pending_forms": pending_forms,
        "pending_approvals": pending_approvals,
        "pending_reviews": pending_reviews
    }
