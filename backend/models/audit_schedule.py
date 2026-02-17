"""
Audit Schedule Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import uuid


class AuditSchedule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contract_id: str
    organization_name: str
    # Audit details
    audit_type: str  # initial, surveillance_1, surveillance_2, recertification
    standards: List[str] = []
    # Schedule
    scheduled_date: str  # YYYY-MM-DD
    scheduled_time: str = ""  # HH:MM
    duration_days: float = 1
    # Location
    location: str = ""
    is_remote: bool = False
    # Team
    lead_auditor_id: str = ""
    lead_auditor_name: str = ""
    auditor_ids: List[str] = []
    auditor_names: List[str] = []
    # Status
    status: str = "scheduled"  # scheduled, in_progress, completed, cancelled
    # Recurring
    is_recurring: bool = False
    recurrence_pattern: str = ""  # weekly, monthly, quarterly, yearly
    recurrence_end_date: str = ""
    # Notes
    notes: str = ""
    # Google Calendar
    google_calendar_event_id: str = ""
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


class AuditScheduleCreate(BaseModel):
    contract_id: str
    audit_type: str
    scheduled_date: str
    scheduled_time: str = ""
    duration_days: float = 1
    location: str = ""
    is_remote: bool = False
    lead_auditor_id: str = ""
    auditor_ids: List[str] = []
    notes: str = ""
    is_recurring: bool = False
    recurrence_pattern: str = ""
    recurrence_end_date: str = ""
