"""
Technical Reviews Routes (BAC-F6-15)
Technical Review and Certification Decision endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from pathlib import Path
import uuid
import os
import logging

# Import shared dependencies (avoiding circular imports)
from dependencies import (
    db, get_current_user, create_notification, 
    generate_certificate_number, get_qr_code_base64, Certificate,
    security, CONTRACTS_DIR
)
from technical_review_generator import generate_technical_review_pdf

router = APIRouter(prefix="/technical-reviews", tags=["Technical Reviews"])
security = HTTPBearer()

# ================= MODELS =================

class TechnicalReviewChecklistItem(BaseModel):
    """Individual checklist item for technical review"""
    category: str = ""
    item: str = ""
    item_ar: str = ""
    checked: Optional[bool] = None
    remarks: str = ""

class TechnicalReviewCreate(BaseModel):
    """Create Technical Review request"""
    stage2_report_id: str = ""
    client_name: str
    client_name_ar: str = ""
    location: str = ""
    scope: str = ""
    ea_code: str = ""
    standards: List[str] = []
    audit_type: str = ""
    audit_dates: str = ""
    audit_team_members: List[str] = []
    technical_expert: str = ""

class TechnicalReviewUpdate(BaseModel):
    """Update Technical Review"""
    client_name: Optional[str] = None
    client_name_ar: Optional[str] = None
    location: Optional[str] = None
    scope: Optional[str] = None
    ea_code: Optional[str] = None
    standards: Optional[List[str]] = None
    audit_type: Optional[str] = None
    audit_dates: Optional[str] = None
    audit_team_members: Optional[List[str]] = None
    technical_expert: Optional[str] = None
    checklist_items: Optional[List[dict]] = None
    technical_reviewer: Optional[str] = None
    review_date: Optional[str] = None
    review_comments: Optional[str] = None
    certification_decision: Optional[str] = None
    decision_comments: Optional[str] = None
    approved_by: Optional[str] = None
    approval_date: Optional[str] = None

class TechnicalReview(BaseModel):
    """Technical Review and Certification Decision (BACF6-15)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    stage2_report_id: str = ""
    job_order_id: str = ""
    audit_program_id: str = ""
    contract_review_id: str = ""
    agreement_id: str = ""
    client_name: str = ""
    client_name_ar: str = ""
    location: str = ""
    scope: str = ""
    ea_code: str = ""
    standards: List[str] = []
    audit_type: str = ""
    audit_dates: str = ""
    audit_team_members: List[str] = []
    technical_expert: str = ""
    checklist_items: List[dict] = []
    technical_reviewer: str = ""
    review_date: str = ""
    review_comments: str = ""
    certification_decision: str = ""
    decision_comments: str = ""
    approved_by: str = ""
    approval_date: str = ""
    certificate_id: str = ""
    certificate_number: str = ""
    status: str = "draft"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

# Default checklist items
DEFAULT_TECHNICAL_REVIEW_CHECKLIST = [
    {"category": "General", "item": "Correctness of Name, address, scope, Ref no.", "item_ar": "صحة الاسم والعنوان والنطاق ورقم المرجع", "checked": None, "remarks": ""},
    {"category": "General", "item": "Scope Terminology", "item_ar": "مصطلحات النطاق", "checked": None, "remarks": ""},
    {"category": "General", "item": "EA Code verification", "item_ar": "التحقق من رمز EA", "checked": None, "remarks": ""},
    {"category": "General", "item": "Conformance to audited processes", "item_ar": "المطابقة للعمليات المدققة", "checked": None, "remarks": ""},
    {"category": "Application", "item": "Application form complete and signed by both parties", "item_ar": "نموذج الطلب مكتمل وموقع من الطرفين", "checked": None, "remarks": ""},
    {"category": "Quotation", "item": "Quotation signed by both BAC & client representative", "item_ar": "عرض السعر موقع من بيان والعميل", "checked": None, "remarks": ""},
    {"category": "Man Days", "item": "Adequacy per IAF guidelines", "item_ar": "الكفاية وفقًا لإرشادات IAF", "checked": None, "remarks": ""},
    {"category": "Man Days", "item": "Adequacy on complexity", "item_ar": "الكفاية من حيث التعقيد", "checked": None, "remarks": ""},
    {"category": "Man Days", "item": "Reduction/change in man days justified", "item_ar": "تبرير التخفيض/التغيير في أيام العمل", "checked": None, "remarks": ""},
    {"category": "Audit Team", "item": "Team competent for scope", "item_ar": "الفريق مؤهل للنطاق", "checked": None, "remarks": ""},
    {"category": "Stage 1", "item": "Audit plan available and contains all requirements", "item_ar": "خطة التدقيق متوفرة وتحتوي على جميع المتطلبات", "checked": None, "remarks": ""},
    {"category": "Stage 1", "item": "Opening & Closing Meeting attendance available", "item_ar": "سجل حضور الاجتماع الافتتاحي والختامي متوفر", "checked": None, "remarks": ""},
    {"category": "Stage 1", "item": "Duration corresponds to contract review", "item_ar": "المدة تتوافق مع مراجعة العقد", "checked": None, "remarks": ""},
    {"category": "Stage 1", "item": "Audit report covers all areas including scope validation", "item_ar": "تقرير التدقيق يغطي جميع المجالات بما في ذلك التحقق من النطاق", "checked": None, "remarks": ""},
    {"category": "Stage 1", "item": "Findings clearly highlighted as concerns", "item_ar": "النتائج موضحة بوضوح كمخاوف", "checked": None, "remarks": ""},
    {"category": "Stage 2", "item": "Stage 2 audit plan available and complete", "item_ar": "خطة تدقيق المرحلة 2 متوفرة ومكتملة", "checked": None, "remarks": ""},
    {"category": "Stage 2", "item": "Opening & Closing Meeting attendance available", "item_ar": "سجل حضور الاجتماع الافتتاحي والختامي متوفر", "checked": None, "remarks": ""},
    {"category": "Stage 2", "item": "Stage 2 Audit Report correct and complete", "item_ar": "تقرير تدقيق المرحلة 2 صحيح ومكتمل", "checked": None, "remarks": ""},
    {"category": "Stage 2", "item": "Evidence for NC Closure recorded", "item_ar": "دليل إغلاق عدم المطابقة مسجل", "checked": None, "remarks": ""},
    {"category": "Other", "item": "Conflict of Interest and Confidentiality Undertaking", "item_ar": "إقرار تضارب المصالح والسرية", "checked": None, "remarks": ""},
    {"category": "Other", "item": "Customer Feedback Form reviewed", "item_ar": "مراجعة نموذج ملاحظات العميل", "checked": None, "remarks": ""},
    {"category": "Other", "item": "Certificate data request reviewed", "item_ar": "مراجعة طلب بيانات الشهادة", "checked": None, "remarks": ""},
]

# ================= ENDPOINTS =================

@router.get("")
async def get_technical_reviews(
    status: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all technical reviews"""
    await get_current_user(credentials)
    
    query = {}
    if status and status != 'all':
        query['status'] = status
    
    reviews = await db.technical_reviews.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return reviews

@router.post("")
async def create_technical_review(
    data: TechnicalReviewCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new technical review"""
    await get_current_user(credentials)
    
    checklist_items = [item.copy() for item in DEFAULT_TECHNICAL_REVIEW_CHECKLIST]
    
    review = TechnicalReview(
        stage2_report_id=data.stage2_report_id,
        client_name=data.client_name,
        client_name_ar=data.client_name_ar,
        location=data.location,
        scope=data.scope,
        ea_code=data.ea_code,
        standards=data.standards,
        audit_type=data.audit_type,
        audit_dates=data.audit_dates,
        audit_team_members=data.audit_team_members,
        technical_expert=data.technical_expert,
        checklist_items=checklist_items,
        status="draft"
    )
    
    if data.stage2_report_id:
        stage2_report = await db.stage2_audit_reports.find_one({"id": data.stage2_report_id}, {"_id": 0})
        if stage2_report:
            review.job_order_id = stage2_report.get('job_order_id', '')
            review.audit_program_id = stage2_report.get('audit_program_id', '')
            review.contract_review_id = stage2_report.get('contract_review_id', '')
            review.agreement_id = stage2_report.get('agreement_id', '')
            
            if not review.client_name:
                review.client_name = stage2_report.get('client_name', '')
            if not review.client_name_ar:
                review.client_name_ar = stage2_report.get('client_name_ar', '')
            if not review.scope:
                review.scope = stage2_report.get('scope', '')
            if not review.standards:
                review.standards = stage2_report.get('standards', [])
            if not review.audit_team_members:
                team = []
                if stage2_report.get('team_leader'):
                    team.append(stage2_report.get('team_leader'))
                team.extend(stage2_report.get('team_members', []))
                review.audit_team_members = team
    
    review_doc = review.model_dump()
    review_doc['created_at'] = review_doc['created_at'].isoformat()
    
    await db.technical_reviews.insert_one(review_doc)
    
    await create_notification(
        notification_type="technical_review_created",
        title="Technical Review Created",
        title_ar="تم إنشاء مراجعة فنية",
        message=f"Technical review created for {review.client_name}",
        message_ar=f"تم إنشاء مراجعة فنية لـ {review.client_name}",
        related_id=review.id,
        related_type="technical_review"
    )
    
    return {"message": "Technical review created", "id": review.id}

@router.get("/{review_id}")
async def get_technical_review(
    review_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get a specific technical review"""
    await get_current_user(credentials)
    
    review = await db.technical_reviews.find_one({"id": review_id}, {"_id": 0})
    if not review:
        raise HTTPException(status_code=404, detail="Technical review not found")
    
    return review

@router.put("/{review_id}")
async def update_technical_review(
    review_id: str,
    data: TechnicalReviewUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update a technical review"""
    await get_current_user(credentials)
    
    existing = await db.technical_reviews.find_one({"id": review_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Technical review not found")
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.technical_reviews.update_one(
        {"id": review_id},
        {"$set": update_data}
    )
    
    return {"message": "Technical review updated"}

@router.delete("/{review_id}")
async def delete_technical_review(
    review_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete a technical review"""
    await get_current_user(credentials)
    
    existing = await db.technical_reviews.find_one({"id": review_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Technical review not found")
    
    await db.technical_reviews.delete_one({"id": review_id})
    return {"message": "Technical review deleted"}

@router.post("/{review_id}/submit-review")
async def submit_technical_review(
    review_id: str,
    data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Submit technical review"""
    await get_current_user(credentials)
    
    existing = await db.technical_reviews.find_one({"id": review_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Technical review not found")
    
    await db.technical_reviews.update_one(
        {"id": review_id},
        {"$set": {
            "technical_reviewer": data.get('technical_reviewer', ''),
            "review_date": data.get('review_date', datetime.now().strftime("%Y-%m-%d")),
            "review_comments": data.get('review_comments', ''),
            "status": "under_review",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": "Technical review submitted"}

@router.post("/{review_id}/make-decision")
async def make_certification_decision(
    review_id: str,
    data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Make certification decision"""
    await get_current_user(credentials)
    
    existing = await db.technical_reviews.find_one({"id": review_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Technical review not found")
    
    decision = data.get('certification_decision', '')
    if decision not in ['issue_certificate', 'reject_certificate', 'needs_review']:
        raise HTTPException(status_code=400, detail="Invalid certification decision")
    
    update_data = {
        "certification_decision": decision,
        "decision_comments": data.get('decision_comments', ''),
        "status": "decision_made",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.technical_reviews.update_one({"id": review_id}, {"$set": update_data})
    
    decision_ar = {
        'issue_certificate': 'إصدار الشهادة',
        'reject_certificate': 'رفض الشهادة',
        'needs_review': 'يحتاج مراجعة'
    }.get(decision, decision)
    
    await create_notification(
        notification_type="certification_decision",
        title="Certification Decision Made",
        title_ar="تم اتخاذ قرار الشهادة",
        message=f"Decision for {existing.get('client_name', '')}: {decision.replace('_', ' ').title()}",
        message_ar=f"قرار لـ {existing.get('client_name', '')}: {decision_ar}",
        related_id=review_id,
        related_type="technical_review"
    )
    
    return {"message": f"Certification decision recorded: {decision}"}

@router.post("/{review_id}/approve")
async def approve_technical_review(
    review_id: str,
    data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Approve technical review and optionally issue certificate"""
    await get_current_user(credentials)
    
    existing = await db.technical_reviews.find_one({"id": review_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Technical review not found")
    
    update_data = {
        "approved_by": data.get('approved_by', ''),
        "approval_date": data.get('approval_date', datetime.now().strftime("%Y-%m-%d")),
        "status": "approved",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    certificate_result = None
    
    if existing.get('certification_decision') == 'issue_certificate':
        cert_number = await generate_certificate_number()
        
        issue_date = datetime.now().strftime("%Y-%m-%d")
        expiry_date = (datetime.now() + timedelta(days=365*3)).strftime("%Y-%m-%d")
        
        base_url = os.environ.get('FRONTEND_URL', 'https://service-audit-portal.preview.emergentagent.com')
        verification_url = f"{base_url}/verify/{cert_number}"
        qr_base64 = get_qr_code_base64(verification_url)
        
        certificate = Certificate(
            certificate_number=cert_number,
            contract_id=existing.get('agreement_id', ''),
            audit_id=existing.get('stage2_report_id', ''),
            organization_name=existing.get('client_name', ''),
            organization_name_ar=existing.get('client_name_ar', ''),
            standards=existing.get('standards', []),
            scope=existing.get('scope', ''),
            issue_date=issue_date,
            expiry_date=expiry_date,
            status="active",
            verification_url=verification_url,
            qr_code_data=qr_base64,
            lead_auditor=existing.get('audit_team_members', [''])[0] if existing.get('audit_team_members') else '',
            audit_team=existing.get('audit_team_members', [])
        )
        
        cert_doc = certificate.model_dump()
        cert_doc['created_at'] = cert_doc['created_at'].isoformat()
        
        await db.certificates.insert_one(cert_doc)
        
        update_data['certificate_id'] = certificate.id
        update_data['certificate_number'] = cert_number
        update_data['status'] = 'certificate_issued'
        
        await create_notification(
            notification_type="certificate_issued",
            title="Certificate Issued",
            title_ar="تم إصدار الشهادة",
            message=f"Certificate {cert_number} issued for {existing.get('client_name', '')}",
            message_ar=f"تم إصدار الشهادة {cert_number} لـ {existing.get('client_name', '')}",
            related_id=certificate.id,
            related_type="certificate"
        )
        
        certificate_result = {
            "certificate_id": certificate.id,
            "certificate_number": cert_number
        }
    
    await db.technical_reviews.update_one({"id": review_id}, {"$set": update_data})
    
    response = {"message": "Technical review approved", "status": update_data['status']}
    if certificate_result:
        response["certificate"] = certificate_result
    
    return response

@router.get("/{review_id}/pdf")
async def get_technical_review_pdf(
    review_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Generate PDF for Technical Review"""
    await get_current_user(credentials)
    
    review = await db.technical_reviews.find_one({"id": review_id}, {"_id": 0})
    if not review:
        raise HTTPException(status_code=404, detail="Technical review not found")
    
    try:
        pdf_path = str(CONTRACTS_DIR / f"technical_review_{review_id[:8]}.pdf")
        
        generate_technical_review_pdf(review, pdf_path)
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"technical_review_{review_id[:8]}.pdf"
        )
    except Exception as e:
        logging.error(f"Error generating Technical Review PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
