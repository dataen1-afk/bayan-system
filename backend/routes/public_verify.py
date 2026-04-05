"""
Public certificate verification route.
"""
from fastapi import APIRouter, HTTPException

import app_documents_pg as doc_pg

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/verify/{certificate_number}")
async def verify_certificate(certificate_number: str):
    """Public endpoint to verify a certificate by its number"""
    cert = await doc_pg.get_by_payload_field(
        doc_pg.C_CERTIFICATES, "certificate_number", certificate_number
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
