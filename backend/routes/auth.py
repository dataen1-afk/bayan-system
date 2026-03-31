"""
Authentication routes.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

from database import db
from auth import (
    hash_password, verify_password, create_jwt_token,
    get_current_user, UserRole
)
from models.user import UserRegister, UserLogin, User, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=User)
async def register_user(user_data: UserRegister):
    """Register a new user"""
    # Check if email already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate role
    if user_data.role not in [UserRole.ADMIN, UserRole.CLIENT]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # Create user
    user = User(
        name=user_data.name,
        email=user_data.email,
        role=user_data.role
    )
    
    # Store with hashed password (using 'password' field to match existing schema)
    user_dict = user.model_dump()
    user_dict["password"] = hash_password(user_data.password)
    user_dict["created_at"] = user_dict["created_at"].isoformat()
    
    await db.users.insert_one(user_dict)
    
    return user


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Authenticate user and return JWT token"""
    user_doc = await db.users.find_one({"email": credentials.email})
    
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(credentials.password, user_doc.get("password", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create token
    token = create_jwt_token(user_doc["id"], user_doc["role"])
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
        id=user_doc["id"],
        name=user_doc["name"],
        email=user_doc["email"],
        role=user_doc["role"],
        created_at=created_at
    )
    
    return TokenResponse(token=token, user=user)


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user info"""
    user_doc = await db.users.find_one({"id": current_user["user_id"]})
    
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    created_at = user_doc.get("created_at")
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)
    elif created_at is None:
        created_at = datetime.now(timezone.utc)
    
    return User(
        id=user_doc["id"],
        name=user_doc["name"],
        email=user_doc["email"],
        role=user_doc["role"],
        created_at=created_at
    )
