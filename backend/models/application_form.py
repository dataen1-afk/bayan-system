"""
Application form-related Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid


class FormField(BaseModel):
    label: str
    type: str  # text, textarea, number, email, etc.
    required: bool = True
    options: Optional[List[str]] = None


class FormCreate(BaseModel):
    client_id: str
    fields: List[FormField]


class Form(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    fields: List[FormField]
    responses: Optional[Dict[str, Any]] = None
    status: str = "pending"  # pending, submitted
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FormSubmission(BaseModel):
    responses: Dict[str, Any]


class CurrentCertification(BaseModel):
    standard: str = ""
    body: str = ""
    expiry: str = ""


class ApplicationFormData(BaseModel):
    """All possible fields in the application form"""
    # Company Information
    companyName: str = ""
    companyNameArabic: str = ""
    commercialRegNo: str = ""
    crExpiryDate: str = ""
    website: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    city: str = ""
    country: str = ""
    
    # Contact Person
    contactName: str = ""
    contactPosition: str = ""
    contactPhone: str = ""
    contactMobile: str = ""
    contactEmail: str = ""
    
    # Organization Details
    industryType: str = ""
    businessActivity: str = ""
    totalEmployees: str = ""
    operationalShifts: str = ""
    
    # Sites Information
    numberOfSites: str = "1"
    sites: List[Dict[str, Any]] = []
    
    # Audit and Certification
    certificationSchemes: List[str] = []
    otherCertification: str = ""
    certificationScopes: str = ""
    
    # Food Safety Specific (ISO 22000)
    numberOfHACCPStudies: str = ""
    productCategories: str = ""
    processingType: str = ""
    
    # Current Certifications
    currentCertifications: List[CurrentCertification] = []
    
    # Consultant Information
    usedConsultant: str = ""
    consultantName: str = ""
    consultantAffectsImpartiality: str = ""
    
    # Legal Compliance
    lawsuitsPending: str = ""
    lawsuitsDetails: str = ""
    
    # Additional Information
    comments: str = ""


class ClientInfo(BaseModel):
    """Client information for creating application forms"""
    name: str
    company_name: str
    email: str
    phone: str


class AuditCalculationResult(BaseModel):
    certifications: Dict[str, Any]
    total_md: float
    reduction: float
    final_total_md: float
    phases: Dict[str, float]


class ApplicationFormCreate(BaseModel):
    client: ClientInfo


class ApplicationForm(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    access_token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client: ClientInfo
    data: Optional[ApplicationFormData] = None
    audit_calculation: Optional[AuditCalculationResult] = None
    status: str = "pending"  # pending, submitted, proposal_sent, agreement_pending, agreement_signed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


class ApplicationFormUpdate(BaseModel):
    data: ApplicationFormData


class PublicApplicationFormResponse(BaseModel):
    id: str
    client: ClientInfo
    data: Optional[ApplicationFormData]
    status: str
