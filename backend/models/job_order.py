"""
Job Order (BACF6-06) Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import uuid


class JobOrderCreate(BaseModel):
    """Create a new Job Order from an Audit Program"""
    audit_program_id: str  # Reference to audit program
    auditor_id: str  # Selected auditor from system
    position: str = "Auditor"  # Auditor, Lead Auditor, Technical Expert
    audit_type: str = ""  # Stage 1, Stage 2, Surveillance 1, Surveillance 2, Recertification
    audit_date: str = ""  # YYYY-MM-DD


class JobOrderUpdate(BaseModel):
    """Update job order (admin)"""
    position: str = "Auditor"
    audit_type: str = ""
    audit_date: str = ""
    certification_manager: str = ""
    manager_approval_date: str = ""
    notes: str = ""


class JobOrderAuditorConfirmation(BaseModel):
    """Auditor confirmation of job order"""
    confirmed: bool = True
    unable_reason: str = ""  # If not confirmed, reason why


class JobOrder(BaseModel):
    """Job Order (BACF6-06) - Auditor appointment for audit"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    access_token: str = Field(default_factory=lambda: str(uuid.uuid4()))  # For auditor confirmation link
    audit_program_id: str  # Reference to audit program
    contract_review_id: str = ""  # Reference to contract review
    agreement_id: str = ""  # Reference to certification agreement
    # Auditor info
    auditor_id: str
    auditor_name: str = ""
    auditor_name_ar: str = ""
    auditor_email: str = ""
    position: str = "Auditor"  # Auditor, Lead Auditor, Technical Expert
    # Client/Audit details (from audit program)
    organization_name: str = ""
    organization_address: str = ""
    total_employees: int = 0
    phone: str = ""
    scope_of_services: str = ""
    standards: List[str] = []
    audit_type: str = ""  # Stage 1, Stage 2, Surveillance 1, Surveillance 2, Recertification
    audit_date: str = ""
    client_ref: str = ""
    # Manager approval
    certification_manager: str = ""
    manager_approval_date: str = ""
    manager_approved: bool = False
    # Auditor confirmation
    auditor_confirmed: bool = False
    auditor_confirmation_date: str = ""
    unable_reason: str = ""  # If auditor can't perform
    # Status
    status: str = "pending_approval"  # pending_approval, approved, pending_auditor, confirmed, rejected, completed
    notes: str = ""
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
