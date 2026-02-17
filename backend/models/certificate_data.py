"""
Certificate Data (BACF6-14) Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import uuid


class CertificateDataCreate(BaseModel):
    """Create Certificate Data - from NC report or independently"""
    nc_report_id: Optional[str] = None  # Optional link to NC report
    stage2_report_id: Optional[str] = None  # Optional link to Stage 2 report
    # If not from report, these fields can be provided
    client_name: str = ""
    standards: List[str] = []
    lead_auditor: str = ""
    audit_type: str = ""
    audit_date: str = ""


class CertificateDataUpdate(BaseModel):
    """Update Certificate Data"""
    client_name: Optional[str] = None
    standards: Optional[List[str]] = None
    lead_auditor: Optional[str] = None
    audit_type: Optional[str] = None
    audit_date: Optional[str] = None
    # Certification scope
    agreed_certification_scope: Optional[str] = None
    agreed_certification_scope_ar: Optional[str] = None
    ea_code: Optional[str] = None
    technical_category: Optional[str] = None
    # Company data - Local Language (Arabic)
    company_data_local: Optional[str] = None
    certification_scope_local: Optional[str] = None
    # Company data - English
    company_data_english: Optional[str] = None
    certification_scope_english: Optional[str] = None
    # Client confirmation
    client_signature: Optional[str] = None  # Base64 image
    client_stamp: Optional[str] = None  # Base64 image
    client_signature_date: Optional[str] = None
    # Certificate details (generated)
    certificate_number: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None


class CertificateData(BaseModel):
    """Certificate Data (BACF6-14) - Confirmation of details for certificate printing"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    access_token: str = Field(default_factory=lambda: str(uuid.uuid4()))  # For client access
    nc_report_id: str = ""
    stage2_report_id: str = ""
    job_order_id: str = ""
    audit_program_id: str = ""
    contract_review_id: str = ""
    agreement_id: str = ""
    # Header fields
    client_name: str = ""
    client_name_ar: str = ""
    standards: List[str] = []
    lead_auditor: str = ""
    lead_auditor_ar: str = ""
    audit_type: str = ""  # CA (Certification Audit), RA (Recertification Audit), Surveillance, Extension, Special
    audit_date: str = ""
    # Certification scope
    agreed_certification_scope: str = ""
    agreed_certification_scope_ar: str = ""
    ea_code: str = ""  # EA Code
    technical_category: str = ""
    # Company data - Local Language (Arabic)
    company_data_local: str = ""  # Company name, address in Arabic
    certification_scope_local: str = ""  # Certification scope in Arabic
    # Company data - English
    company_data_english: str = ""  # Company name, address in English
    certification_scope_english: str = ""  # Certification scope in English
    # Client confirmation
    client_signature: str = ""  # Base64 image
    client_stamp: str = ""  # Base64 image
    client_signature_date: str = ""
    client_confirmed: bool = False
    client_confirmed_at: Optional[datetime] = None
    # Certificate details (to be filled after approval)
    certificate_number: str = ""
    issue_date: str = ""
    expiry_date: str = ""
    certificate_generated: bool = False
    # Status
    status: str = "draft"  # draft, sent_to_client, client_confirmed, certificate_issued
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


class CertificateDataClientConfirm(BaseModel):
    """Client confirmation of certificate data"""
    client_signature: str = ""  # Base64 image
    client_stamp: str = ""  # Base64 image
    signature_date: str = ""
