"""
Certification Agreement-related Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime, timezone
import uuid


class AgreementAcknowledgements(BaseModel):
    certificationRules: bool = False
    publicDirectory: bool = False
    certificationCommunication: bool = False
    surveillanceSchedule: bool = False
    nonconformityResolution: bool = False
    feesAndPayment: bool = False


class CertificationAgreementSubmit(BaseModel):
    organization_name: str
    organization_address: str
    selected_standards: List[str]
    other_standard: str = ""
    scope_of_services: str
    sites: List[str]
    signatory_name: str
    signatory_position: str
    signatory_date: str
    acknowledgements: AgreementAcknowledgements
    signature_image: str  # Base64 encoded signature image (required)
    stamp_image: str  # Base64 encoded stamp image (required)


class CertificationAgreement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposal_id: str
    proposal_access_token: str
    organization_name: str
    organization_address: str
    selected_standards: List[str]
    other_standard: str = ""
    scope_of_services: str
    sites: List[str]
    signatory_name: str
    signatory_position: str
    signatory_date: str
    acknowledgements: Dict[str, bool] = {}
    signature_image: Optional[str] = None  # Base64 encoded signature image
    stamp_image: Optional[str] = None  # Base64 encoded stamp image
    status: str = "submitted"  # submitted, contract_generated
    contract_pdf_path: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Legacy contract model
class Contract(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quotation_id: str
    client_id: str
    pdf_path: str
    status: str = "active"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
