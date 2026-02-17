"""
Auditor management routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from datetime import datetime, timezone

from database import db
from auth import get_current_user
from models.auditor import Auditor, AuditorCreate, AuditorAvailability

router = APIRouter(prefix="/auditors", tags=["Auditors"])
security = HTTPBearer()


@router.get("")
async def get_auditors(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    status: Optional[str] = None,
    specialization: Optional[str] = None
):
    """Get all auditors with optional filtering"""
    await get_current_user(credentials)
    
    query = {}
    if status:
        query["status"] = status
    if specialization:
        query["specializations"] = specialization
    
    auditors = await db.auditors.find(query, {"_id": 0}).sort("name", 1).to_list(100)
    
    # Calculate current assignments for each auditor
    for auditor in auditors:
        assignments = await db.audit_assignments.count_documents({
            "auditor_id": auditor['id'],
            "status": {"$in": ["assigned", "confirmed"]}
        })
        auditor['current_assignments'] = assignments
    
    return auditors


@router.get("/available")
async def get_available_auditors(
    date: str,
    specialization: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get auditors available on a specific date"""
    await get_current_user(credentials)
    
    query = {"status": "active"}
    if specialization:
        query["specializations"] = specialization
    
    auditors = await db.auditors.find(query, {"_id": 0}).to_list(100)
    
    available_auditors = []
    for auditor in auditors:
        # Check if auditor has specific unavailability for this date
        is_available = auditor.get('default_available', True)
        for avail in auditor.get('availability', []):
            if avail.get('date') == date:
                is_available = avail.get('is_available', True)
                break
        
        if is_available:
            # Check if auditor is already assigned to an audit on this date
            existing = await db.audit_schedules.count_documents({
                "scheduled_date": date,
                "auditors": {"$regex": auditor['id']}
            })
            
            # Check max audits per month
            monthly_count = await db.audit_assignments.count_documents({
                "auditor_id": auditor['id'],
                "status": {"$in": ["assigned", "confirmed", "completed"]}
            })
            
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
        existing = await db.auditors.find_one({"email": auditor_data.email})
        if existing:
            raise HTTPException(status_code=400, detail="Auditor with this email already exists")
    
    auditor = Auditor(**auditor_data.model_dump())
    auditor_doc = auditor.model_dump()
    auditor_doc['created_at'] = auditor_doc['created_at'].isoformat()
    
    await db.auditors.insert_one(auditor_doc)
    
    return {"message": "Auditor created", "auditor_id": auditor.id}


@router.get("/{auditor_id}")
async def get_auditor(
    auditor_id: str, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get auditor details"""
    await get_current_user(credentials)
    
    auditor = await db.auditors.find_one({"id": auditor_id}, {"_id": 0})
    if not auditor:
        raise HTTPException(status_code=404, detail="Auditor not found")
    
    # Get recent assignments
    assignments = await db.audit_assignments.find(
        {"auditor_id": auditor_id},
        {"_id": 0}
    ).sort("assigned_at", -1).to_list(20)
    
    auditor['recent_assignments'] = assignments
    
    return auditor


@router.put("/{auditor_id}")
async def update_auditor(
    auditor_id: str, 
    updates: dict, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update auditor details"""
    await get_current_user(credentials)
    
    auditor = await db.auditors.find_one({"id": auditor_id})
    if not auditor:
        raise HTTPException(status_code=404, detail="Auditor not found")
    
    updates['updated_at'] = datetime.now(timezone.utc).isoformat()
    await db.auditors.update_one({"id": auditor_id}, {"$set": updates})
    
    return {"message": "Auditor updated"}


@router.delete("/{auditor_id}")
async def delete_auditor(
    auditor_id: str, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete an auditor (soft delete - sets status to inactive)"""
    await get_current_user(credentials)
    
    auditor = await db.auditors.find_one({"id": auditor_id})
    if not auditor:
        raise HTTPException(status_code=404, detail="Auditor not found")
    
    # Check for active assignments
    active_assignments = await db.audit_assignments.count_documents({
        "auditor_id": auditor_id,
        "status": {"$in": ["assigned", "confirmed"]}
    })
    
    if active_assignments > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete auditor with {active_assignments} active assignments"
        )
    
    # Soft delete
    await db.auditors.update_one(
        {"id": auditor_id},
        {"$set": {"status": "inactive", "updated_at": datetime.now(timezone.utc).isoformat()}}
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
    
    auditor = await db.auditors.find_one({"id": auditor_id})
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
    
    await db.auditors.update_one(
        {"id": auditor_id},
        {"$set": {
            "availability": current_availability,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": "Availability updated"}
