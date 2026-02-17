"""
Opening & Closing Meeting (BACF6-09) Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid


class MeetingAttendee(BaseModel):
    """Single attendee in the meeting"""
    name: str = ""
    designation: str = ""
    opening_date: str = ""  # When attended opening meeting
    closing_date: str = ""  # When attended closing meeting


class OpeningClosingMeetingCreate(BaseModel):
    """Create a new Opening/Closing Meeting form"""
    stage1_plan_id: str  # Reference to client-accepted Stage 1 plan


class OpeningClosingMeetingSubmit(BaseModel):
    """Client submission of meeting data"""
    attendees: List[MeetingAttendee] = []
    opening_notes: str = ""
    closing_notes: str = ""


class OpeningClosingMeeting(BaseModel):
    """Opening & Closing Meeting (BACF6-09)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    access_token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    stage1_plan_id: str
    job_order_id: str = ""
    audit_program_id: str = ""
    contract_review_id: str = ""
    # Client information
    organization_name: str = ""
    standards: List[str] = []
    audit_type: str = ""
    audit_date_from: str = ""
    audit_date_to: str = ""
    # Attendees
    attendees: List[Dict[str, Any]] = []
    opening_notes: str = ""
    closing_notes: str = ""
    # Status
    status: str = "pending"  # pending, sent_to_client, submitted
    sent_to_client: bool = False
    submitted_at: Optional[datetime] = None
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
