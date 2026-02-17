"""
Proposal/Quotation-related Pydantic models.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime, timezone
import uuid


class AuditDuration(BaseModel):
    stage_1: float = 0
    stage_2: float = 0
    surveillance_1: float = 0
    surveillance_2: float = 0
    recertification: float = 0


class ServiceFees(BaseModel):
    initial_certification: float = 0
    surveillance_1: float = 0
    surveillance_2: float = 0
    recertification: float = 0
    currency: str = "SAR"


class ProposalCreate(BaseModel):
    application_form_id: str
    # Organization details (pre-filled from application)
    organization_name: str
    organization_address: str
    organization_phone: str
    contact_person: str
    contact_position: str
    contact_email: EmailStr
    # Service details
    standards: List[str]
    scope: str
    total_employees: int
    number_of_sites: int
    # Audit duration
    audit_duration: AuditDuration
    # Pricing
    service_fees: ServiceFees
    # Additional notes
    notes: str = ""
    # Validity
    validity_days: int = 30
    # First Party (Bayan) authorized signatory
    issuer_name: str = "Abdullah Al-Rashid"  # Default authorized signatory
    issuer_designation: str = "General Manager"  # Default job title
    issuer_signature: str = ""  # Base64 encoded signature image
    issuer_stamp: str = ""  # Base64 encoded stamp image


class Proposal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    access_token: str = Field(default_factory=lambda: str(uuid.uuid4()))  # For client access
    application_form_id: str
    # Organization details
    organization_name: str
    organization_address: str
    organization_phone: str
    contact_person: str
    contact_position: str
    contact_email: EmailStr
    # Service details
    standards: List[str]
    scope: str
    total_employees: int
    number_of_sites: int
    # Audit duration
    audit_duration: AuditDuration
    # Pricing
    service_fees: ServiceFees
    total_amount: float = 0
    # Additional
    notes: str = ""
    validity_days: int = 30
    # Status
    status: str = "pending"  # pending, accepted, rejected, expired
    # First Party (Bayan) Signatures
    issuer_name: str = ""
    issuer_designation: str = ""
    issuer_signature: str = ""  # Base64 encoded signature image
    issuer_stamp: str = ""  # Base64 encoded stamp image
    issued_date: Optional[datetime] = None
    # Client response
    client_response_date: Optional[datetime] = None
    client_signatory_name: str = ""
    client_signatory_designation: str = ""
    rejection_reason: str = ""
    # Modification tracking
    modification_comment: str = ""
    modification_requested_changes: str = ""
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProposalResponse(BaseModel):
    status: str  # accepted or rejected
    signatory_name: str = ""
    signatory_designation: str = ""
    rejection_reason: str = ""


class ModificationRequest(BaseModel):
    comment: str
    requested_changes: str = ""


class PublicProposalResponse(BaseModel):
    id: str
    organization_name: str
    organization_address: str = ""
    contact_person: str
    contact_email: str
    standards: List[str]
    scope: str
    total_employees: int
    number_of_sites: int
    audit_duration: AuditDuration
    service_fees: ServiceFees
    total_amount: float
    notes: str
    validity_days: int
    status: str
    issuer_name: str
    issuer_designation: str
    issued_date: Optional[datetime]
    modification_comment: str = ""
    modification_requested_changes: str = ""


# Legacy quotation models for backwards compatibility
class QuotationCreate(BaseModel):
    form_id: str
    price: float
    details: str
    validity_days: int = 30


class Quotation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    form_id: str
    client_id: str
    price: float
    details: str
    status: str = "pending"  # pending, approved, rejected
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class QuotationResponse(BaseModel):
    approved: bool
