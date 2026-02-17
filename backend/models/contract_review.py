"""
Contract Review (BACF6-04) and Audit Program (BACF6-05) Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid


# ================= CONTRACT REVIEW MODELS (BACF6-04) =================

class AuditTimeEntry(BaseModel):
    standard: str = ""  # ISO 9001, ISO 14001, etc.
    audit_type: str = ""  # SA1, SA2, SUR1, SUR2, RE
    num_days: float = 0
    percent_increase: float = 0
    percent_reduction: float = 0
    final_days: float = 0


class ContractReviewCreate(BaseModel):
    agreement_id: str  # Reference to certification agreement


class ContractReviewClientSubmit(BaseModel):
    """Data submitted by client"""
    consultant_name: str = ""
    consultant_affects_impartiality: bool = False
    consultant_impact_explanation: str = ""
    exclusions_justification: str = ""


class ContractReviewAdminUpdate(BaseModel):
    """Data filled by admin/auditor"""
    contract_review_date: str = ""
    risk_category: str = ""  # For QMS
    complexity_category: str = ""  # For other standards
    integration_level_percent: float = 100
    combined_audit_ability_percent: float = 100
    auditor_code_matched: bool = False
    # Audit time calculations
    audit_times: List[AuditTimeEntry] = []
    final_man_days: float = 0
    # Team assignment
    lead_auditor_id: str = ""
    lead_auditor_name: str = ""
    auditor_ids: List[str] = []
    auditor_names: List[str] = []
    other_team_members: str = ""
    technical_expert_needed: bool = False
    technical_expert_name: str = ""
    certification_decision_maker: str = ""
    # Approval
    prepared_by_name: str = ""
    prepared_by_date: str = ""
    reviewed_by_name: str = ""
    reviewed_by_date: str = ""


class ContractReview(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    access_token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agreement_id: str  # Reference to certification agreement
    # Auto-populated from agreement
    organization_name: str = ""
    standards: List[str] = []
    scope_of_services: str = ""
    total_employees: int = 0
    application_date: str = ""
    client_id: str = ""
    # Client-filled data
    consultant_name: str = ""
    consultant_affects_impartiality: bool = False
    consultant_impact_explanation: str = ""
    exclusions_justification: str = ""
    client_submitted: bool = False
    client_submitted_at: Optional[datetime] = None
    # Admin-filled data
    contract_review_date: str = ""
    risk_category: str = ""
    complexity_category: str = ""
    integration_level_percent: float = 100
    combined_audit_ability_percent: float = 100
    auditor_code_matched: bool = False
    audit_times: List[Dict[str, Any]] = []
    final_man_days: float = 0
    lead_auditor_id: str = ""
    lead_auditor_name: str = ""
    auditor_ids: List[str] = []
    auditor_names: List[str] = []
    other_team_members: str = ""
    technical_expert_needed: bool = False
    technical_expert_name: str = ""
    certification_decision_maker: str = ""
    prepared_by_name: str = ""
    prepared_by_date: str = ""
    reviewed_by_name: str = ""
    reviewed_by_date: str = ""
    # Status
    status: str = "pending_client"  # pending_client, pending_review, completed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


# ================= AUDIT PROGRAM MODELS (BACF6-05) =================

class AuditActivityEntry(BaseModel):
    """Single audit activity row in the program"""
    activity: str = ""  # Audit activity description
    audit_type: str = ""  # Desktop, On-site, etc.
    stage1: str = ""  # Stage 1 allocation (e.g., "1 day")
    stage2: str = ""  # Stage 2 allocation
    sur1: str = ""  # Surveillance 1 allocation
    sur2: str = ""  # Surveillance 2 allocation
    rc: str = ""  # Recertification allocation
    planned_date: str = ""  # YYYY-MM-DD


class AuditProgramCreate(BaseModel):
    """Create a new Audit Program from a Contract Review"""
    contract_review_id: str  # Reference to contract review


class AuditProgramUpdate(BaseModel):
    """Update audit program data"""
    num_shifts: int = 1
    activities: List[AuditActivityEntry] = []
    certification_manager: str = ""
    approval_date: str = ""
    notes: str = ""


class AuditProgram(BaseModel):
    """Audit Program (BACF6-05) - schedules audit stages"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    access_token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contract_review_id: str  # Reference to contract review
    agreement_id: str = ""  # Reference to certification agreement
    # Auto-populated from contract review/agreement
    organization_name: str = ""
    standards: List[str] = []
    scope_of_services: str = ""
    total_employees: int = 0
    # Program data
    num_shifts: int = 1
    activities: List[Dict[str, Any]] = []  # List of AuditActivityEntry dicts
    # Approval
    certification_manager: str = ""
    approval_date: str = ""
    notes: str = ""
    # Status
    status: str = "draft"  # draft, approved, in_progress, completed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
