"""
Document management Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid


class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    original_filename: str
    file_type: str  # pdf, image, etc.
    file_size: int = 0
    file_data: str = ""  # Base64 encoded file content
    # Relations
    related_id: Optional[str] = None  # form_id, proposal_id, contract_id, etc.
    related_type: Optional[str] = None  # form, proposal, contract
    # Metadata
    description: str = ""
    uploaded_by: str = ""
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DocumentCreate(BaseModel):
    filename: str
    file_type: str
    file_data: str  # Base64 encoded
    related_id: Optional[str] = None
    related_type: Optional[str] = None
    description: str = ""
