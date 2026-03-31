"""
Single source of truth for JWT (encode/decode), HTTPBearer security, and password hashing.

JWT secret resolution (local Bayan default):
- backend/.env is authoritative when it contains a non-empty JWT_SECRET.
- Process JWT_SECRET is then ignored for signing (logged clearly), so IDE/shell stubs cannot
  fight the repo .env file.
- Set BAYAN_JWT_PREFER_PROCESS_ENV=1 to prefer a non-empty process JWT_SECRET (e.g. Docker/K8s).
- One pinned secret per process for identical encode/decode.
- Per-request JWT trace logs are at DEBUG (enable with ``LOG_LEVEL=DEBUG`` or ``logging.getLogger("auth").setLevel(logging.DEBUG)``).
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

import jwt
from dotenv import dotenv_values
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

_BACKEND_DIR = Path(__file__).resolve().parent
_ENV_FILE = _BACKEND_DIR / ".env"

# One shared HTTPBearer for the whole app (OpenAPI + Depends).
security = HTTPBearer()

_backend_env_bootstrapped = False
# Single resolved secret for this process — computed lazily, identical for encode and decode.
_jwt_secret_resolved: str | None = None
_jwt_secret_source: str | None = None
_jwt_resolution_meta: str = ""


def _normalize_secret(raw: str | None) -> str:
    if raw is None:
        return ""
    return str(raw).strip().strip('"').strip("'")


def _ensure_backend_dotenv_loaded() -> None:
    """Merge backend/.env into os.environ for keys that are unset (override=False)."""
    global _backend_env_bootstrapped
    if _backend_env_bootstrapped:
        return
    try:
        from dotenv import load_dotenv

        if _ENV_FILE.is_file():
            load_dotenv(_ENV_FILE, override=False)
    finally:
        _backend_env_bootstrapped = True


def _prefer_process_jwt_secret() -> bool:
    v = os.environ.get("BAYAN_JWT_PREFER_PROCESS_ENV", "")
    return str(v).strip().lower() in ("1", "true", "yes", "on")


def _resolve_jwt_secret_once() -> tuple[str, str]:
    """
    Pick exactly one secret for the lifetime of this process.

    Default (local): backend/.env wins if JWT_SECRET is set there.
    Opt-in: BAYAN_JWT_PREFER_PROCESS_ENV=1 makes a non-empty process JWT_SECRET win.
    """
    global _jwt_resolution_meta
    _ensure_backend_dotenv_loaded()

    env_path_resolved = str(_ENV_FILE.resolve())
    env_raw = os.environ.get("JWT_SECRET")
    env_present = "JWT_SECRET" in os.environ
    env_val = _normalize_secret(env_raw) if env_raw is not None else ""

    file_val = ""
    if _ENV_FILE.is_file():
        vals = dotenv_values(_ENV_FILE)
        file_val = _normalize_secret(vals.get("JWT_SECRET"))

    prefer_proc = _prefer_process_jwt_secret()

    if prefer_proc:
        if env_val:
            _jwt_resolution_meta = (
                f"BAYAN_JWT_PREFER_PROCESS_ENV=1 | env_file={env_path_resolved} | "
                f"process_JWT_SECRET=used len={len(env_val)}"
            )
            if file_val and file_val != env_val:
                logger.warning(
                    "JWT_SECRET: using process environment (BAYAN_JWT_PREFER_PROCESS_ENV=1); "
                    "backend/.env contains a different JWT_SECRET - .env value IGNORED for JWT."
                )
            return env_val, "process_environment (BAYAN_JWT_PREFER_PROCESS_ENV=1)"
        if file_val:
            _jwt_resolution_meta = (
                f"BAYAN_JWT_PREFER_PROCESS_ENV=1 but process JWT_SECRET empty | "
                f"fell_back_to_backend/.env | env_file={env_path_resolved}"
            )
            logger.warning(
                "JWT_SECRET: BAYAN_JWT_PREFER_PROCESS_ENV=1 but process JWT_SECRET empty/missing; "
                "using backend/.env (%s)",
                env_path_resolved,
            )
            return file_val, f"backend/.env ({_ENV_FILE})"
        _jwt_resolution_meta = "no JWT_SECRET in process or .env"
        raise RuntimeError(
            "JWT_SECRET missing. With BAYAN_JWT_PREFER_PROCESS_ENV=1, set a non-empty JWT_SECRET "
            "in the process environment, or remove the flag and set JWT_SECRET in backend/.env."
        )

    # Local default: backend/.env is authoritative
    if file_val:
        if env_present and not env_val:
            _jwt_resolution_meta = (
                f"backend/.env authoritative | env_file={env_path_resolved} | "
                "process had JWT_SECRET key but value empty/whitespace - IGNORED"
            )
            logger.warning(
                "JWT_SECRET: pinned from backend/.env (%s); process had JWT_SECRET but it was "
                "empty/whitespace (ignored).",
                env_path_resolved,
            )
        elif env_val and env_val != file_val:
            _jwt_resolution_meta = (
                f"backend/.env authoritative | env_file={env_path_resolved} | "
                f"process_JWT_SECRET=IGNORED (had different value, len={len(env_val)})"
            )
            logger.warning(
                "JWT_SECRET: pinned from backend/.env (%s); process environment had a different "
                "JWT_SECRET (len=%d) - IGNORED for Bayan. Set BAYAN_JWT_PREFER_PROCESS_ENV=1 to use process env.",
                env_path_resolved,
                len(env_val),
            )
        elif env_val:
            _jwt_resolution_meta = (
                f"backend/.env authoritative | env_file={env_path_resolved} | "
                f"process_JWT_SECRET present and identical to file (len={len(env_val)}) - file used"
            )
            logger.debug(
                "JWT_SECRET: backend/.env (%s); process matches file (len=%d).",
                env_path_resolved,
                len(env_val),
            )
        else:
            _jwt_resolution_meta = (
                f"backend/.env authoritative | env_file={env_path_resolved} | "
                "process_JWT_SECRET absent"
            )
            logger.debug(
                "JWT_SECRET: using backend/.env (%s); process JWT_SECRET unset.",
                env_path_resolved,
            )
        return file_val, f"backend/.env ({_ENV_FILE})"

    if env_val:
        _jwt_resolution_meta = (
            f"no JWT_SECRET in backend/.env file | env_file={env_path_resolved} | "
            f"fell_back_to_process len={len(env_val)}"
        )
        logger.warning(
            "JWT_SECRET: backend/.env has no JWT_SECRET; using process environment (len=%d). "
            "Add JWT_SECRET to backend/.env for local authoritative config.",
            len(env_val),
        )
        return env_val, "process_environment (fallback: missing JWT_SECRET in backend/.env)"

    _jwt_resolution_meta = "no JWT_SECRET anywhere"
    raise RuntimeError(
        "JWT_SECRET is missing. Add JWT_SECRET to backend/.env (recommended), or set "
        "BAYAN_JWT_PREFER_PROCESS_ENV=1 with a non-empty process JWT_SECRET."
    )


def get_jwt_secret() -> str:
    global _jwt_secret_resolved, _jwt_secret_source
    if _jwt_secret_resolved is not None:
        return _jwt_secret_resolved
    secret, src = _resolve_jwt_secret_once()
    _jwt_secret_resolved = secret
    _jwt_secret_source = src
    logger.info(
        "JWT secret ready: source=%s len=%d (encode/decode use same secret)",
        src,
        len(secret),
    )
    logger.debug("JWT resolution detail: %s", _jwt_resolution_meta)
    return secret


def jwt_secret_source() -> str:
    """After first get_jwt_secret(), where the secret came from."""
    get_jwt_secret()
    assert _jwt_secret_source is not None
    return _jwt_secret_source


def jwt_secret_fingerprint(secret: str) -> str:
    """len + first 6 hex chars of SHA-256 (no secret leakage)."""
    digest = hashlib.sha256(secret.encode("utf-8")).hexdigest()
    return f"len={len(secret)} sha256_6={digest[:6]} full_sha256_16={digest[:16]}"


def normalize_bearer_token(raw: str | None) -> str:
    """Strip whitespace and accidental nested 'Bearer ' prefixes (Swagger / copy-paste)."""
    if not raw:
        return ""
    t = raw.strip()
    while t.lower().startswith("bearer "):
        t = t[7:].strip()
    return t


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


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Return False for missing/invalid hashes instead of raising (passlib can raise
    UnknownHashError on empty or non-bcrypt strings — that surfaced as HTTP 500 on /login).
    """
    if hashed_password is None or not str(hashed_password).strip():
        return False
    try:
        return bool(pwd_context.verify(plain_password, str(hashed_password)))
    except Exception as e:
        logger.warning("Password verify failed (unusable hash): %s", type(e).__name__)
        return False


def resolve_user_document_id(user_doc: dict) -> str:
    """
    Bayan stores a string ``id`` field. Legacy or imported users may only have MongoDB ``_id``.
    """
    uid = user_doc.get("id")
    if uid is not None and str(uid).strip() != "":
        return str(uid)
    oid = user_doc.get("_id")
    if oid is not None:
        return str(oid)
    raise ValueError("user document has no id or _id")


def create_jwt_token(user_id: str, role: str) -> str:
    secret = get_jwt_secret()
    fp = jwt_secret_fingerprint(secret)
    exp = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "user_id": user_id,
        "sub": user_id,
        "role": role,
        "exp": exp,
    }
    logger.debug(
        "JWT encode: algorithm=%s payload_keys=%s secret_source=%s fingerprint=%s",
        JWT_ALGORITHM,
        list(payload.keys()),
        jwt_secret_source(),
        fp,
    )
    logger.debug(
        "JWT encode payload (no exp repr): %s",
        {k: v for k, v in payload.items() if k != "exp"},
    )
    encoded = jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)
    if isinstance(encoded, bytes):
        encoded = encoded.decode("utf-8")
    return encoded


def decode_jwt_token(token: str) -> dict:
    normalized = normalize_bearer_token(token)
    if not normalized:
        logger.error("JWT decode: empty token after normalize; raw_repr=%r", token[:120] if token else "")
        raise HTTPException(status_code=401, detail="Invalid token")

    secret = get_jwt_secret()
    fp = jwt_secret_fingerprint(secret)
    logger.debug(
        "JWT decode attempt: algorithm=%s token_len=%d token_prefix=%r fingerprint=%s secret_source=%s",
        JWT_ALGORITHM,
        len(normalized),
        normalized[:40] + ("…" if len(normalized) > 40 else ""),
        fp,
        jwt_secret_source(),
    )

    try:
        payload = jwt.decode(normalized, secret, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as e:
        logger.error(
            "JWT decode FAILED ExpiredSignatureError: algorithm=%s fingerprint=%s full_message=%r",
            JWT_ALGORITHM,
            fp,
            str(e),
        )
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        logger.error(
            "JWT decode FAILED %s: algorithm=%s fingerprint=%s full_message=%r args=%r",
            type(e).__name__,
            JWT_ALGORITHM,
            fp,
            str(e),
            getattr(e, "args", None),
        )
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.exception(
            "JWT decode FAILED unexpected %s: algorithm=%s fingerprint=%s full_message=%r",
            type(e).__name__,
            JWT_ALGORITHM,
            fp,
            str(e),
        )
        raise HTTPException(status_code=401, detail="Invalid token")

    # JWT returns exp as int; safe to log
    try:
        payload_log = json.dumps(payload, default=str)
    except Exception:
        payload_log = repr(payload)
    logger.debug(
        "JWT decode OK: algorithm=%s fingerprint=%s secret_source=%s payload=%s",
        JWT_ALGORITHM,
        fp,
        jwt_secret_source(),
        payload_log,
    )
    return payload


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    raw = credentials.credentials or ""
    secret = get_jwt_secret()
    logger.debug(
        "JWT HTTPBearer: scheme=%r credentials_len=%d credentials_prefix=%r fingerprint=%s",
        getattr(credentials, "scheme", None),
        len(raw),
        (raw[:36] + "…") if len(raw) > 36 else raw,
        jwt_secret_fingerprint(secret),
    )
    if raw.strip().lower().startswith("bearer "):
        logger.warning("HTTPBearer credentials still contained 'Bearer '; normalizing in decode")
    return decode_jwt_token(raw)


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Modular routes: legacy admin role only (see server.require_admin for monolith rules)."""
    if current_user.get("role") != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
