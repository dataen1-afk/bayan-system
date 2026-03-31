"""
Document management routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid
import base64

from database import db
from auth import get_current_user, security

router = APIRouter(prefix="/documents", tags=["Documents"])


# Pydantic models (matching monolith schema)
class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    related_id: str = ""  # ID of form/proposal/agreement
    related_type: str = ""  # form, proposal, agreement
    name: str
    file_type: str = ""
    file_size: int = 0
    file_data: str = ""  # Base64 encoded
    uploaded_by: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DocumentCreate(BaseModel):
    related_id: str = ""
    related_type: str = ""
    name: str
    file_type: str
    file_data: str  # Base64 encoded


@router.get("")
async def get_documents(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    related_id: Optional[str] = None
):
    """Get documents, optionally filtered by related ID"""
    await get_current_user(credentials)
    
    query = {}
    if related_id:
        query["related_id"] = related_id
    
    # Return documents without file_data for listing (to reduce payload size)
    documents = await db.documents.find(query, {"_id": 0, "file_data": 0}).sort("created_at", -1).to_list(100)
    return documents


@router.post("")
async def upload_document(
    doc_data: DocumentCreate, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Upload a new document"""
    current_user = await get_current_user(credentials)
    
    # Calculate file size from base64
    try:
        file_bytes = base64.b64decode(
            doc_data.file_data.split(',')[-1] if ',' in doc_data.file_data else doc_data.file_data
        )
        file_size = len(file_bytes)
    except:
        file_size = 0
    
    document = Document(
        related_id=doc_data.related_id,
        related_type=doc_data.related_type,
        name=doc_data.name,
        file_type=doc_data.file_type,
        file_size=file_size,
        file_data=doc_data.file_data,
        uploaded_by=current_user.get('user_id', '')
    )
    
    doc_doc = document.model_dump()
    doc_doc['created_at'] = doc_doc['created_at'].isoformat()
    
    await db.documents.insert_one(doc_doc)
    return {"message": "Document uploaded", "id": document.id}


@router.get("/{document_id}")
async def get_document(
    document_id: str, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get a specific document including file data"""
    await get_current_user(credentials)
    
    document = await db.documents.find_one({"id": document_id}, {"_id": 0})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.delete("/{document_id}")
async def delete_document(
    document_id: str, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete a document"""
    await get_current_user(credentials)
    await db.documents.delete_one({"id": document_id})
    return {"message": "Document deleted"}
