"""
Public certificate verification route.
"""
from fastapi import APIRouter, HTTPException

from database import db

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/verify/{certificate_number}")
async def verify_certificate(certificate_number: str):
    """Public endpoint to verify a certificate by its number"""
    cert = await db.certificates.find_one(
        {"certificate_number": certificate_number},
        {"_id": 0, "qr_code_data": 0}  # Exclude large QR data
    )
    
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    return {
        "valid": cert.get("status") == "active",
        "certificate_number": cert.get("certificate_number"),
        "organization_name": cert.get("organization_name"),
        "standards": cert.get("standards", []),
        "scope": cert.get("scope", ""),
        "issue_date": cert.get("issue_date"),
        "expiry_date": cert.get("expiry_date"),
        "status": cert.get("status")
    }
