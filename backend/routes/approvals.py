"""
Multi-Level Approval Workflow Routes
Handles approval workflows for various document types
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
import uuid

from auth import get_current_user, security
from dependencies import db, create_notification

router = APIRouter(prefix="/approvals", tags=["Approvals"])

# ================= MODELS =================

class ApprovalLevel(BaseModel):
    """Defines an approval level in the workflow"""
    level: int  # 1, 2, 3, etc.
    role: str  # technical_reviewer, manager, director
    role_ar: str = ""
    approver_id: str = ""
    approver_name: str = ""
    status: str = "pending"  # pending, approved, rejected, skipped
    decision_date: str = ""
    comments: str = ""
    comments_ar: str = ""

class ApprovalWorkflowCreate(BaseModel):
    """Create a new approval workflow"""
    document_type: str  # contract_review, job_order, audit_plan, technical_review, certificate
    document_id: str
    document_name: str
    document_name_ar: str = ""
    requested_by: str
    requested_by_name: str = ""
    levels: List[dict] = []  # List of approval levels

class ApprovalDecision(BaseModel):
    """Submit an approval decision"""
    status: str  # approved, rejected
    comments: str = ""
    comments_ar: str = ""

class ApprovalWorkflow(BaseModel):
    """Complete approval workflow"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_type: str
    document_id: str
    document_name: str
    document_name_ar: str = ""
    requested_by: str
    requested_by_name: str = ""
    current_level: int = 1
    total_levels: int = 0
    levels: List[dict] = []
    status: str = "in_progress"  # in_progress, approved, rejected, cancelled
    final_decision: str = ""
    final_decision_date: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

# Default approval configurations for different document types
DEFAULT_APPROVAL_CONFIGS = {
    "contract_review": {
        "name": "Contract Review",
        "name_ar": "مراجعة العقد",
        "levels": [
            {"level": 1, "role": "technical_reviewer", "role_ar": "المراجع الفني"},
            {"level": 2, "role": "manager", "role_ar": "المدير"},
        ]
    },
    "job_order": {
        "name": "Job Order",
        "name_ar": "أمر العمل",
        "levels": [
            {"level": 1, "role": "manager", "role_ar": "المدير"},
        ]
    },
    "audit_plan": {
        "name": "Audit Plan",
        "name_ar": "خطة التدقيق",
        "levels": [
            {"level": 1, "role": "technical_reviewer", "role_ar": "المراجع الفني"},
            {"level": 2, "role": "manager", "role_ar": "المدير"},
        ]
    },
    "technical_review": {
        "name": "Technical Review",
        "name_ar": "المراجعة الفنية",
        "levels": [
            {"level": 1, "role": "technical_reviewer", "role_ar": "المراجع الفني"},
            {"level": 2, "role": "certification_manager", "role_ar": "مدير الشهادات"},
            {"level": 3, "role": "director", "role_ar": "المدير العام"},
        ]
    },
    "certificate": {
        "name": "Certificate Issuance",
        "name_ar": "إصدار الشهادة",
        "levels": [
            {"level": 1, "role": "certification_manager", "role_ar": "مدير الشهادات"},
            {"level": 2, "role": "director", "role_ar": "المدير العام"},
        ]
    },
    "pre_transfer": {
        "name": "Pre-Transfer Review",
        "name_ar": "مراجعة ما قبل النقل",
        "levels": [
            {"level": 1, "role": "technical_reviewer", "role_ar": "المراجع الفني"},
            {"level": 2, "role": "manager", "role_ar": "المدير"},
        ]
    }
}

# ================= HELPER FUNCTIONS =================

async def get_pending_approvals_for_user(user_id: str, role: str) -> List[dict]:
    """Get all pending approvals for a user based on their role"""
    query = {
        "status": "in_progress",
        "levels": {
            "$elemMatch": {
                "status": "pending",
                "role": role
            }
        }
    }
    
    # Find workflows where current level matches user's role
    workflows = await db.approval_workflows.find(query, {"_id": 0}).to_list(100)
    
    pending = []
    for wf in workflows:
        current_level = wf.get('current_level', 1)
        for level in wf.get('levels', []):
            if level.get('level') == current_level and level.get('status') == 'pending':
                if level.get('role') == role or level.get('approver_id') == user_id:
                    pending.append(wf)
                    break
    
    return pending

# ================= ENDPOINTS =================

@router.get("")
async def get_approval_workflows(
    status: Optional[str] = None,
    document_type: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all approval workflows"""
    await get_current_user(credentials)
    
    query = {}
    if status and status != 'all':
        query['status'] = status
    if document_type and document_type != 'all':
        query['document_type'] = document_type
    
    workflows = await db.approval_workflows.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return workflows

@router.get("/pending")
async def get_pending_approvals(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get pending approvals for the current user"""
    user = await get_current_user(credentials)
    
    # For admin users, return all pending approvals
    if user.get('role') == 'admin':
        workflows = await db.approval_workflows.find(
            {"status": "in_progress"},
            {"_id": 0}
        ).sort("created_at", -1).to_list(100)
        return workflows
    
    # For other users, filter by their role
    user_role = user.get('approval_role', user.get('role', ''))
    return await get_pending_approvals_for_user(user.get('user_id', ''), user_role)

@router.get("/stats")
async def get_approval_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get approval workflow statistics"""
    await get_current_user(credentials)
    
    total = await db.approval_workflows.count_documents({})
    in_progress = await db.approval_workflows.count_documents({"status": "in_progress"})
    approved = await db.approval_workflows.count_documents({"status": "approved"})
    rejected = await db.approval_workflows.count_documents({"status": "rejected"})
    
    # Count by document type
    pipeline = [
        {"$group": {"_id": "$document_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    by_type = await db.approval_workflows.aggregate(pipeline).to_list(20)
    
    # Average approval time (in days) for completed workflows
    completed_workflows = await db.approval_workflows.find(
        {"status": {"$in": ["approved", "rejected"]}},
        {"created_at": 1, "completed_at": 1}
    ).to_list(100)
    
    avg_time = 0
    if completed_workflows:
        total_days = 0
        count = 0
        for wf in completed_workflows:
            if wf.get('completed_at') and wf.get('created_at'):
                try:
                    created = datetime.fromisoformat(str(wf['created_at']).replace('Z', '+00:00'))
                    completed = datetime.fromisoformat(str(wf['completed_at']).replace('Z', '+00:00'))
                    days = (completed - created).days
                    total_days += days
                    count += 1
                except:
                    pass
        if count > 0:
            avg_time = round(total_days / count, 1)
    
    return {
        "total": total,
        "in_progress": in_progress,
        "approved": approved,
        "rejected": rejected,
        "by_type": by_type,
        "average_completion_days": avg_time
    }

@router.get("/configs")
async def get_approval_configs(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get default approval configurations"""
    await get_current_user(credentials)
    return DEFAULT_APPROVAL_CONFIGS

@router.post("")
async def create_approval_workflow(
    data: ApprovalWorkflowCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new approval workflow"""
    user = await get_current_user(credentials)
    
    # Get default config for this document type
    config = DEFAULT_APPROVAL_CONFIGS.get(data.document_type)
    if not config and not data.levels:
        raise HTTPException(status_code=400, detail="Unknown document type and no levels provided")
    
    # Use provided levels or default config
    levels = data.levels if data.levels else [
        {
            **level,
            "status": "pending",
            "approver_id": "",
            "approver_name": "",
            "decision_date": "",
            "comments": "",
            "comments_ar": ""
        }
        for level in config['levels']
    ]
    
    workflow = ApprovalWorkflow(
        document_type=data.document_type,
        document_id=data.document_id,
        document_name=data.document_name,
        document_name_ar=data.document_name_ar,
        requested_by=data.requested_by or user.get('user_id', ''),
        requested_by_name=data.requested_by_name or user.get('name', ''),
        current_level=1,
        total_levels=len(levels),
        levels=levels,
        status="in_progress"
    )
    
    workflow_doc = workflow.model_dump()
    workflow_doc['created_at'] = workflow_doc['created_at'].isoformat()
    
    await db.approval_workflows.insert_one(workflow_doc)
    
    # Notify first level approvers
    first_level = levels[0] if levels else None
    if first_level:
        await create_notification(
            notification_type="approval_required",
            title="Approval Required",
            title_ar="مطلوب موافقة",
            message=f"New approval request for {data.document_name}",
            message_ar=f"طلب موافقة جديد لـ {data.document_name_ar or data.document_name}",
            related_id=workflow.id,
            related_type="approval_workflow"
        )
    
    return {"message": "Approval workflow created", "id": workflow.id}

@router.get("/{workflow_id}")
async def get_approval_workflow(
    workflow_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get a specific approval workflow"""
    await get_current_user(credentials)
    
    workflow = await db.approval_workflows.find_one({"id": workflow_id}, {"_id": 0})
    if not workflow:
        raise HTTPException(status_code=404, detail="Approval workflow not found")
    
    return workflow

@router.post("/{workflow_id}/decide")
async def submit_approval_decision(
    workflow_id: str,
    decision: ApprovalDecision,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Submit an approval decision for the current level"""
    user = await get_current_user(credentials)
    
    workflow = await db.approval_workflows.find_one({"id": workflow_id}, {"_id": 0})
    if not workflow:
        raise HTTPException(status_code=404, detail="Approval workflow not found")
    
    if workflow['status'] != 'in_progress':
        raise HTTPException(status_code=400, detail="This workflow is no longer active")
    
    if decision.status not in ['approved', 'rejected']:
        raise HTTPException(status_code=400, detail="Invalid decision. Use 'approved' or 'rejected'")
    
    current_level = workflow['current_level']
    levels = workflow['levels']
    
    # Update the current level
    for i, level in enumerate(levels):
        if level['level'] == current_level and level['status'] == 'pending':
            levels[i] = {
                **level,
                "status": decision.status,
                "approver_id": user.get('user_id', ''),
                "approver_name": user.get('name', ''),
                "decision_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "comments": decision.comments,
                "comments_ar": decision.comments_ar
            }
            break
    
    # Determine next action
    update_data = {
        "levels": levels,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    if decision.status == 'rejected':
        # Workflow is rejected
        update_data['status'] = 'rejected'
        update_data['final_decision'] = 'rejected'
        update_data['final_decision_date'] = datetime.now().strftime("%Y-%m-%d")
        update_data['completed_at'] = datetime.now(timezone.utc).isoformat()
        
        await create_notification(
            notification_type="approval_rejected",
            title="Approval Rejected",
            title_ar="تم رفض الموافقة",
            message=f"Approval for {workflow['document_name']} was rejected at level {current_level}",
            message_ar=f"تم رفض الموافقة على {workflow.get('document_name_ar') or workflow['document_name']} في المستوى {current_level}",
            related_id=workflow_id,
            related_type="approval_workflow"
        )
    elif current_level < workflow['total_levels']:
        # Move to next level
        update_data['current_level'] = current_level + 1
        
        # Notify next level approvers
        next_level = levels[current_level] if current_level < len(levels) else None
        if next_level:
            await create_notification(
                notification_type="approval_required",
                title="Approval Required",
                title_ar="مطلوب موافقة",
                message=f"Level {current_level + 1} approval required for {workflow['document_name']}",
                message_ar=f"مطلوب موافقة المستوى {current_level + 1} على {workflow.get('document_name_ar') or workflow['document_name']}",
                related_id=workflow_id,
                related_type="approval_workflow"
            )
    else:
        # All levels approved - workflow complete
        update_data['status'] = 'approved'
        update_data['final_decision'] = 'approved'
        update_data['final_decision_date'] = datetime.now().strftime("%Y-%m-%d")
        update_data['completed_at'] = datetime.now(timezone.utc).isoformat()
        
        # Update the source document status
        await update_source_document_status(
            workflow['document_type'],
            workflow['document_id'],
            'approved'
        )
        
        await create_notification(
            notification_type="approval_completed",
            title="Approval Completed",
            title_ar="اكتملت الموافقة",
            message=f"All approvals completed for {workflow['document_name']}",
            message_ar=f"اكتملت جميع الموافقات على {workflow.get('document_name_ar') or workflow['document_name']}",
            related_id=workflow_id,
            related_type="approval_workflow"
        )
    
    await db.approval_workflows.update_one({"id": workflow_id}, {"$set": update_data})
    
    return {
        "message": f"Decision recorded: {decision.status}",
        "workflow_status": update_data.get('status', 'in_progress'),
        "current_level": update_data.get('current_level', current_level)
    }

@router.post("/{workflow_id}/cancel")
async def cancel_approval_workflow(
    workflow_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Cancel an approval workflow"""
    await get_current_user(credentials)
    
    workflow = await db.approval_workflows.find_one({"id": workflow_id})
    if not workflow:
        raise HTTPException(status_code=404, detail="Approval workflow not found")
    
    if workflow['status'] != 'in_progress':
        raise HTTPException(status_code=400, detail="Only in-progress workflows can be cancelled")
    
    await db.approval_workflows.update_one(
        {"id": workflow_id},
        {"$set": {
            "status": "cancelled",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": "Approval workflow cancelled"}

@router.delete("/{workflow_id}")
async def delete_approval_workflow(
    workflow_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete an approval workflow"""
    await get_current_user(credentials)
    
    result = await db.approval_workflows.delete_one({"id": workflow_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Approval workflow not found")
    
    return {"message": "Approval workflow deleted"}

# ================= HELPER FUNCTION =================

async def update_source_document_status(document_type: str, document_id: str, status: str):
    """Update the status of the source document when workflow is completed"""
    collection_map = {
        "contract_review": "contract_reviews",
        "job_order": "job_orders",
        "audit_plan": "audit_plans",
        "technical_review": "technical_reviews",
        "certificate": "certificates",
        "pre_transfer": "pre_transfer_reviews"
    }
    
    collection_name = collection_map.get(document_type)
    if collection_name:
        collection = db[collection_name]
        await collection.update_one(
            {"id": document_id},
            {"$set": {
                "approval_status": status,
                "approval_completed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
