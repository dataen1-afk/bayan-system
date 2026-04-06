"""
Authentication routes (PostgreSQL).
"""
import asyncio
import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

logger = logging.getLogger(__name__)

DB_UNAVAILABLE_DETAIL = "Database temporarily unavailable. Please try again shortly."

from database import AsyncSessionLocal, UserRow, describe_database_url_sanitized
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

_LOGIN_DB_MAX_ATTEMPTS = 3
_LOGIN_DB_RETRY_DELAY_SEC = 0.5
# Transient pool / network / Supabase pooler issues (not query semantics).
_LOGIN_DB_RETRYABLE_EXC = (OSError, TimeoutError, OperationalError)


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
        extra={},
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
    _login_log = logging.getLogger("bayan.login")
    email_raw = str(credentials.email).strip()
    email_norm = email_raw.lower()
    _login_log.info("login: entered email=%s", email_norm)

    try:
        _login_log.info(
            "login: acquiring AsyncSessionLocal (same engine/pool as db_startup.connect_db)"
        )
        row = None
        last_retryable_exc: BaseException | None = None
        last_failure_phase = "session_acquire"
        for attempt in range(1, _LOGIN_DB_MAX_ATTEMPTS + 1):
            _session_opened = False
            try:
                async with AsyncSessionLocal() as session:
                    _session_opened = True
                    _login_log.info(
                        "login: AsyncSessionLocal acquired successfully (attempt %s/%s)",
                        attempt,
                        _LOGIN_DB_MAX_ATTEMPTS,
                    )
                    result = await session.execute(
                        select(UserRow).where(
                            or_(UserRow.email == email_norm, UserRow.email == email_raw)
                        )
                    )
                    row = result.scalar_one_or_none()
                last_retryable_exc = None
                break
            except _LOGIN_DB_RETRYABLE_EXC as e:
                last_retryable_exc = e
                phase = "query_or_orm" if _session_opened else "session_acquire"
                last_failure_phase = phase
                _login_log.warning(
                    "login: connection-layer failure attempt %s/%s phase=%s exc_type=%s exc_msg=%s | %s",
                    attempt,
                    _LOGIN_DB_MAX_ATTEMPTS,
                    phase,
                    type(e).__name__,
                    str(e),
                    describe_database_url_sanitized(),
                )
                if attempt < _LOGIN_DB_MAX_ATTEMPTS:
                    _login_log.info(
                        "login: retrying DB fetch in %.1fs (next attempt %s)",
                        _LOGIN_DB_RETRY_DELAY_SEC,
                        attempt + 1,
                    )
                    await asyncio.sleep(_LOGIN_DB_RETRY_DELAY_SEC)
            except SQLAlchemyError as e:
                phase = "query_or_orm" if _session_opened else "session_acquire"
                _login_log.error(
                    "bayan.login: OUTCOME=DB_FAILURE | async_session_opened=%s | failure_phase=%s | "
                    "exc_type=%s | exc_msg=%s | errno=n/a | winerror=n/a | %s",
                    _session_opened,
                    phase,
                    type(e).__name__,
                    str(e),
                    describe_database_url_sanitized(),
                )
                _login_log.exception("bayan.login: traceback email=%s", email_norm)
                raise HTTPException(status_code=503, detail=DB_UNAVAILABLE_DETAIL)

        if last_retryable_exc is not None:
            e = last_retryable_exc
            _login_log.error(
                "bayan.login: OUTCOME=DB_FAILURE after %s attempts | failure_phase=%s | "
                "exc_type=%s | exc_msg=%s | %s",
                _LOGIN_DB_MAX_ATTEMPTS,
                last_failure_phase,
                type(e).__name__,
                str(e),
                describe_database_url_sanitized(),
            )
            _login_log.exception(
                "bayan.login: exhausted retries email=%s",
                email_norm,
            )
            raise HTTPException(status_code=503, detail=DB_UNAVAILABLE_DETAIL)

        _login_log.info(
            "bayan.login: OUTCOME=DB_QUERY_OK | async_session_opened=true | failure_phase=n/a | "
            "exc_type=n/a | exc_msg=n/a | errno=n/a | winerror=n/a | %s",
            describe_database_url_sanitized(),
        )

        if not row:
            _login_log.info("login: user not found email=%s", email_norm)
            raise HTTPException(status_code=401, detail="Invalid email or password")

        _login_log.info("login: user found id=%s", row.id)

        if not row.active:
            _login_log.info("login: user inactive id=%s", row.id)
            raise HTTPException(status_code=401, detail="Invalid email or password")

        pwd_ok = verify_password(credentials.password, row.password)
        _login_log.info("login: password verification finished success=%s", pwd_ok)
        if not pwd_ok:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        user_doc = _row_to_user_doc(row)

        try:
            uid = resolve_user_document_id(user_doc)
        except ValueError:
            _login_log.exception(
                "login: user record missing resolvable id email=%s",
                email_norm,
            )
            raise HTTPException(status_code=401, detail="Invalid email or password")

        role_raw = user_doc.get("role")
        role = str(role_raw).strip().lower() if role_raw is not None else UserRole.CLIENT

        _login_log.info("login: creating token")
        token = create_jwt_token(uid, role)
        _login_log.info("login: token created successfully")

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
    except HTTPException:
        raise
    except Exception:
        _login_log.exception("login: unexpected failure email=%s", email_norm)
        raise HTTPException(
            status_code=500,
            detail="Authentication service error (AUTH_500)",
        )


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
