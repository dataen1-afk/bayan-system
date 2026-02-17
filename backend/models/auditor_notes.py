"""
Auditor Notes (BACF6-12) Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import uuid


class AuditorNotesCreate(BaseModel):
    """Create Auditor Notes - can be from Stage 2 report or independently"""
    stage2_report_id: Optional[str] = None  # Optional link to Stage 2 report
    # If not from report, these fields are required
    client_name: str = ""
    location: str = ""
    standards: List[str] = []
    auditor_name: str = ""
    audit_type: str = ""  # Stage 1, Stage 2, Surveillance, Recertification
    audit_date: str = ""
    department: str = ""


class AuditorNotesUpdate(BaseModel):
    """Update Auditor Notes"""
    client_name: str = ""
    location: str = ""
    standards: List[str] = []
    auditor_name: str = ""
    audit_type: str = ""
    audit_date: str = ""
    department: str = ""
    notes: str = ""  # Main auditor notes content
    notes_ar: str = ""  # Arabic notes


class AuditorNotes(BaseModel):
    """Auditor Notes (BACF6-12) - Created by auditor after audit"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    stage2_report_id: Optional[str] = None
    stage1_report_id: Optional[str] = None
    job_order_id: str = ""
    audit_program_id: str = ""
    contract_review_id: str = ""
    # Form fields
    client_name: str = ""
    client_name_ar: str = ""
    location: str = ""
    location_ar: str = ""
    standards: List[str] = []
    auditor_id: str = ""
    auditor_name: str = ""
    auditor_name_ar: str = ""
    audit_type: str = ""  # Stage 1, Stage 2, Surveillance 1, Surveillance 2, Recertification
    audit_date: str = ""
    department: str = ""
    department_ar: str = ""
    # Notes content
    notes: str = ""
    notes_ar: str = ""
    # Status
    status: str = "draft"  # draft, completed
    completed_at: Optional[datetime] = None
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
