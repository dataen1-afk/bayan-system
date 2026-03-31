"""
Shared dependencies for modular routes (DB helpers, notifications, etc.).

JWT / HTTP Bearer: `security` and `get_current_user` are re-exported from `auth`
(the only module that calls jwt.encode / jwt.decode). Import from `auth` directly
in new code; re-exports remain for backward compatibility.
"""
from fastapi import Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from pathlib import Path
import os
import uuid
import qrcode
from io import BytesIO
import base64

# Load environment
from dotenv import load_dotenv
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from database import db
from auth import security, get_current_user

# Contracts directory
CONTRACTS_DIR = ROOT_DIR / "contracts"
CONTRACTS_DIR.mkdir(exist_ok=True)

# ================= USER ROLE CONSTANTS =================

class UserRole:
    ADMIN = "admin"
    CLIENT = "client"

# ================= SHARED PYDANTIC MODELS =================

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    title: str
    title_ar: str = ""  # Arabic title
    message: str
    message_ar: str = ""  # Arabic message
    related_id: Optional[str] = None
    related_type: Optional[str] = None
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Certificate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    certificate_number: str = ""
    contract_id: str
    audit_id: str = ""
    organization_name: str
    organization_name_ar: str = ""
    standards: List[str] = []
    scope: str = ""
    scope_ar: str = ""
    issue_date: str
    expiry_date: str
    status: str = "active"
    verification_url: str = ""
    qr_code_data: str = ""
    lead_auditor: str = ""
    audit_team: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

# ================= AUTHENTICATION DEPENDENCIES =================

async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin role for the current user"""
    if current_user.get("role") != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# ================= NOTIFICATION HELPER =================

async def create_notification(notification_type: str, title: str, message: str, related_id: str = None, related_type: str = None, title_ar: str = "", message_ar: str = ""):
    """Helper function to create a notification with bilingual support"""
    notification = Notification(
        type=notification_type,
        title=title,
        title_ar=title_ar,
        message=message,
        message_ar=message_ar,
        related_id=related_id,
        related_type=related_type
    )
    notification_doc = notification.model_dump()
    notification_doc['created_at'] = notification_doc['created_at'].isoformat()
    await db.notifications.insert_one(notification_doc)
    return notification

# ================= CERTIFICATE HELPERS =================

async def generate_certificate_number():
    """Generate unique certificate number: CERT-YYYY-XXXX"""
    year = datetime.now().year
    last_cert = await db.certificates.find_one(
        {"certificate_number": {"$regex": f"^CERT-{year}-"}},
        sort=[("certificate_number", -1)]
    )
    if last_cert:
        last_num = int(last_cert['certificate_number'].split('-')[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    return f"CERT-{year}-{new_num:04d}"

def get_qr_code_base64(data: str) -> str:
    """Generate QR code and return as base64"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()
