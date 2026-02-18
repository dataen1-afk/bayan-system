"""
Shared dependencies for modular routes.
Contains database connection, authentication helpers, and common utilities.
"""
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from pathlib import Path
import jwt
import os
import uuid
import qrcode
from io import BytesIO
import base64

# Load environment
from dotenv import load_dotenv
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
security = HTTPBearer()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

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
    message: str
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

# ================= JWT HELPER FUNCTIONS =================

def decode_jwt_token(token: str) -> dict:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ================= AUTHENTICATION DEPENDENCIES =================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get the current authenticated user from JWT token"""
    token = credentials.credentials
    payload = decode_jwt_token(token)
    return payload

async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin role for the current user"""
    if current_user.get("role") != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# ================= NOTIFICATION HELPER =================

async def create_notification(notification_type: str, title: str, message: str, related_id: str = None, related_type: str = None):
    """Helper function to create a notification"""
    notification = Notification(
        type=notification_type,
        title=title,
        message=message,
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
