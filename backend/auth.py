"""
Authentication utilities - JWT, password hashing, and user verification.
"""
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
import jwt
import os

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Security
security = HTTPBearer()


class UserRole:
    SYSTEM_ADMIN = "system_admin"
    ADMIN = "admin"
    CEO = "ceo"
    GENERAL_MANAGER = "general_manager"
    QUALITY_MANAGER = "quality_manager"
    CERTIFICATION_MANAGER = "certification_manager"
    OPERATION_COORDINATOR = "operation_coordinator"
    MARKETING_MANAGER = "marketing_manager"
    FINANCIAL_MANAGER = "financial_manager"
    HR_MANAGER = "hr_manager"
    LEAD_AUDITOR = "lead_auditor"
    AUDITOR = "auditor"
    TECHNICAL_EXPERT = "technical_expert"
    CLIENT = "client"


# Staff roles that can access admin features
STAFF_ROLES = [
    UserRole.SYSTEM_ADMIN, UserRole.ADMIN, UserRole.CEO, UserRole.GENERAL_MANAGER,
    UserRole.QUALITY_MANAGER, UserRole.CERTIFICATION_MANAGER, UserRole.OPERATION_COORDINATOR,
    UserRole.MARKETING_MANAGER, UserRole.FINANCIAL_MANAGER, UserRole.HR_MANAGER,
    UserRole.LEAD_AUDITOR, UserRole.AUDITOR, UserRole.TECHNICAL_EXPERT
]

# Management roles with full access
MANAGEMENT_ROLES = [UserRole.SYSTEM_ADMIN, UserRole.CEO, UserRole.GENERAL_MANAGER, UserRole.ADMIN]


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt_token(user_id: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    payload = decode_jwt_token(token)
    return payload


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require staff-level access (any internal role)"""
    user_role = current_user.get("role")
    
    # Allow all staff roles
    if user_role in STAFF_ROLES:
        return current_user
    
    raise HTTPException(status_code=403, detail="Staff access required")


async def require_management(current_user: dict = Depends(get_current_user)) -> dict:
    """Require management-level access"""
    if current_user.get("role") not in MANAGEMENT_ROLES:
        raise HTTPException(status_code=403, detail="Management access required")
    return current_user
