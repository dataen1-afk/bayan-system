"""
Authentication routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone

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
    
    # Create user
    user = User(
        name=user_data.name,
        email=user_data.email,
        role=user_data.role
    )
    
    # Store with hashed password
    user_dict = user.model_dump()
    user_dict["password_hash"] = hash_password(user_data.password)
    
    await db.users.insert_one(user_dict)
    
    return user


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Authenticate user and return JWT token"""
    user_doc = await db.users.find_one({"email": credentials.email})
    
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(credentials.password, user_doc.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    token = create_jwt_token(user_doc["id"], user_doc["role"])
    
    # Create user response (without password)
    user = User(
        id=user_doc["id"],
        name=user_doc["name"],
        email=user_doc["email"],
        role=user_doc["role"],
        created_at=user_doc.get("created_at", datetime.now(timezone.utc))
    )
    
    return TokenResponse(token=token, user=user)


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user info"""
    user_doc = await db.users.find_one({"id": current_user["user_id"]})
    
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(
        id=user_doc["id"],
        name=user_doc["name"],
        email=user_doc["email"],
        role=user_doc["role"],
        created_at=user_doc.get("created_at", datetime.now(timezone.utc))
    )
