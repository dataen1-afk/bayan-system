"""
Database configuration and connection management.

Local default: ``backend/.env`` is authoritative for ``DB_NAME`` when the file sets it (same idea as JWT).
Process ``DB_NAME`` is then ignored unless ``BAYAN_DB_PREFER_PROCESS_ENV=1`` (Docker/K8s).
If neither file nor process sets a name, default is ``bayan_system``.
"""
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
from dotenv import load_dotenv, dotenv_values

ROOT_DIR = Path(__file__).parent
_ENV_PATH = ROOT_DIR / ".env"
load_dotenv(_ENV_PATH)


def _prefer_process_db_name() -> bool:
    v = os.environ.get("BAYAN_DB_PREFER_PROCESS_ENV", "")
    return str(v).strip().lower() in ("1", "true", "yes", "on")


def _normalize_db_name(raw: str | None) -> str:
    if raw is None:
        return ""
    s = str(raw).strip().strip('"').strip("'")
    return s


def _coerce_bayan_db(name: str, source_hint: str) -> tuple[str, str]:
    if name == "test_database":
        return (
            "bayan_system",
            f"override ({source_hint}: test_database invalid for Bayan; using bayan_system)",
        )
    return name, source_hint


def _resolve_db_name() -> tuple[str, str]:
    file_val = ""
    if _ENV_PATH.is_file():
        file_val = _normalize_db_name(dotenv_values(_ENV_PATH).get("DB_NAME"))

    proc_raw = os.environ.get("DB_NAME")
    proc_val = _normalize_db_name(proc_raw) if proc_raw is not None else ""

    if _prefer_process_db_name():
        if proc_val:
            return _coerce_bayan_db(proc_val, "process DB_NAME")
        if file_val:
            return _coerce_bayan_db(file_val, "backend/.env DB_NAME")
        return "bayan_system", "fallback (no DB_NAME; using bayan_system) [BAYAN_DB_PREFER_PROCESS_ENV=1]"

    if file_val:
        hint_base = f"backend/.env (DB_NAME={file_val})"
        if proc_val and proc_val != file_val:
            return _coerce_bayan_db(
                file_val,
                f"{hint_base}; process DB_NAME={proc_val} IGNORED "
                "(set BAYAN_DB_PREFER_PROCESS_ENV=1 to use process)",
            )
        if proc_val:
            return _coerce_bayan_db(file_val, f"{hint_base}; matches process")
        return _coerce_bayan_db(file_val, hint_base)

    if proc_val:
        return _coerce_bayan_db(
            proc_val,
            f"process env only (DB_NAME={proc_val}); no DB_NAME in backend/.env",
        )

    return "bayan_system", "fallback (DB_NAME unset; using bayan_system)"


# MongoDB connection (same cluster URI as env; DB_NAME selects Bayan database only)
mongo_url = os.environ["MONGO_URL"]
_server_sel_ms = int(os.environ.get("MONGO_SERVER_SELECTION_TIMEOUT_MS", "30000"))
client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=_server_sel_ms)
DB_NAME, DB_NAME_SOURCE = _resolve_db_name()
db = client[DB_NAME]
ENV_FILE_USED = _ENV_PATH.resolve()

# Ensure contracts directory exists
CONTRACTS_DIR = ROOT_DIR / "contracts"
CONTRACTS_DIR.mkdir(exist_ok=True)

# Certificates directory
CERTIFICATES_DIR = ROOT_DIR / "certificates"
CERTIFICATES_DIR.mkdir(exist_ok=True)
