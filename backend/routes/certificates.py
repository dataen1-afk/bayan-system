"""
Certificate management routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import os

import app_documents_pg as doc_pg
from auth import require_admin
from models.certificate import Certificate, CertificateCreate
from certificate_generator import generate_certificate_pdf, get_qr_code_base64

router = APIRouter(prefix="/certificates", tags=["Certificates"])


async def generate_certificate_number():
    """Generate unique certificate number: CERT_YYYY_XXXX (underscore form for this router)."""
    year = datetime.now().year
    pattern = f"CERT\\_{year}\\_%"
    last_cert = await doc_pg.get_latest_by_certificate_number_like(
        doc_pg.C_CERTIFICATES, pattern, escape_underscore=True
    )
    if last_cert:
        last_num = int(last_cert["certificate_number"].split("_")[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    return f"CERT_{year}_{new_num:04d}"


@router.get("", response_model=List[dict])
async def get_certificates(
    status: Optional[str] = None,
    standard: Optional[str] = None,
    current_user: dict = Depends(require_admin)
):
    """Get all certificates with optional filtering"""
    certificates = await doc_pg.list_ordered(doc_pg.C_CERTIFICATES, 1000)
    if status:
        certificates = [c for c in certificates if c.get("status") == status]
    if standard:
        certificates = [c for c in certificates if standard in c.get("standards", [])]
    return certificates


@router.get("/stats")
async def get_certificate_stats(current_user: dict = Depends(require_admin)):
    """Get certificate statistics"""
    all_certs = await doc_pg.list_ordered(doc_pg.C_CERTIFICATES, 1000)
    
    total = len(all_certs)
    active = len([c for c in all_certs if c.get("status") == "active"])
    suspended = len([c for c in all_certs if c.get("status") == "suspended"])
    withdrawn = len([c for c in all_certs if c.get("status") == "withdrawn"])
    expired = len([c for c in all_certs if c.get("status") == "expired"])
    
    # Count by standard
    standards_count = {}
    for cert in all_certs:
        for std in cert.get("standards", []):
            standards_count[std] = standards_count.get(std, 0) + 1
    
    return {
        "total": total,
        "active": active,
        "suspended": suspended,
        "withdrawn": withdrawn,
        "expired": expired,
        "by_standard": standards_count
    }


@router.post("", response_model=dict)
async def create_certificate(
    cert_data: CertificateCreate,
    current_user: dict = Depends(require_admin)
):
    """Create a new certificate"""
    # Get agreement info
    agreement = await doc_pg.get_by_doc_id(
        doc_pg.C_CERTIFICATION_AGREEMENTS, cert_data.contract_id
    )
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    # Generate certificate number
    cert_number = await generate_certificate_number()
    
    # Calculate dates
    issue_date = datetime.now().strftime("%Y-%m-%d")
    expiry_date = (datetime.now() + timedelta(days=3*365)).strftime("%Y-%m-%d")
    
    # Generate verification URL
    base_url = os.environ.get("REACT_APP_BACKEND_URL", "")
    verification_url = f"{base_url}/api/public/verify/{cert_number}"
    
    # Generate QR code
    qr_code_data = get_qr_code_base64(verification_url)
    
    certificate = Certificate(
        certificate_number=cert_number,
        contract_id=cert_data.contract_id,
        audit_id=cert_data.audit_id,
        organization_name=agreement.get("organization_name", ""),
        standards=cert_data.standards or agreement.get("selected_standards", []),
        scope=cert_data.scope or agreement.get("scope_of_services", ""),
        scope_ar=cert_data.scope_ar,
        issue_date=issue_date,
        expiry_date=expiry_date,
        verification_url=verification_url,
        qr_code_data=qr_code_data,
        lead_auditor=cert_data.lead_auditor,
        audit_team=cert_data.audit_team
    )
    
    cert_doc = certificate.model_dump()
    cert_doc["created_at"] = cert_doc["created_at"].isoformat()
    if cert_doc.get("updated_at") is not None:
        u = cert_doc["updated_at"]
        cert_doc["updated_at"] = u.isoformat() if isinstance(u, datetime) else u
    await doc_pg.insert_document(doc_pg.C_CERTIFICATES, cert_doc)
    return certificate.model_dump()


@router.get("/{certificate_id}", response_model=dict)
async def get_certificate(
    certificate_id: str,
    current_user: dict = Depends(require_admin)
):
    """Get a specific certificate"""
    cert = await doc_pg.get_by_doc_id(doc_pg.C_CERTIFICATES, certificate_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return cert


@router.put("/{certificate_id}/status")
async def update_certificate_status(
    certificate_id: str,
    status: str,
    current_user: dict = Depends(require_admin)
):
    """Update certificate status"""
    valid_statuses = ["active", "suspended", "withdrawn", "expired"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    ok = await doc_pg.merge_set_by_doc_id(
        doc_pg.C_CERTIFICATES,
        certificate_id,
        {"status": status, "updated_at": datetime.now(timezone.utc)},
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    return {"status": "success"}


@router.get("/{certificate_id}/pdf")
async def download_certificate_pdf(
    certificate_id: str,
    current_user: dict = Depends(require_admin)
):
    """Generate and download certificate PDF"""
    cert = await doc_pg.get_by_doc_id(doc_pg.C_CERTIFICATES, certificate_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    pdf_bytes = generate_certificate_pdf(cert)
    safe_name = str(cert.get("certificate_number", "cert")).replace("/", "_")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="certificate_{safe_name}.pdf"'
        },
    )
