"""
Audit Report (BACF6-10 Stage 1 & BACF6-11 Stage 2) Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid


# ================= COMMON MODELS =================

class AuditFinding(BaseModel):
    """Positive finding in the audit"""
    description: str = ""
    description_ar: str = ""


class ChecklistItem(BaseModel):
    """Single item in the audit checklist"""
    requirement: str = ""
    requirement_ar: str = ""
    status: str = ""  # C (Conformity), NC (Non-Conformity), O (Observation/OFI)


# ================= STAGE 1 AUDIT REPORT MODELS (BACF6-10) =================

class AuditConcern(BaseModel):
    """Area of concern (Stage 1)"""
    description: str = ""
    description_ar: str = ""
    rating: int = 1  # 1=OFI, 2=Probable NC in Stage 2, 3=Not Ready


class Stage1AuditReportCreate(BaseModel):
    """Create a new Stage 1 Audit Report"""
    stage1_plan_id: str  # Reference to client-accepted Stage 1 plan
    meeting_id: Optional[str] = None  # Optional link to Opening/Closing Meeting


class Stage1AuditReportUpdate(BaseModel):
    """Update Stage 1 Audit Report data"""
    # Change details
    change_details: str = ""
    change_details_ar: str = ""
    # Findings
    positive_findings: List[AuditFinding] = []
    areas_of_concern: List[AuditConcern] = []
    # Team leader declarations
    declarations: Dict[str, bool] = {}
    # Recommendation
    recommendation: str = ""  # proceed_stage2, not_proceed, further_stage1
    recommendation_notes: str = ""
    # Checklist
    checklist: List[ChecklistItem] = []


class Stage1AuditReport(BaseModel):
    """Stage 1 Audit Report (BACF6-10)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    stage1_plan_id: str
    meeting_id: Optional[str] = None
    job_order_id: str = ""
    audit_program_id: str = ""
    contract_review_id: str = ""
    # Organization info
    organization_name: str = ""
    standards: List[str] = []
    scope: str = ""
    audit_type: str = "Stage 1"
    audit_date_from: str = ""
    audit_date_to: str = ""
    total_duration: str = ""
    # Team info
    team_leader: Dict[str, Any] = {}
    team_members: List[Dict[str, Any]] = []
    # Change details
    change_details: str = ""
    change_details_ar: str = ""
    # Attendance (from meeting if linked)
    attendance: List[Dict[str, Any]] = []
    # Findings
    positive_findings: List[Dict[str, Any]] = []
    areas_of_concern: List[Dict[str, Any]] = []
    # Declarations
    declarations: Dict[str, bool] = {}
    # Recommendation
    recommendation: str = ""
    recommendation_notes: str = ""
    # Checklist
    checklist: List[Dict[str, Any]] = []
    # Status
    status: str = "draft"  # draft, completed, approved
    completed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approved_by: str = ""
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


# ================= STAGE 2 AUDIT REPORT MODELS (BACF6-11) =================

class Nonconformity(BaseModel):
    """Non-conformity finding (Stage 2)"""
    description: str = ""
    description_ar: str = ""
    rating: int = 1  # 1=Minor NC, 2=Major NC


class OpportunityForImprovement(BaseModel):
    """Opportunity for Improvement (OFI)"""
    description: str = ""
    description_ar: str = ""


class Stage2AuditReportCreate(BaseModel):
    """Create a new Stage 2 Audit Report"""
    stage2_plan_id: str  # Reference to client-accepted Stage 2 plan
    stage1_report_id: Optional[str] = None  # Optional link to Stage 1 report


class Stage2AuditReportUpdate(BaseModel):
    """Update Stage 2 Audit Report data"""
    # Change details
    change_details: str = ""
    change_details_ar: str = ""
    # Findings
    positive_findings: List[AuditFinding] = []
    opportunities_for_improvement: List[OpportunityForImprovement] = []
    nonconformities: List[Nonconformity] = []
    # Certification recommendations (checkboxes)
    cert_recommendations: Dict[str, bool] = {}
    # Overall recommendation
    overall_recommendation: str = ""
    overall_recommendation_notes: str = ""
    # Checklist
    checklist: List[ChecklistItem] = []


class Stage2AuditReport(BaseModel):
    """Stage 2 Audit Report (BACF6-11)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    stage2_plan_id: str
    stage1_report_id: Optional[str] = None
    job_order_id: str = ""
    audit_program_id: str = ""
    contract_review_id: str = ""
    # Organization info
    organization_name: str = ""
    standards: List[str] = []
    scope: str = ""
    audit_type: str = "Stage 2"
    audit_date_from: str = ""
    audit_date_to: str = ""
    total_duration: str = ""
    # Team info
    team_leader: Dict[str, Any] = {}
    team_members: List[Dict[str, Any]] = []
    # Change details
    change_details: str = ""
    change_details_ar: str = ""
    # Findings
    positive_findings: List[Dict[str, Any]] = []
    opportunities_for_improvement: List[Dict[str, Any]] = []
    nonconformities: List[Dict[str, Any]] = []
    # Certification recommendations
    cert_recommendations: Dict[str, bool] = {}
    # Overall recommendation
    overall_recommendation: str = ""
    overall_recommendation_notes: str = ""
    # Checklist
    checklist: List[Dict[str, Any]] = []
    # Status
    status: str = "draft"  # draft, completed, approved
    completed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approved_by: str = ""
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
