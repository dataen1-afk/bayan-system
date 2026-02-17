"""
Notification-related Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid


class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # form_submitted, proposal_sent, proposal_accepted, proposal_rejected, agreement_signed
    title: str
    message: str
    related_id: Optional[str] = None  # ID of related form/proposal/agreement
    related_type: Optional[str] = None  # form, proposal, agreement
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NotificationCreate(BaseModel):
    type: str
    title: str
    message: str
    related_id: Optional[str] = None
    related_type: Optional[str] = None
