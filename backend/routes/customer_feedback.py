"""
Customer Feedback Routes (BAC-F6-16)
Customer Feedback Survey endpoints
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
from customer_feedback_generator import generate_customer_feedback_pdf

router = APIRouter(prefix="/customer-feedback", tags=["Customer Feedback"])

# ================= MODELS =================

class FeedbackQuestion(BaseModel):
    category: str = ""
    category_ar: str = ""
    question: str = ""
    question_ar: str = ""
    rating: Optional[int] = None

class CustomerFeedbackCreate(BaseModel):
    certificate_id: str = ""
    audit_id: str = ""
    organization_name: str
    organization_name_ar: str = ""
    audit_type: str = ""
    standards: List[str] = []
    audit_date: str = ""
    lead_auditor: str = ""
    auditor: str = ""

class CustomerFeedbackSubmit(BaseModel):
    questions: List[dict] = []
    want_same_team: Optional[bool] = None
    suggestions: str = ""
    respondent_name: str = ""
    respondent_designation: str = ""

class CustomerFeedback(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    access_token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    certificate_id: str = ""
    audit_id: str = ""
    organization_name: str = ""
    organization_name_ar: str = ""
    audit_type: str = ""
    standards: List[str] = []
    audit_date: str = ""
    lead_auditor: str = ""
    auditor: str = ""
    questions: List[dict] = []
    want_same_team: Optional[bool] = None
    suggestions: str = ""
    respondent_name: str = ""
    respondent_designation: str = ""
    submission_date: str = ""
    overall_score: float = 0.0
    evaluation_result: str = ""
    reviewed_by: str = ""
    review_date: str = ""
    review_comments: str = ""
    status: str = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    submitted_at: Optional[datetime] = None

# Default feedback questions
DEFAULT_FEEDBACK_QUESTIONS = [
    {"category": "BAC Office", "category_ar": "مكتب بيان", "question": "Responsiveness to your enquiries - Promptness", "question_ar": "الاستجابة لاستفساراتكم - السرعة", "rating": None},
    {"category": "BAC Office", "category_ar": "مكتب بيان", "question": "Accuracy of the quotes communicated to you", "question_ar": "دقة عروض الأسعار المقدمة لكم", "rating": None},
    {"category": "BAC Office", "category_ar": "مكتب بيان", "question": "Handling of your Complaint(s)", "question_ar": "التعامل مع شكواكم", "rating": None},
    {"category": "Audit Preparation", "category_ar": "التحضير للتدقيق", "question": "The audit Plan was sent sufficiently in advance", "question_ar": "تم إرسال خطة التدقيق مسبقاً بوقت كافٍ", "rating": None},
    {"category": "Audit Preparation", "category_ar": "التحضير للتدقيق", "question": "The audit team was well prepared for audit", "question_ar": "كان فريق التدقيق مستعداً جيداً للتدقيق", "rating": None},
    {"category": "Punctuality", "category_ar": "الالتزام بالمواعيد", "question": "The audit carried out as per the programme", "question_ar": "تم التدقيق وفقاً للبرنامج", "rating": None},
    {"category": "Audit", "category_ar": "التدقيق", "question": "Opening and closing meetings were professional", "question_ar": "كانت الاجتماعات الافتتاحية والختامية احترافية", "rating": None},
    {"category": "Audit", "category_ar": "التدقيق", "question": "Questions asked were relevant and easy to understand", "question_ar": "كانت الأسئلة ذات صلة وسهلة الفهم", "rating": None},
    {"category": "Audit", "category_ar": "التدقيق", "question": "The audit team gave enough explanation for your questions", "question_ar": "قدم فريق التدقيق شرحاً كافياً لأسئلتكم", "rating": None},
    {"category": "Audit", "category_ar": "التدقيق", "question": "The audit team was fair and impartial", "question_ar": "كان فريق التدقيق عادلاً ومحايداً", "rating": None},
    {"category": "Ethics", "category_ar": "الأخلاقيات", "question": "The audit team concentrated on the audit", "question_ar": "ركز فريق التدقيق على التدقيق", "rating": None},
    {"category": "Ethics", "category_ar": "الأخلاقيات", "question": "The audit team didn't make unreasonable demands", "question_ar": "لم يقدم فريق التدقيق طلبات غير معقولة", "rating": None},
    {"category": "Effectiveness", "category_ar": "الفعالية", "question": "Issues found were helpful for improving your system", "question_ar": "كانت النتائج مفيدة لتحسين نظامكم", "rating": None},
]

def calculate_feedback_score(questions: List[dict]) -> tuple:
    """Calculate overall score and evaluation result from ratings"""
    total_score = 0
    rated_count = 0
    
    for q in questions:
        rating = q.get('rating')
        if rating is not None and rating != 'na':
            try:
                rating_int = int(rating)
                if 1 <= rating_int <= 5:
                    total_score += rating_int
                    rated_count += 1
            except:
                pass
    
    if rated_count == 0:
        return 0.0, "unsatisfactory"
    
    percentage = (total_score / (rated_count * 5)) * 100
    
    if percentage >= 90:
        evaluation = "excellent"
    elif percentage >= 75:
        evaluation = "good"
    elif percentage >= 60:
        evaluation = "average"
    else:
        evaluation = "unsatisfactory"
    
    return round(percentage, 1), evaluation

# ================= ENDPOINTS =================

@router.get("")
async def get_customer_feedback_list(
    status: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all customer feedback forms"""
    await get_current_user(credentials)
    
    query = {}
    if status and status != 'all':
        query['status'] = status
    
    feedbacks = await db.customer_feedback.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return feedbacks

@router.post("")
async def create_customer_feedback(
    data: CustomerFeedbackCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new customer feedback form"""
    await get_current_user(credentials)
    
    questions = [q.copy() for q in DEFAULT_FEEDBACK_QUESTIONS]
    
    feedback = CustomerFeedback(
        certificate_id=data.certificate_id,
        audit_id=data.audit_id,
        organization_name=data.organization_name,
        organization_name_ar=data.organization_name_ar,
        audit_type=data.audit_type,
        standards=data.standards,
        audit_date=data.audit_date,
        lead_auditor=data.lead_auditor,
        auditor=data.auditor,
        questions=questions,
        status="pending"
    )
    
    feedback_doc = feedback.model_dump()
    feedback_doc['created_at'] = feedback_doc['created_at'].isoformat()
    
    await db.customer_feedback.insert_one(feedback_doc)
    
    await create_notification(
        notification_type="feedback_created",
        title="Customer Feedback Created",
        title_ar="تم إنشاء نموذج الملاحظات",
        message=f"Feedback form created for {feedback.organization_name}",
        message_ar=f"تم إنشاء نموذج ملاحظات لـ {feedback.organization_name}",
        related_id=feedback.id,
        related_type="customer_feedback"
    )
    
    return {
        "message": "Customer feedback form created",
        "id": feedback.id,
        "access_token": feedback.access_token,
        "public_url": f"/feedback/{feedback.access_token}"
    }

@router.get("/{feedback_id}")
async def get_customer_feedback(
    feedback_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get a specific customer feedback"""
    await get_current_user(credentials)
    
    feedback = await db.customer_feedback.find_one({"id": feedback_id}, {"_id": 0})
    if not feedback:
        raise HTTPException(status_code=404, detail="Customer feedback not found")
    
    return feedback

@router.put("/{feedback_id}")
async def update_customer_feedback(
    feedback_id: str,
    data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update a customer feedback (admin only)"""
    await get_current_user(credentials)
    
    existing = await db.customer_feedback.find_one({"id": feedback_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Customer feedback not found")
    
    if 'questions' in data:
        score, evaluation = calculate_feedback_score(data['questions'])
        data['overall_score'] = score
        data['evaluation_result'] = evaluation
    
    await db.customer_feedback.update_one({"id": feedback_id}, {"$set": data})
    
    return {"message": "Customer feedback updated"}

@router.delete("/{feedback_id}")
async def delete_customer_feedback(
    feedback_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete a customer feedback"""
    await get_current_user(credentials)
    
    existing = await db.customer_feedback.find_one({"id": feedback_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Customer feedback not found")
    
    await db.customer_feedback.delete_one({"id": feedback_id})
    return {"message": "Customer feedback deleted"}

@router.post("/{feedback_id}/review")
async def review_customer_feedback(
    feedback_id: str,
    data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Mark feedback as reviewed by admin"""
    await get_current_user(credentials)
    
    existing = await db.customer_feedback.find_one({"id": feedback_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Customer feedback not found")
    
    await db.customer_feedback.update_one(
        {"id": feedback_id},
        {"$set": {
            "reviewed_by": data.get('reviewed_by', ''),
            "review_date": data.get('review_date', datetime.now().strftime("%Y-%m-%d")),
            "review_comments": data.get('review_comments', ''),
            "status": "reviewed"
        }}
    )
    
    return {"message": "Feedback marked as reviewed"}

@router.get("/{feedback_id}/pdf")
async def get_customer_feedback_pdf(
    feedback_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Generate PDF for Customer Feedback"""
    await get_current_user(credentials)
    
    feedback = await db.customer_feedback.find_one({"id": feedback_id}, {"_id": 0})
    if not feedback:
        raise HTTPException(status_code=404, detail="Customer feedback not found")
    
    try:
        pdf_path = str(CONTRACTS_DIR / f"customer_feedback_{feedback_id[:8]}.pdf")
        generate_customer_feedback_pdf(feedback, pdf_path)
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"customer_feedback_{feedback_id[:8]}.pdf"
        )
    except Exception as e:
        logging.error(f"Error generating Customer Feedback PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
