"""
Pre-Transfer Review Routes (BAC-F6-17)
Pre-Transfer Review and Transfer Decision endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from pathlib import Path
import uuid
import logging

from auth import get_current_user, security
from dependencies import db, create_notification, CONTRACTS_DIR
from pre_transfer_review_generator import generate_pre_transfer_review_pdf

router = APIRouter(prefix="/pre-transfer-reviews", tags=["Pre-Transfer Reviews"])

# ================= MODELS =================

class PreTransferChecklist(BaseModel):
    suspension_status: Optional[bool] = None
    threat_of_suspension: Optional[bool] = None
    minor_nc_outstanding: Optional[bool] = None
    major_nc_outstanding: Optional[bool] = None
    legal_representation: Optional[bool] = None
    complaints_handled: Optional[bool] = None
    within_bac_scope: Optional[bool] = None
    previous_reports_available: Optional[bool] = None

class PreTransferReviewCreate(BaseModel):
    client_name: str
    client_name_ar: str = ""
    client_address: str = ""
    client_phone: str = ""
    enquiry_reference: str = ""
    transfer_reason: str = ""
    existing_cb: str = ""
    certificate_number: str = ""
    validity: str = ""
    scope: str = ""
    sites: str = ""
    eac_code: str = ""
    standards: List[str] = []

class PreTransferReviewUpdate(BaseModel):
    client_name: Optional[str] = None
    client_name_ar: Optional[str] = None
    client_address: Optional[str] = None
    client_phone: Optional[str] = None
    enquiry_reference: Optional[str] = None
    transfer_reason: Optional[str] = None
    existing_cb: Optional[str] = None
    certificate_number: Optional[str] = None
    validity: Optional[str] = None
    scope: Optional[str] = None
    sites: Optional[str] = None
    eac_code: Optional[str] = None
    standards: Optional[List[str]] = None
    checklist: Optional[dict] = None
    certification_cycle_stage: Optional[str] = None
    has_previous_audit_report: Optional[bool] = None
    has_previous_certificates: Optional[bool] = None
    transfer_decision: Optional[str] = None
    decision_reason: Optional[str] = None
    reviewed_by: Optional[str] = None
    review_date: Optional[str] = None
    approved_by: Optional[str] = None
    approval_date: Optional[str] = None

class PreTransferReview(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str = ""
    client_name_ar: str = ""
    client_address: str = ""
    client_phone: str = ""
    enquiry_reference: str = ""
    transfer_reason: str = ""
    existing_cb: str = ""
    certificate_number: str = ""
    validity: str = ""
    scope: str = ""
    sites: str = ""
    eac_code: str = ""
    standards: List[str] = []
    checklist: dict = {}
    certification_cycle_stage: str = ""
    has_previous_audit_report: bool = False
    has_previous_certificates: bool = False
    attachments: List[str] = []
    transfer_decision: str = "pending"
    decision_reason: str = ""
    reviewed_by: str = ""
    review_date: str = ""
    approved_by: str = ""
    approval_date: str = ""
    status: str = "draft"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

DEFAULT_PRETRANSFER_CHECKLIST = {
    "suspension_status": None,
    "threat_of_suspension": None,
    "minor_nc_outstanding": None,
    "major_nc_outstanding": None,
    "legal_representation": None,
    "complaints_handled": None,
    "within_bac_scope": None,
    "previous_reports_available": None
}

# ================= ENDPOINTS =================

@router.get("")
async def get_pre_transfer_reviews(
    status: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all pre-transfer reviews"""
    await get_current_user(credentials)
    
    query = {}
    if status and status != 'all':
        query['status'] = status
    
    reviews = await db.pre_transfer_reviews.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return reviews

@router.post("")
async def create_pre_transfer_review(
    data: PreTransferReviewCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new pre-transfer review"""
    await get_current_user(credentials)
    
    review = PreTransferReview(
        client_name=data.client_name,
        client_name_ar=data.client_name_ar,
        client_address=data.client_address,
        client_phone=data.client_phone,
        enquiry_reference=data.enquiry_reference,
        transfer_reason=data.transfer_reason,
        existing_cb=data.existing_cb,
        certificate_number=data.certificate_number,
        validity=data.validity,
        scope=data.scope,
        sites=data.sites,
        eac_code=data.eac_code,
        standards=data.standards,
        checklist=DEFAULT_PRETRANSFER_CHECKLIST.copy(),
        status="draft"
    )
    
    review_doc = review.model_dump()
    review_doc['created_at'] = review_doc['created_at'].isoformat()
    
    await db.pre_transfer_reviews.insert_one(review_doc)
    
    await create_notification(
        notification_type="pre_transfer_created",
        title="Pre-Transfer Review Created",
        title_ar="تم إنشاء مراجعة ما قبل النقل",
        message=f"Pre-transfer review created for {review.client_name}",
        message_ar=f"تم إنشاء مراجعة ما قبل النقل لـ {review.client_name}",
        related_id=review.id,
        related_type="pre_transfer_review"
    )
    
    return {"message": "Pre-transfer review created", "id": review.id}

@router.get("/{review_id}")
async def get_pre_transfer_review(
    review_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get a specific pre-transfer review"""
    await get_current_user(credentials)
    
    review = await db.pre_transfer_reviews.find_one({"id": review_id}, {"_id": 0})
    if not review:
        raise HTTPException(status_code=404, detail="Pre-transfer review not found")
    
    return review

@router.put("/{review_id}")
async def update_pre_transfer_review(
    review_id: str,
    data: PreTransferReviewUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update a pre-transfer review"""
    await get_current_user(credentials)
    
    existing = await db.pre_transfer_reviews.find_one({"id": review_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Pre-transfer review not found")
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.pre_transfer_reviews.update_one({"id": review_id}, {"$set": update_data})
    
    return {"message": "Pre-transfer review updated"}

@router.delete("/{review_id}")
async def delete_pre_transfer_review(
    review_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete a pre-transfer review"""
    await get_current_user(credentials)
    
    existing = await db.pre_transfer_reviews.find_one({"id": review_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Pre-transfer review not found")
    
    await db.pre_transfer_reviews.delete_one({"id": review_id})
    return {"message": "Pre-transfer review deleted"}

@router.post("/{review_id}/make-decision")
async def make_transfer_decision(
    review_id: str,
    data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Make transfer decision"""
    await get_current_user(credentials)
    
    existing = await db.pre_transfer_reviews.find_one({"id": review_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Pre-transfer review not found")
    
    decision = data.get('transfer_decision', '')
    if decision not in ['approved', 'rejected', 'pending']:
        raise HTTPException(status_code=400, detail="Invalid transfer decision")
    
    update_data = {
        "transfer_decision": decision,
        "decision_reason": data.get('decision_reason', ''),
        "reviewed_by": data.get('reviewed_by', ''),
        "review_date": data.get('review_date', datetime.now().strftime("%Y-%m-%d")),
        "approved_by": data.get('approved_by', ''),
        "approval_date": data.get('approval_date', datetime.now().strftime("%Y-%m-%d")),
        "status": "decision_made",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.pre_transfer_reviews.update_one({"id": review_id}, {"$set": update_data})
    
    decision_ar = {'approved': 'تمت الموافقة', 'rejected': 'مرفوض', 'pending': 'قيد الانتظار'}.get(decision, decision)
    
    await create_notification(
        notification_type="transfer_decision",
        title="Transfer Decision Made",
        title_ar="تم اتخاذ قرار النقل",
        message=f"Transfer decision for {existing.get('client_name', '')}: {decision.title()}",
        message_ar=f"قرار النقل لـ {existing.get('client_name', '')}: {decision_ar}",
        related_id=review_id,
        related_type="pre_transfer_review"
    )
    
    return {"message": f"Transfer decision recorded: {decision}"}

@router.get("/{review_id}/pdf")
async def get_pre_transfer_review_pdf(
    review_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Generate PDF for Pre-Transfer Review"""
    await get_current_user(credentials)
    
    review = await db.pre_transfer_reviews.find_one({"id": review_id}, {"_id": 0})
    if not review:
        raise HTTPException(status_code=404, detail="Pre-transfer review not found")
    
    try:
        pdf_path = str(CONTRACTS_DIR / f"pre_transfer_review_{review_id[:8]}.pdf")
        generate_pre_transfer_review_pdf(review, pdf_path)
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"pre_transfer_review_{review_id[:8]}.pdf"
        )
    except Exception as e:
        logging.error(f"Error generating Pre-Transfer Review PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
