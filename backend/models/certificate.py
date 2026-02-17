"""
Certificate-related Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import uuid


class Certificate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    certificate_number: str = ""  # Auto-generated: CERT-YYYY-XXXX
    contract_id: str  # Reference to certification agreement
    audit_id: str = ""  # Reference to the final audit that granted certification
    # Organization details
    organization_name: str
    organization_name_ar: str = ""
    # Certification details
    standards: List[str] = []  # ISO 9001, ISO 14001, etc.
    scope: str = ""
    scope_ar: str = ""
    # Dates
    issue_date: str  # YYYY-MM-DD
    expiry_date: str  # YYYY-MM-DD (typically 3 years from issue)
    # Status
    status: str = "active"  # active, suspended, withdrawn, expired
    # QR Code
    verification_url: str = ""  # URL for QR code verification
    qr_code_data: str = ""  # Base64 encoded QR code image
    # Audit details
    lead_auditor: str = ""
    audit_team: List[str] = []
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


class CertificateCreate(BaseModel):
    contract_id: str
    audit_id: str = ""
    standards: List[str] = []
    scope: str = ""
    scope_ar: str = ""
    lead_auditor: str = ""
    audit_team: List[str] = []
