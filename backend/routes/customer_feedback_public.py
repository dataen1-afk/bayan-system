"""
Customer Feedback Public Routes (BAC-F6-16)
Public endpoints for client feedback submission (no authentication required)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone

from dependencies import db, create_notification

router = APIRouter(prefix="/public/feedback", tags=["Public Feedback"])

# ================= MODELS =================

class CustomerFeedbackSubmit(BaseModel):
    questions: List[dict] = []
    want_same_team: Optional[bool] = None
    suggestions: str = ""
    respondent_name: str = ""
    respondent_designation: str = ""

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

@router.get("/{access_token}")
async def get_public_feedback_form(access_token: str):
    """Get feedback form for client to fill (public, no auth required)"""
    feedback = await db.customer_feedback.find_one(
        {"access_token": access_token},
        {"_id": 0}
    )
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback form not found")
    
    if feedback.get('status') == 'submitted':
        raise HTTPException(status_code=400, detail="This feedback has already been submitted")
    
    return {
        "id": feedback['id'],
        "organization_name": feedback.get('organization_name', ''),
        "organization_name_ar": feedback.get('organization_name_ar', ''),
        "audit_type": feedback.get('audit_type', ''),
        "standards": feedback.get('standards', []),
        "audit_date": feedback.get('audit_date', ''),
        "lead_auditor": feedback.get('lead_auditor', ''),
        "auditor": feedback.get('auditor', ''),
        "questions": feedback.get('questions', []),
        "status": feedback.get('status', 'pending')
    }

@router.post("/{access_token}/submit")
async def submit_public_feedback(access_token: str, data: CustomerFeedbackSubmit):
    """Submit feedback from client (public, no auth required)"""
    feedback = await db.customer_feedback.find_one({"access_token": access_token})
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback form not found")
    
    if feedback.get('status') == 'submitted':
        raise HTTPException(status_code=400, detail="This feedback has already been submitted")
    
    questions = feedback.get('questions', [])
    for submitted_q in data.questions:
        q_idx = submitted_q.get('index', -1)
        if 0 <= q_idx < len(questions):
            questions[q_idx]['rating'] = submitted_q.get('rating')
    
    score, evaluation = calculate_feedback_score(questions)
    
    await db.customer_feedback.update_one(
        {"access_token": access_token},
        {"$set": {
            "questions": questions,
            "want_same_team": data.want_same_team,
            "suggestions": data.suggestions,
            "respondent_name": data.respondent_name,
            "respondent_designation": data.respondent_designation,
            "submission_date": datetime.now().strftime("%Y-%m-%d"),
            "overall_score": score,
            "evaluation_result": evaluation,
            "status": "submitted",
            "submitted_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    await create_notification(
        notification_type="feedback_submitted",
        title="Customer Feedback Submitted",
        title_ar="تم تقديم ملاحظات العميل",
        message=f"Feedback received from {feedback.get('organization_name', '')} - Score: {score}%",
        message_ar=f"تم استلام ملاحظات من {feedback.get('organization_name', '')} - النتيجة: {score}%",
        related_id=feedback['id'],
        related_type="customer_feedback"
    )
    
    return {
        "message": "Feedback submitted successfully",
        "overall_score": score,
        "evaluation_result": evaluation
    }
