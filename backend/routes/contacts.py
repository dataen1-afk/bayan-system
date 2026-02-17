"""
Contact history/CRM routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timezone

from database import db
from auth import require_admin
from models.contact import ContactRecord, ContactRecordCreate

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.get("", response_model=List[dict])
async def get_contacts(
    customer_id: Optional[str] = None,
    current_user: dict = Depends(require_admin)
):
    """Get all contact records with optional filtering by customer"""
    query = {}
    if customer_id:
        query["customer_id"] = customer_id
    
    contacts = await db.contacts.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return contacts


@router.post("", response_model=dict)
async def create_contact(
    contact_data: ContactRecordCreate,
    current_user: dict = Depends(require_admin)
):
    """Create a new contact record"""
    contact = ContactRecord(
        customer_id=contact_data.customer_id,
        customer_name=contact_data.customer_name,
        contact_type=contact_data.contact_type,
        subject=contact_data.subject,
        notes=contact_data.notes,
        follow_up_date=contact_data.follow_up_date,
        contact_date=contact_data.contact_date,
        contacted_by=current_user.get("user_id", "")
    )
    
    await db.contacts.insert_one(contact.model_dump())
    return contact.model_dump()


@router.put("/{contact_id}/follow-up")
async def mark_follow_up_completed(
    contact_id: str,
    current_user: dict = Depends(require_admin)
):
    """Mark a follow-up as completed"""
    result = await db.contacts.update_one(
        {"id": contact_id},
        {"$set": {"follow_up_completed": True}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Contact record not found")
    
    return {"status": "success"}


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: str,
    current_user: dict = Depends(require_admin)
):
    """Delete a contact record"""
    result = await db.contacts.delete_one({"id": contact_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contact record not found")
    return {"status": "success"}
