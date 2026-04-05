"""
Template routes (Certification Packages and Proposal Templates).
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List

import app_documents_pg as doc_pg
from auth import require_admin
from models.template import CertificationPackage, ProposalTemplate

router = APIRouter(prefix="/templates", tags=["Templates"])


# ================= CERTIFICATION PACKAGES =================

@router.get("/packages", response_model=List[dict])
async def get_certification_packages(current_user: dict = Depends(require_admin)):
    """Get all certification packages"""
    return await doc_pg.list_ordered(doc_pg.C_CERTIFICATION_PACKAGES, 100)


@router.post("/packages", response_model=dict)
async def create_certification_package(
    package: CertificationPackage,
    current_user: dict = Depends(require_admin)
):
    """Create a new certification package"""
    doc = package.model_dump()
    doc.setdefault("is_active", True)
    doc["created_at"] = doc["created_at"].isoformat()
    await doc_pg.insert_document(doc_pg.C_CERTIFICATION_PACKAGES, doc)
    out = package.model_dump()
    out.setdefault("is_active", True)
    return out


@router.put("/packages/{package_id}", response_model=dict)
async def update_certification_package(
    package_id: str,
    package: CertificationPackage,
    current_user: dict = Depends(require_admin)
):
    """Update a certification package"""
    update_data = package.model_dump()
    update_data.setdefault("is_active", True)
    update_data["id"] = package_id  # Preserve ID
    update_data["created_at"] = (
        update_data["created_at"].isoformat()
        if hasattr(update_data["created_at"], "isoformat")
        else update_data["created_at"]
    )

    cur = await doc_pg.get_by_doc_id(doc_pg.C_CERTIFICATION_PACKAGES, package_id)
    if not cur:
        raise HTTPException(status_code=404, detail="Package not found")

    ok = await doc_pg.merge_set_by_doc_id(
        doc_pg.C_CERTIFICATION_PACKAGES, package_id, update_data
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Package not found")

    return update_data


@router.delete("/packages/{package_id}")
async def delete_certification_package(
    package_id: str,
    current_user: dict = Depends(require_admin)
):
    """Delete a certification package"""
    deleted = await doc_pg.delete_by_doc_id(
        doc_pg.C_CERTIFICATION_PACKAGES, package_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Package not found")
    return {"status": "success"}


# ================= PROPOSAL TEMPLATES =================

@router.get("/proposals", response_model=List[dict])
async def get_proposal_templates(current_user: dict = Depends(require_admin)):
    """Get all proposal templates"""
    return await doc_pg.list_ordered(doc_pg.C_PROPOSAL_TEMPLATES, 100)


@router.post("/proposals", response_model=dict)
async def create_proposal_template(
    template: ProposalTemplate,
    current_user: dict = Depends(require_admin)
):
    """Create a new proposal template"""
    doc = template.model_dump()
    doc.setdefault("is_active", True)
    doc["created_at"] = doc["created_at"].isoformat()
    await doc_pg.insert_document(doc_pg.C_PROPOSAL_TEMPLATES, doc)
    out = template.model_dump()
    out.setdefault("is_active", True)
    return out


@router.put("/proposals/{template_id}", response_model=dict)
async def update_proposal_template(
    template_id: str,
    template: ProposalTemplate,
    current_user: dict = Depends(require_admin)
):
    """Update a proposal template"""
    update_data = template.model_dump()
    update_data.setdefault("is_active", True)
    update_data["id"] = template_id  # Preserve ID
    update_data["created_at"] = (
        update_data["created_at"].isoformat()
        if hasattr(update_data["created_at"], "isoformat")
        else update_data["created_at"]
    )

    cur = await doc_pg.get_by_doc_id(doc_pg.C_PROPOSAL_TEMPLATES, template_id)
    if not cur:
        raise HTTPException(status_code=404, detail="Template not found")

    ok = await doc_pg.merge_set_by_doc_id(
        doc_pg.C_PROPOSAL_TEMPLATES, template_id, update_data
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Template not found")

    return update_data


@router.delete("/proposals/{template_id}")
async def delete_proposal_template(
    template_id: str,
    current_user: dict = Depends(require_admin)
):
    """Delete a proposal template"""
    deleted = await doc_pg.delete_by_doc_id(
        doc_pg.C_PROPOSAL_TEMPLATES, template_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"status": "success"}


# ================= SEED DEFAULT TEMPLATES =================

async def seed_default_templates():
    """Seed default certification packages and proposal templates"""
    # Check if packages exist
    if await doc_pg.count_all(doc_pg.C_CERTIFICATION_PACKAGES) == 0:
        default_packages = [
            CertificationPackage(
                name="Quality Management",
                name_ar="إدارة الجودة",
                standards=["ISO 9001:2015"],
                description="Quality Management System certification",
                is_default=True
            ),
            CertificationPackage(
                name="Environmental Management",
                name_ar="الإدارة البيئية",
                standards=["ISO 14001:2015"],
                description="Environmental Management System certification"
            ),
            CertificationPackage(
                name="Occupational Health & Safety",
                name_ar="الصحة والسلامة المهنية",
                standards=["ISO 45001:2018"],
                description="Occupational Health & Safety Management System"
            ),
            CertificationPackage(
                name="Integrated Management System",
                name_ar="نظام الإدارة المتكامل",
                standards=["ISO 9001:2015", "ISO 14001:2015", "ISO 45001:2018"],
                description="Combined QMS, EMS, and OH&S certification"
            )
        ]
        for pkg in default_packages:
            d = pkg.model_dump()
            d.setdefault("is_active", True)
            d["created_at"] = d["created_at"].isoformat()
            await doc_pg.insert_document(doc_pg.C_CERTIFICATION_PACKAGES, d)

    # Check if templates exist
    if await doc_pg.count_all(doc_pg.C_PROPOSAL_TEMPLATES) == 0:
        default_templates = [
            ProposalTemplate(
                name="Standard Package",
                name_ar="الباقة القياسية",
                initial_certification_fee=15000,
                surveillance_1_fee=5000,
                surveillance_2_fee=5000,
                recertification_fee=12000,
                description="Standard pricing for medium-sized organizations",
                is_default=True
            ),
            ProposalTemplate(
                name="Small Business",
                name_ar="المؤسسات الصغيرة",
                initial_certification_fee=10000,
                surveillance_1_fee=3500,
                surveillance_2_fee=3500,
                recertification_fee=8000,
                description="Discounted pricing for small businesses"
            ),
            ProposalTemplate(
                name="Enterprise",
                name_ar="المؤسسات الكبيرة",
                initial_certification_fee=25000,
                surveillance_1_fee=8000,
                surveillance_2_fee=8000,
                recertification_fee=20000,
                description="Premium pricing for large organizations"
            )
        ]
        for tmpl in default_templates:
            d = tmpl.model_dump()
            d.setdefault("is_active", True)
            d["created_at"] = d["created_at"].isoformat()
            await doc_pg.insert_document(doc_pg.C_PROPOSAL_TEMPLATES, d)
