"""
Auditor management routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from typing import Optional
from datetime import datetime, timezone

import app_documents_pg as doc_pg
import auditors_pg
from auth import get_current_user, security
from models.auditor import Auditor, AuditorCreate, AuditorAvailability

router = APIRouter(prefix="/auditors", tags=["Auditors"])


@router.get("")
async def get_auditors(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    status: Optional[str] = None,
    specialization: Optional[str] = None
):
    """Get all auditors with optional filtering"""
    await get_current_user(credentials)
    
    auditors = await auditors_pg.list_auditors_filtered(
        status=status,
        specialization=specialization,
        sort_by_name=True,
        max_results=100,
    )
    all_assignments = await doc_pg.list_ordered(doc_pg.C_AUDIT_ASSIGNMENTS, 5000)
    
    for auditor in auditors:
        aid = str(auditor["id"])
        assignments = sum(
            1
            for x in all_assignments
            if str(x.get("auditor_id", "")) == aid
            and x.get("status") in ("assigned", "confirmed")
        )
        auditor["current_assignments"] = assignments
    
    return auditors


@router.get("/available")
async def get_available_auditors(
    date: str,
    specialization: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get auditors available on a specific date"""
    await get_current_user(credentials)
    
    auditors = await auditors_pg.list_auditors_filtered(
        status="active",
        specialization=specialization,
        sort_by_name=False,
        max_results=100,
    )
    audit_schedules_cache = await doc_pg.list_ordered(doc_pg.C_AUDIT_SCHEDULES, 3000)
    all_assignments = await doc_pg.list_ordered(doc_pg.C_AUDIT_ASSIGNMENTS, 5000)
    
    available_auditors = []
    for auditor in auditors:
        # Check if auditor has specific unavailability for this date
        is_available = auditor.get('default_available', True)
        for avail in auditor.get('availability', []):
            if avail.get('date') == date:
                is_available = avail.get('is_available', True)
                break
        
        if is_available:
            aid = str(auditor["id"])
            existing = sum(
                1
                for a in audit_schedules_cache
                if a.get("scheduled_date") == date and aid in str(a.get("auditors", ""))
            )
            
            monthly_count = sum(
                1
                for x in all_assignments
                if str(x.get("auditor_id", "")) == aid
                and x.get("status") in ("assigned", "confirmed", "completed")
            )
            
            auditor['is_available'] = existing == 0 and monthly_count < auditor.get('max_audits_per_month', 10)
            auditor['existing_audits_today'] = existing
            auditor['monthly_audits'] = monthly_count
            available_auditors.append(auditor)
    
    return available_auditors


@router.post("")
async def create_auditor(
    auditor_data: AuditorCreate, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new auditor"""
    await get_current_user(credentials)
    
    # Check if email already exists
    if auditor_data.email:
        existing = await doc_pg.get_by_payload_field(
            doc_pg.C_AUDITORS, "email", str(auditor_data.email).strip()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Auditor with this email already exists")
    
    auditor = Auditor(**auditor_data.model_dump())
    auditor_doc = auditor.model_dump()
    auditor_doc['created_at'] = auditor_doc['created_at'].isoformat()
    
    await doc_pg.insert_document(doc_pg.C_AUDITORS, auditor_doc)
    
    return {"message": "Auditor created", "auditor_id": auditor.id}


@router.get("/{auditor_id}")
async def get_auditor(
    auditor_id: str, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get auditor details"""
    await get_current_user(credentials)
    
    auditor = await doc_pg.get_by_doc_id(doc_pg.C_AUDITORS, auditor_id)
    if not auditor:
        raise HTTPException(status_code=404, detail="Auditor not found")
    
    candidates = await doc_pg.list_by_payload_field(
        doc_pg.C_AUDIT_ASSIGNMENTS, "auditor_id", auditor_id, 100
    )
    candidates.sort(key=lambda x: str(x.get("assigned_at", "")), reverse=True)
    auditor["recent_assignments"] = candidates[:20]
    
    return auditor


@router.put("/{auditor_id}")
async def update_auditor(
    auditor_id: str, 
    updates: dict, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update auditor details"""
    await get_current_user(credentials)
    
    auditor = await doc_pg.get_by_doc_id(doc_pg.C_AUDITORS, auditor_id)
    if not auditor:
        raise HTTPException(status_code=404, detail="Auditor not found")
    
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    await doc_pg.merge_set_by_doc_id(doc_pg.C_AUDITORS, auditor_id, updates)
    
    return {"message": "Auditor updated"}


@router.delete("/{auditor_id}")
async def delete_auditor(
    auditor_id: str, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete an auditor (soft delete - sets status to inactive)"""
    await get_current_user(credentials)
    
    auditor = await doc_pg.get_by_doc_id(doc_pg.C_AUDITORS, auditor_id)
    if not auditor:
        raise HTTPException(status_code=404, detail="Auditor not found")
    
    all_assignments = await doc_pg.list_ordered(doc_pg.C_AUDIT_ASSIGNMENTS, 5000)
    active_assignments = sum(
        1
        for x in all_assignments
        if str(x.get("auditor_id", "")) == str(auditor_id)
        and x.get("status") in ("assigned", "confirmed")
    )
    
    if active_assignments > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete auditor with {active_assignments} active assignments"
        )
    
    await doc_pg.merge_set_by_doc_id(
        doc_pg.C_AUDITORS,
        auditor_id,
        {"status": "inactive", "updated_at": datetime.now(timezone.utc).isoformat()},
    )
    
    return {"message": "Auditor deactivated"}


@router.post("/{auditor_id}/availability")
async def set_auditor_availability(
    auditor_id: str,
    availability_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Set auditor availability for specific dates"""
    await get_current_user(credentials)
    
    auditor = await doc_pg.get_by_doc_id(doc_pg.C_AUDITORS, auditor_id)
    if not auditor:
        raise HTTPException(status_code=404, detail="Auditor not found")
    
    # Update availability array
    current_availability = auditor.get('availability', [])
    date = availability_data.get('date')
    
    # Remove existing entry for this date
    current_availability = [a for a in current_availability if a.get('date') != date]
    
    # Add new entry
    current_availability.append({
        "date": date,
        "is_available": availability_data.get('is_available', True),
        "reason": availability_data.get('reason', '')
    })
    
    await doc_pg.merge_set_by_doc_id(
        doc_pg.C_AUDITORS,
        auditor_id,
        {
            "availability": current_availability,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    
    return {"message": "Availability updated"}
