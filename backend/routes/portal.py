"""
Customer Portal Routes
Public RFQ and Contact form endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid

from dependencies import db, get_current_user, create_notification, security

router = APIRouter(tags=["Customer Portal"])

# ================= MODELS =================

class RFQRequest(BaseModel):
    """Request for Quotation submission"""
    company_name: str
    contact_name: str
    email: str
    phone: str
    employees: str = ""
    sites: str = "1"
    standards: List[str] = []
    message: str = ""

class ContactRequest(BaseModel):
    """Contact form submission"""
    name: str
    email: str
    subject: str
    message: str

# ================= PUBLIC ENDPOINTS (No Auth) =================

@router.post("/public/rfq")
async def submit_rfq(data: RFQRequest):
    """Submit a Request for Quotation from the customer portal"""
    
    rfq_record = {
        "id": str(uuid.uuid4()),
        "company_name": data.company_name,
        "contact_name": data.contact_name,
        "email": data.email,
        "phone": data.phone,
        "employees": data.employees,
        "sites": data.sites,
        "standards": data.standards,
        "message": data.message,
        "status": "new",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.rfq_requests.insert_one(rfq_record)
    
    await create_notification(
        notification_type="rfq_received",
        title="New Quote Request",
        message=f"New RFQ from {data.company_name} - Standards: {', '.join(data.standards)}",
        related_id=rfq_record['id'],
        related_type="rfq"
    )
    
    return {"message": "RFQ submitted successfully", "id": rfq_record['id']}

@router.post("/public/contact")
async def submit_contact_form(data: ContactRequest):
    """Submit a contact form message from the customer portal"""
    
    contact_record = {
        "id": str(uuid.uuid4()),
        "name": data.name,
        "email": data.email,
        "subject": data.subject,
        "message": data.message,
        "status": "unread",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.contact_messages.insert_one(contact_record)
    
    await create_notification(
        notification_type="contact_received",
        title="New Contact Message",
        message=f"Message from {data.name}: {data.subject}",
        related_id=contact_record['id'],
        related_type="contact"
    )
    
    return {"message": "Message sent successfully"}

# ================= ADMIN ENDPOINTS (Auth Required) =================

@router.get("/rfq-requests")
async def get_rfq_requests(
    status: str = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all RFQ requests (Admin only)"""
    await get_current_user(credentials)
    
    query = {}
    if status and status != 'all':
        query['status'] = status
    
    requests = await db.rfq_requests.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return requests

@router.put("/rfq-requests/{rfq_id}")
async def update_rfq_request(
    rfq_id: str,
    status: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update RFQ request status (Admin only)"""
    await get_current_user(credentials)
    
    await db.rfq_requests.update_one(
        {"id": rfq_id},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"message": "RFQ updated successfully"}

@router.delete("/rfq-requests/{rfq_id}")
async def delete_rfq_request(
    rfq_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete an RFQ request (Admin only)"""
    await get_current_user(credentials)
    
    result = await db.rfq_requests.delete_one({"id": rfq_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    return {"message": "RFQ deleted successfully"}

@router.get("/contact-messages")
async def get_contact_messages(
    status: str = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all contact messages (Admin only)"""
    await get_current_user(credentials)
    
    query = {}
    if status and status != 'all':
        query['status'] = status
    
    messages = await db.contact_messages.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return messages

@router.put("/contact-messages/{message_id}")
async def update_contact_message(
    message_id: str,
    status: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update contact message status (Admin only)"""
    await get_current_user(credentials)
    
    await db.contact_messages.update_one(
        {"id": message_id},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"message": "Contact message updated successfully"}

@router.delete("/contact-messages/{message_id}")
async def delete_contact_message(
    message_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete a contact message (Admin only)"""
    await get_current_user(credentials)
    
    result = await db.contact_messages.delete_one({"id": message_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contact message not found")
    
    return {"message": "Contact message deleted successfully"}
