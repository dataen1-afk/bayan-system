"""
Template-related Pydantic models (Certification Packages and Proposal Templates).
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import uuid


class CertificationPackage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    name_ar: str = ""
    standards: List[str]  # List of ISO standards included
    description: str = ""
    description_ar: str = ""
    is_default: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProposalTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    name_ar: str = ""
    # Fee structure
    initial_certification_fee: float = 0
    surveillance_1_fee: float = 0
    surveillance_2_fee: float = 0
    recertification_fee: float = 0
    currency: str = "SAR"
    # Details
    description: str = ""
    description_ar: str = ""
    validity_days: int = 30
    is_default: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
