"""
Audit Plan (BACF6-07 Stage 1 & BACF6-08 Stage 2) Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid


# ================= COMMON MODELS =================

class ScheduleEntry(BaseModel):
    """Single schedule entry in the audit plan"""
    date_time: str = ""  # Date and time range
    process: str = ""  # Process being audited
    process_owner: str = ""  # Process owner/auditee
    clauses: str = ""  # Applicable ISO clauses
    auditor: str = ""  # Assigned auditor name


class TeamMember(BaseModel):
    """Team member in the audit"""
    auditor_id: str = ""
    name: str = ""
    name_ar: str = ""
    role: str = "Auditor"  # Team Leader, Auditor, Technical Expert, Evaluator


# ================= STAGE 1 AUDIT PLAN MODELS (BACF6-07) =================

class Stage1AuditPlanCreate(BaseModel):
    """Create a new Stage 1 Audit Plan from a confirmed Job Order"""
    job_order_id: str  # Reference to confirmed job order


class Stage1AuditPlanUpdate(BaseModel):
    """Update Stage 1 Audit Plan data"""
    # Client contact
    contact_person: str = ""
    contact_phone: str = ""
    contact_designation: str = ""
    contact_email: str = ""
    # Audit details
    audit_language: str = "English"
    audit_date_from: str = ""
    audit_date_to: str = ""
    # Team members (additional to team leader)
    team_members: List[TeamMember] = []
    # Schedule
    schedule_entries: List[ScheduleEntry] = []
    notes: str = ""


class Stage1AuditPlanClientResponse(BaseModel):
    """Client response to the audit plan"""
    accepted: bool = True
    change_requests: str = ""  # If not accepted, requested changes


class Stage1AuditPlan(BaseModel):
    """Stage 1 Audit Plan (BACF6-07) - Phase 1 audit planning"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    access_token: str = Field(default_factory=lambda: str(uuid.uuid4()))  # For client review link
    job_order_id: str  # Reference to job order
    audit_program_id: str = ""
    contract_review_id: str = ""
    # Client information (from job order)
    organization_name: str = ""
    file_no: str = ""
    address: str = ""
    plan_date: str = ""
    contact_person: str = ""
    contact_phone: str = ""
    contact_designation: str = ""
    contact_email: str = ""
    # Audit details (from job order)
    standards: List[str] = []
    audit_language: str = "English"
    audit_type: str = "Stage 1"
    audit_date_from: str = ""
    audit_date_to: str = ""
    scope: str = ""
    # Team (Team Leader from Job Order)
    team_leader: Dict[str, Any] = {}  # {auditor_id, name, name_ar, role}
    team_members: List[Dict[str, Any]] = []  # Additional team members
    # Schedule
    schedule_entries: List[Dict[str, Any]] = []  # List of ScheduleEntry dicts
    # Manager approval (internal)
    manager_approved: bool = False
    manager_name: str = ""
    manager_approval_date: str = ""
    # Client acceptance
    sent_to_client: bool = False
    client_accepted: bool = False
    client_acceptance_date: str = ""
    client_change_requests: str = ""
    # Status
    status: str = "draft"  # draft, pending_manager, manager_approved, pending_client, client_accepted, changes_requested, completed
    notes: str = ""
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


# ================= STAGE 2 AUDIT PLAN MODELS (BACF6-08) =================

class Stage2AuditPlanCreate(BaseModel):
    """Create a new Stage 2 Audit Plan - from Stage 1 or independently"""
    stage1_plan_id: Optional[str] = None  # Optional - if from Stage 1 plan
    job_order_id: Optional[str] = None  # Optional - if creating independently
    audit_type: str = "Stage 2"  # Stage 2, Renewal, Surveillance


class Stage2AuditPlanUpdate(BaseModel):
    """Update Stage 2 Audit Plan data"""
    contact_person: str = ""
    contact_phone: str = ""
    contact_designation: str = ""
    contact_email: str = ""
    audit_language: str = "English"
    audit_date_from: str = ""
    audit_date_to: str = ""
    team_members: List[TeamMember] = []
    schedule_entries: List[ScheduleEntry] = []
    notes: str = ""


class Stage2AuditPlanClientResponse(BaseModel):
    """Client response to the Stage 2 audit plan"""
    accepted: bool = True
    change_requests: str = ""


class Stage2AuditPlan(BaseModel):
    """Stage 2 Audit Plan (BACF6-08) - Phase 2 audit planning"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    access_token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    stage1_plan_id: Optional[str] = None
    job_order_id: Optional[str] = None
    audit_program_id: str = ""
    contract_review_id: str = ""
    # Client information
    organization_name: str = ""
    file_no: str = ""
    address: str = ""
    plan_date: str = ""
    contact_person: str = ""
    contact_phone: str = ""
    contact_designation: str = ""
    contact_email: str = ""
    # Audit details
    standards: List[str] = []
    audit_language: str = "English"
    audit_type: str = "Stage 2"
    audit_date_from: str = ""
    audit_date_to: str = ""
    scope: str = ""
    # Team
    team_leader: Dict[str, Any] = {}
    team_members: List[Dict[str, Any]] = []
    # Schedule
    schedule_entries: List[Dict[str, Any]] = []
    # Manager approval
    manager_approved: bool = False
    manager_name: str = ""
    manager_approval_date: str = ""
    # Client acceptance
    sent_to_client: bool = False
    client_accepted: bool = False
    client_acceptance_date: str = ""
    client_change_requests: str = ""
    # Status
    status: str = "draft"
    notes: str = ""
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
