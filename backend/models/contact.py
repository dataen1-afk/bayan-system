"""
Contact history/CRM Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid


class ContactRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    customer_name: str = ""
    # Contact details
    contact_type: str  # phone, email, meeting, other
    subject: str = ""
    notes: str = ""
    # Follow-up
    follow_up_date: Optional[str] = None
    follow_up_completed: bool = False
    # Metadata
    contacted_by: str = ""
    # Timestamps
    contact_date: str = ""  # YYYY-MM-DD
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ContactRecordCreate(BaseModel):
    customer_id: str
    customer_name: str = ""
    contact_type: str
    subject: str = ""
    notes: str = ""
    follow_up_date: Optional[str] = None
    contact_date: str = ""
