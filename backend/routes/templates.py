"""
Template routes (Certification Packages and Proposal Templates).
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List

from database import db
from auth import require_admin
from models.template import CertificationPackage, ProposalTemplate

router = APIRouter(prefix="/templates", tags=["Templates"])


# ================= CERTIFICATION PACKAGES =================

@router.get("/packages", response_model=List[dict])
async def get_certification_packages(current_user: dict = Depends(require_admin)):
    """Get all certification packages"""
    packages = await db.certification_packages.find({}, {"_id": 0}).to_list(100)
    return packages


@router.post("/packages", response_model=dict)
async def create_certification_package(
    package: CertificationPackage,
    current_user: dict = Depends(require_admin)
):
    """Create a new certification package"""
    await db.certification_packages.insert_one(package.model_dump())
    return package.model_dump()


@router.put("/packages/{package_id}", response_model=dict)
async def update_certification_package(
    package_id: str,
    package: CertificationPackage,
    current_user: dict = Depends(require_admin)
):
    """Update a certification package"""
    update_data = package.model_dump()
    update_data["id"] = package_id  # Preserve ID
    
    result = await db.certification_packages.update_one(
        {"id": package_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Package not found")
    
    return update_data


@router.delete("/packages/{package_id}")
async def delete_certification_package(
    package_id: str,
    current_user: dict = Depends(require_admin)
):
    """Delete a certification package"""
    result = await db.certification_packages.delete_one({"id": package_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Package not found")
    return {"status": "success"}


# ================= PROPOSAL TEMPLATES =================

@router.get("/proposals", response_model=List[dict])
async def get_proposal_templates(current_user: dict = Depends(require_admin)):
    """Get all proposal templates"""
    templates = await db.proposal_templates.find({}, {"_id": 0}).to_list(100)
    return templates


@router.post("/proposals", response_model=dict)
async def create_proposal_template(
    template: ProposalTemplate,
    current_user: dict = Depends(require_admin)
):
    """Create a new proposal template"""
    await db.proposal_templates.insert_one(template.model_dump())
    return template.model_dump()


@router.put("/proposals/{template_id}", response_model=dict)
async def update_proposal_template(
    template_id: str,
    template: ProposalTemplate,
    current_user: dict = Depends(require_admin)
):
    """Update a proposal template"""
    update_data = template.model_dump()
    update_data["id"] = template_id  # Preserve ID
    
    result = await db.proposal_templates.update_one(
        {"id": template_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return update_data


@router.delete("/proposals/{template_id}")
async def delete_proposal_template(
    template_id: str,
    current_user: dict = Depends(require_admin)
):
    """Delete a proposal template"""
    result = await db.proposal_templates.delete_one({"id": template_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"status": "success"}


# ================= SEED DEFAULT TEMPLATES =================

async def seed_default_templates():
    """Seed default certification packages and proposal templates"""
    # Check if packages exist
    existing_packages = await db.certification_packages.count_documents({})
    if existing_packages == 0:
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
            await db.certification_packages.insert_one(pkg.model_dump())
    
    # Check if templates exist
    existing_templates = await db.proposal_templates.count_documents({})
    if existing_templates == 0:
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
            await db.proposal_templates.insert_one(tmpl.model_dump())
