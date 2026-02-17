"""
Site management routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from database import db
from auth import require_admin
from models.site import Site, SiteCreate

router = APIRouter(prefix="/sites", tags=["Sites"])


@router.get("", response_model=List[dict])
async def get_sites(
    organization_id: Optional[str] = None,
    current_user: dict = Depends(require_admin)
):
    """Get all sites with optional filtering by organization"""
    query = {}
    if organization_id:
        query["organization_id"] = organization_id
    
    sites = await db.sites.find(query, {"_id": 0}).to_list(1000)
    return sites


@router.post("", response_model=dict)
async def create_site(
    site_data: SiteCreate,
    current_user: dict = Depends(require_admin)
):
    """Create a new site"""
    site = Site(
        name=site_data.name,
        name_ar=site_data.name_ar,
        address=site_data.address,
        city=site_data.city,
        country=site_data.country,
        contact_name=site_data.contact_name,
        contact_phone=site_data.contact_phone,
        contact_email=site_data.contact_email,
        organization_id=site_data.organization_id
    )
    
    await db.sites.insert_one(site.model_dump())
    return site.model_dump()


@router.get("/{site_id}", response_model=dict)
async def get_site(
    site_id: str,
    current_user: dict = Depends(require_admin)
):
    """Get a specific site"""
    site = await db.sites.find_one({"id": site_id}, {"_id": 0})
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


@router.delete("/{site_id}")
async def delete_site(
    site_id: str,
    current_user: dict = Depends(require_admin)
):
    """Delete a site"""
    result = await db.sites.delete_one({"id": site_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Site not found")
    return {"status": "success"}
