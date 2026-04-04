"""
Site management routes.
"""
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid

import app_documents_pg as doc_pg
from auth import get_current_user, security

router = APIRouter(prefix="/sites", tags=["Sites"])


# Pydantic models (matching monolith schema)
class Site(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contract_id: str = ""  # Links to proposal/contract
    name: str
    address: str = ""
    city: str = ""
    country: str = ""
    contact_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    is_main_site: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SiteCreate(BaseModel):
    contract_id: str = ""
    name: str
    address: str = ""
    city: str = ""
    country: str = ""
    contact_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    is_main_site: bool = False


@router.get("")
async def get_sites(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all sites"""
    await get_current_user(credentials)
    return await doc_pg.list_ordered(doc_pg.C_SITES, 1000)


@router.post("")
async def create_site(
    site_data: SiteCreate, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new site"""
    await get_current_user(credentials)
    
    site = Site(
        contract_id=site_data.contract_id,
        name=site_data.name,
        address=site_data.address,
        city=site_data.city,
        country=site_data.country,
        contact_name=site_data.contact_name,
        contact_email=site_data.contact_email,
        contact_phone=site_data.contact_phone,
        is_main_site=site_data.is_main_site
    )
    
    site_doc = site.model_dump()
    site_doc['created_at'] = site_doc['created_at'].isoformat()
    
    await doc_pg.insert_document(doc_pg.C_SITES, site_doc)
    return {"message": "Site created", "id": site.id}


@router.delete("/{site_id}")
async def delete_site(
    site_id: str, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete a site"""
    await get_current_user(credentials)
    await doc_pg.delete_by_doc_id(doc_pg.C_SITES, site_id)
    return {"message": "Site deleted"}
