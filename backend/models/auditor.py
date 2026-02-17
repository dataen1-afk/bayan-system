"""
Auditor management Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import uuid


class AuditorAvailability(BaseModel):
    date: str  # YYYY-MM-DD
    available: bool = True
    notes: str = ""


class Auditor(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    name_ar: str = ""
    email: str = ""
    phone: str = ""
    mobile: str = ""
    employee_id: str = ""
    # Certification level
    certification_level: str = "auditor"  # trainee, auditor, lead_auditor, technical_expert
    # Specializations
    specializations: List[str] = []  # ISO standards they can audit
    years_experience: int = 0
    max_audits_per_month: int = 4
    # Availability
    availability: List[AuditorAvailability] = []
    # Status
    status: str = "active"  # active, inactive, on_leave
    notes: str = ""
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


class AuditorCreate(BaseModel):
    name: str
    name_ar: str = ""
    email: str = ""
    phone: str = ""
    mobile: str = ""
    employee_id: str = ""
    certification_level: str = "auditor"
    specializations: List[str] = []
    years_experience: int = 0
    max_audits_per_month: int = 4
    notes: str = ""


class AuditAssignment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    audit_id: str
    auditor_id: str
    role: str = "auditor"  # lead_auditor, auditor, technical_expert
    status: str = "assigned"  # assigned, confirmed, declined, completed
    confirmed_at: Optional[datetime] = None
    notes: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
