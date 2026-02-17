"""
Site management Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid


class Site(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    name_ar: str = ""
    address: str = ""
    city: str = ""
    country: str = ""
    contact_name: str = ""
    contact_phone: str = ""
    contact_email: str = ""
    # Links
    organization_id: Optional[str] = None
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SiteCreate(BaseModel):
    name: str
    name_ar: str = ""
    address: str = ""
    city: str = ""
    country: str = ""
    contact_name: str = ""
    contact_phone: str = ""
    contact_email: str = ""
    organization_id: Optional[str] = None
