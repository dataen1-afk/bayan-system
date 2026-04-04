"""
Authentication routes (PostgreSQL).
"""
import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

logger = logging.getLogger(__name__)

DB_UNAVAILABLE_DETAIL = "Database temporarily unavailable. Please try again shortly."

from database import AsyncSessionLocal, UserRow
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


def _row_to_user_doc(row: UserRow) -> dict:
    return {
        "id": str(row.id),
        "name": row.name,
        "email": row.email,
        "password": row.password,
        "role": row.role,
        "created_at": row.created_at,
        "active": row.active,
    }


@router.post("/register", response_model=User)
async def register_user(user_data: UserRegister):
    """Register a new user"""
    email_norm = str(user_data.email).lower().strip()
    email_raw = str(user_data.email).strip()

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserRow).where(
                    or_(UserRow.email == email_norm, UserRow.email == email_raw)
                )
            )
            existing = result.scalar_one_or_none()
    except SQLAlchemyError as e:
        logger.warning("register: database error: %s", e)
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE_DETAIL)

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    if user_data.role not in [UserRole.ADMIN, UserRole.CLIENT]:
        raise HTTPException(status_code=400, detail="Invalid role")

    now = datetime.now(timezone.utc)
    uid = uuid.uuid4()
    row = UserRow(
        id=uid,
        name=user_data.name,
        email=email_norm,
        password=hash_password(user_data.password),
        role=user_data.role,
        active=True,
        created_at=now,
        updated_at=now,
    )

    try:
        async with AsyncSessionLocal() as session:
            session.add(row)
            await session.commit()
            await session.refresh(row)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered")
    except SQLAlchemyError as e:
        logger.warning("register: database error on insert: %s", e)
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE_DETAIL)

    return User(
        id=str(row.id),
        name=row.name,
        email=row.email,
        role=row.role,
        created_at=row.created_at,
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Authenticate user and return JWT token"""
    email_raw = str(credentials.email).strip()
    email_norm = email_raw.lower()

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserRow).where(
                    or_(UserRow.email == email_norm, UserRow.email == email_raw)
                )
            )
            row = result.scalar_one_or_none()
    except SQLAlchemyError as e:
        logger.warning("login: database error: %s", e)
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE_DETAIL)

    if not row:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not row.active:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(credentials.password, row.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_doc = _row_to_user_doc(row)

    try:
        uid = resolve_user_document_id(user_doc)
    except ValueError:
        logger.error("Login: user record missing id for email=%s", email_norm)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    role_raw = user_doc.get("role")
    role = str(role_raw).strip().lower() if role_raw is not None else UserRole.CLIENT

    token = create_jwt_token(uid, role)

    logger.debug(
        "Login OK email=%s role=%s",
        credentials.email,
        user_doc["role"],
    )

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

    try:
        async with AsyncSessionLocal() as session:
            row = None
            try:
                uid_uuid = uuid.UUID(str(uid_claim))
                result = await session.execute(select(UserRow).where(UserRow.id == uid_uuid))
                row = result.scalar_one_or_none()
            except (ValueError, TypeError):
                row = None
    except SQLAlchemyError as e:
        logger.warning("me: database error: %s", e)
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE_DETAIL)

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    user_doc = _row_to_user_doc(row)

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
