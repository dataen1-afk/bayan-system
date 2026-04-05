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

from auth import get_current_user, security
from dependencies import create_notification
import app_documents_pg as doc_pg

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

    await doc_pg.insert_document(doc_pg.C_RFQ_REQUESTS, rfq_record)

    await create_notification(
        notification_type="rfq_received",
        title="New Quote Request",
        title_ar="طلب عرض سعر جديد",
        message=f"New RFQ from {data.company_name} - Standards: {', '.join(data.standards)}",
        message_ar=f"طلب عرض سعر جديد من {data.company_name} - المعايير: {', '.join(data.standards)}",
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

    await doc_pg.insert_document(doc_pg.C_CONTACT_MESSAGES, contact_record)

    await create_notification(
        notification_type="contact_received",
        title="New Contact Message",
        title_ar="رسالة تواصل جديدة",
        message=f"Message from {data.name}: {data.subject}",
        message_ar=f"رسالة من {data.name}: {data.subject}",
        related_id=contact_record['id'],
        related_type="contact"
    )

    return {"message": "Message sent successfully"}

# ================= ADMIN ENDPOINTS (Auth Required) =================

def _filter_by_status(items: list, status: str | None) -> list:
    if not status or status == "all":
        return items
    return [x for x in items if x.get("status") == status]


@router.get("/rfq-requests")
async def get_rfq_requests(
    status: str = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all RFQ requests (Admin only)"""
    await get_current_user(credentials)

    requests = await doc_pg.list_ordered(doc_pg.C_RFQ_REQUESTS, 1000)
    requests = _filter_by_status(requests, status)
    requests.sort(
        key=lambda x: str(x.get("created_at") or ""),
        reverse=True,
    )
    return requests

@router.put("/rfq-requests/{rfq_id}")
async def update_rfq_request(
    rfq_id: str,
    status: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update RFQ request status (Admin only)"""
    await get_current_user(credentials)

    ok = await doc_pg.merge_set_by_doc_id(
        doc_pg.C_RFQ_REQUESTS,
        rfq_id,
        {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()},
    )
    if not ok:
        raise HTTPException(status_code=404, detail="RFQ not found")
    return {"message": "RFQ updated successfully"}

@router.delete("/rfq-requests/{rfq_id}")
async def delete_rfq_request(
    rfq_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete an RFQ request (Admin only)"""
    await get_current_user(credentials)

    deleted = await doc_pg.delete_by_doc_id(doc_pg.C_RFQ_REQUESTS, rfq_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="RFQ not found")

    return {"message": "RFQ deleted successfully"}

@router.get("/contact-messages")
async def get_contact_messages(
    status: str = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all contact messages (Admin only)"""
    await get_current_user(credentials)

    messages = await doc_pg.list_ordered(doc_pg.C_CONTACT_MESSAGES, 1000)
    messages = _filter_by_status(messages, status)
    messages.sort(
        key=lambda x: str(x.get("created_at") or ""),
        reverse=True,
    )
    return messages

@router.put("/contact-messages/{message_id}")
async def update_contact_message(
    message_id: str,
    status: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update contact message status (Admin only)"""
    await get_current_user(credentials)

    ok = await doc_pg.merge_set_by_doc_id(
        doc_pg.C_CONTACT_MESSAGES,
        message_id,
        {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()},
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Contact message not found")
    return {"message": "Contact message updated successfully"}

@router.delete("/contact-messages/{message_id}")
async def delete_contact_message(
    message_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete a contact message (Admin only)"""
    await get_current_user(credentials)

    deleted = await doc_pg.delete_by_doc_id(doc_pg.C_CONTACT_MESSAGES, message_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Contact message not found")

    return {"message": "Contact message deleted successfully"}
