"""
Auditor management routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timezone

from database import db
from auth import require_admin
from models.auditor import Auditor, AuditorCreate, AuditorAvailability, AuditAssignment

router = APIRouter(prefix="/auditors", tags=["Auditors"])


@router.get("", response_model=List[dict])
async def get_auditors(
    status: Optional[str] = None,
    specialization: Optional[str] = None,
    current_user: dict = Depends(require_admin)
):
    """Get all auditors with optional filtering"""
    query = {}
    if status:
        query["status"] = status
    if specialization:
        query["specializations"] = specialization
    
    auditors = await db.auditors.find(query, {"_id": 0}).to_list(1000)
    return auditors


@router.get("/available")
async def get_available_auditors(
    date: Optional[str] = None,
    standard: Optional[str] = None,
    current_user: dict = Depends(require_admin)
):
    """Get auditors available on a specific date and/or with specific specialization"""
    query = {"status": "active"}
    
    if standard:
        query["specializations"] = standard
    
    auditors = await db.auditors.find(query, {"_id": 0}).to_list(1000)
    
    if date:
        # Filter by availability
        available_auditors = []
        for auditor in auditors:
            availability = auditor.get("availability", [])
            # Check if date is in unavailable list
            is_unavailable = any(
                a.get("date") == date and not a.get("available", True)
                for a in availability
            )
            if not is_unavailable:
                available_auditors.append(auditor)
        return available_auditors
    
    return auditors


@router.post("", response_model=dict)
async def create_auditor(
    auditor_data: AuditorCreate,
    current_user: dict = Depends(require_admin)
):
    """Create a new auditor"""
    auditor = Auditor(
        name=auditor_data.name,
        name_ar=auditor_data.name_ar,
        email=auditor_data.email,
        phone=auditor_data.phone,
        mobile=auditor_data.mobile,
        employee_id=auditor_data.employee_id,
        certification_level=auditor_data.certification_level,
        specializations=auditor_data.specializations,
        years_experience=auditor_data.years_experience,
        max_audits_per_month=auditor_data.max_audits_per_month,
        notes=auditor_data.notes
    )
    
    await db.auditors.insert_one(auditor.model_dump())
    return auditor.model_dump()


@router.get("/{auditor_id}", response_model=dict)
async def get_auditor(
    auditor_id: str,
    current_user: dict = Depends(require_admin)
):
    """Get a specific auditor by ID"""
    auditor = await db.auditors.find_one({"id": auditor_id}, {"_id": 0})
    if not auditor:
        raise HTTPException(status_code=404, detail="Auditor not found")
    return auditor


@router.put("/{auditor_id}", response_model=dict)
async def update_auditor(
    auditor_id: str,
    auditor_data: AuditorCreate,
    current_user: dict = Depends(require_admin)
):
    """Update an auditor"""
    update_data = auditor_data.model_dump()
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.auditors.update_one(
        {"id": auditor_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Auditor not found")
    
    return await db.auditors.find_one({"id": auditor_id}, {"_id": 0})


@router.delete("/{auditor_id}")
async def delete_auditor(
    auditor_id: str,
    current_user: dict = Depends(require_admin)
):
    """Soft delete an auditor (set status to inactive)"""
    result = await db.auditors.update_one(
        {"id": auditor_id},
        {"$set": {"status": "inactive", "updated_at": datetime.now(timezone.utc)}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Auditor not found")
    
    return {"status": "success", "message": "Auditor deactivated"}


@router.post("/{auditor_id}/availability")
async def set_auditor_availability(
    auditor_id: str,
    availability_data: AuditorAvailability,
    current_user: dict = Depends(require_admin)
):
    """Set auditor availability for a specific date"""
    # Get current auditor
    auditor = await db.auditors.find_one({"id": auditor_id})
    if not auditor:
        raise HTTPException(status_code=404, detail="Auditor not found")
    
    # Update availability list
    availability = auditor.get("availability", [])
    
    # Remove existing entry for this date if any
    availability = [a for a in availability if a.get("date") != availability_data.date]
    
    # Add new entry
    availability.append(availability_data.model_dump())
    
    await db.auditors.update_one(
        {"id": auditor_id},
        {"$set": {"availability": availability, "updated_at": datetime.now(timezone.utc)}}
    )
    
    return {"status": "success"}
