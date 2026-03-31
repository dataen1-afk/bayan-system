"""
Authentication routes.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

from database import db
from auth import (
    hash_password,
    verify_password,
    create_jwt_token,
    get_current_user,
    UserRole,
    resolve_user_document_id,
)
from models.user import UserRegister, UserLogin, User, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=User)
async def register_user(user_data: UserRegister):
    """Register a new user"""
    email_norm = str(user_data.email).lower().strip()
    existing_user = await db.users.find_one({"email": email_norm})
    if not existing_user:
        existing_user = await db.users.find_one({"email": str(user_data.email).strip()})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate role
    if user_data.role not in [UserRole.ADMIN, UserRole.CLIENT]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    user = User(
        name=user_data.name,
        email=email_norm,
        role=user_data.role,
    )

    user_dict = user.model_dump()
    user_dict["email"] = email_norm
    user_dict["password"] = hash_password(user_data.password)
    user_dict["created_at"] = user_dict["created_at"].isoformat()

    await db.users.insert_one(user_dict)
    
    return user


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Authenticate user and return JWT token"""
    email_raw = str(credentials.email).strip()
    email_norm = email_raw.lower()
    user_doc = await db.users.find_one({"email": email_norm})
    if not user_doc and email_raw != email_norm:
        user_doc = await db.users.find_one({"email": email_raw})

    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(credentials.password, user_doc.get("password", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    try:
        uid = resolve_user_document_id(user_doc)
    except ValueError:
        logger.error("Login: user record missing id/_id for email=%s", email_norm)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    role_raw = user_doc.get("role")
    role = str(role_raw).strip().lower() if role_raw is not None else UserRole.CLIENT

    # Create token
    token = create_jwt_token(uid, role)
    logger.debug(
        "Login OK email=%s role=%s",
        credentials.email,
        user_doc["role"],
    )

    # Create user response (without password)
    created_at = user_doc.get("created_at")
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)
    elif created_at is None:
        created_at = datetime.now(timezone.utc)
    
    user = User(
        id=uid,
        name=user_doc.get("name") or "",
        email=str(user_doc.get("email", email_norm)),
        role=role,
        created_at=created_at,
    )
    
    return TokenResponse(token=token, user=user)


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user info"""
    uid_claim = current_user["user_id"]
    user_doc = await db.users.find_one({"id": uid_claim})
    if not user_doc:
        try:
            from bson import ObjectId

            if isinstance(uid_claim, str) and len(uid_claim) == 24:
                user_doc = await db.users.find_one({"_id": ObjectId(uid_claim)})
        except Exception:
            user_doc = None

    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    created_at = user_doc.get("created_at")
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)
    elif created_at is None:
        created_at = datetime.now(timezone.utc)
    
    try:
        uid = resolve_user_document_id(user_doc)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")

    role_raw = user_doc.get("role")
    role = str(role_raw).strip().lower() if role_raw is not None else UserRole.CLIENT

    return User(
        id=uid,
        name=user_doc.get("name") or "",
        email=str(user_doc.get("email", "")),
        role=role,
        created_at=created_at,
    )
