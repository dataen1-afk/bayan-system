"""
Contact history/CRM routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from database import db
from auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["Contacts"])
security = HTTPBearer()


# Pydantic models (matching monolith schema)
class ContactRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    customer_name: str = ""
    contact_type: str = "phone"  # phone, email, meeting, other
    subject: str = ""
    notes: str = ""
    contact_date: str = ""
    follow_up_date: str = ""
    follow_up_completed: bool = False
    created_by: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ContactRecordCreate(BaseModel):
    customer_id: str
    contact_type: str = "phone"
    subject: str = ""
    notes: str = ""
    contact_date: str = ""
    follow_up_date: str = ""


@router.get("")
async def get_contact_records(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    customer_id: Optional[str] = None
):
    """Get all contact records or filtered by customer"""
    await get_current_user(credentials)
    
    query = {}
    if customer_id:
        query["customer_id"] = customer_id
    
    contacts = await db.contact_records.find(query, {"_id": 0}).sort("contact_date", -1).to_list(1000)
    return contacts


@router.post("")
async def create_contact_record(
    contact_data: ContactRecordCreate, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new contact record"""
    current_user = await get_current_user(credentials)
    
    # Get customer name from form or proposal
    customer_name = ""
    form = await db.application_forms.find_one({"id": contact_data.customer_id}, {"_id": 0})
    if form:
        customer_name = form.get('client_info', {}).get('company_name', '')
    else:
        proposal = await db.proposals.find_one({"id": contact_data.customer_id}, {"_id": 0})
        if proposal:
            customer_name = proposal.get('organization_name', '')
    
    contact = ContactRecord(
        customer_id=contact_data.customer_id,
        customer_name=customer_name,
        contact_type=contact_data.contact_type,
        subject=contact_data.subject,
        notes=contact_data.notes,
        contact_date=contact_data.contact_date,
        follow_up_date=contact_data.follow_up_date,
        created_by=current_user.get('user_id', '')
    )
    
    contact_doc = contact.model_dump()
    contact_doc['created_at'] = contact_doc['created_at'].isoformat()
    
    await db.contact_records.insert_one(contact_doc)
    return {"message": "Contact record created", "id": contact.id}


@router.put("/{contact_id}/follow-up")
async def mark_follow_up_completed(
    contact_id: str, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Mark a follow-up as completed"""
    await get_current_user(credentials)
    
    await db.contact_records.update_one(
        {"id": contact_id},
        {"$set": {"follow_up_completed": True}}
    )
    return {"message": "Follow-up marked as completed"}


@router.delete("/{contact_id}")
async def delete_contact_record(
    contact_id: str, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete a contact record"""
    await get_current_user(credentials)
    await db.contact_records.delete_one({"id": contact_id})
    return {"message": "Contact record deleted"}
