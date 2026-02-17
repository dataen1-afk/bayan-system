"""
Nonconformity Report (BACF6-13) Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid


class NonconformityItem(BaseModel):
    """Single nonconformity entry in the report"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    standard_clause: str = ""  # e.g., "ISO 9001:2015 Clause 7.1.5"
    description: str = ""  # Description of nonconformity
    description_ar: str = ""
    nc_type: str = "minor"  # "major" or "minor" (MJ or MN)
    root_cause: str = ""  # Root cause analysis
    root_cause_ar: str = ""
    corrections: str = ""  # Immediate corrections taken
    corrections_ar: str = ""
    corrective_actions: str = ""  # Long-term corrective actions
    corrective_actions_ar: str = ""
    # Verification
    verification_evidence: str = ""  # Evidence provided
    verification_decision: str = ""  # auditor's decision
    verification_date: str = ""
    verified_by: str = ""
    # Status
    status: str = "open"  # open, closed, pending_verification


class NonconformityReportCreate(BaseModel):
    """Create Nonconformity Report - from Stage 2 report or independently"""
    stage2_report_id: Optional[str] = None  # Optional link to Stage 2 report
    # If not from report, these fields are required
    client_name: str = ""
    certificate_no: str = ""
    standards: List[str] = []
    audit_type: str = ""
    audit_date: str = ""
    lead_auditor: str = ""
    management_representative: str = ""


class NonconformityReportUpdate(BaseModel):
    """Update Nonconformity Report"""
    client_name: Optional[str] = None
    certificate_no: Optional[str] = None
    standards: Optional[List[str]] = None
    audit_type: Optional[str] = None
    audit_date: Optional[str] = None
    lead_auditor: Optional[str] = None
    management_representative: Optional[str] = None
    nonconformities: Optional[List[Dict[str, Any]]] = None
    submission_deadline: Optional[str] = None
    # Verification options
    verification_options: Optional[Dict[str, bool]] = None
    # Signatures
    management_rep_signature: Optional[str] = None
    management_rep_date: Optional[str] = None
    audit_team_leader_signature: Optional[str] = None
    audit_team_leader_date: Optional[str] = None
    evidence_submission_date: Optional[str] = None


class NonconformityReport(BaseModel):
    """Nonconformity Report (BACF6-13) - Documents audit findings and corrective actions"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    stage2_report_id: str = ""
    job_order_id: str = ""
    audit_program_id: str = ""
    contract_review_id: str = ""
    # Header fields
    client_name: str = ""
    client_name_ar: str = ""
    certificate_no: str = ""
    standards: List[str] = []
    audit_type: str = ""  # Stage 1, Stage 2, Surveillance, Recertification
    audit_date: str = ""
    lead_auditor: str = ""
    lead_auditor_ar: str = ""
    management_representative: str = ""
    management_representative_ar: str = ""
    # Nonconformities list
    nonconformities: List[Dict[str, Any]] = []  # List of NonconformityItem dicts
    # Deadline
    submission_deadline: str = ""  # Deadline for submitting corrective action evidence
    # Verification options (checkboxes)
    verification_options: Dict[str, bool] = {
        "corrections_appropriate": False,
        "corrections_verified": False,
        "verify_next_audit": False,
        "re_audit_performed": False
    }
    # Signatures
    management_rep_signature: str = ""
    management_rep_date: str = ""
    audit_team_leader_signature: str = ""
    audit_team_leader_date: str = ""
    evidence_submission_date: str = ""
    final_lead_auditor_signature: str = ""
    final_date: str = ""
    # Status
    status: str = "draft"  # draft, sent_to_client, pending_verification, closed
    # Stats
    total_major: int = 0
    total_minor: int = 0
    closed_count: int = 0
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
