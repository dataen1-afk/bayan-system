"""
Document management routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from typing import List, Optional
import base64

from database import db
from auth import require_admin
from models.document import Document, DocumentCreate

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=List[dict])
async def get_documents(
    related_id: Optional[str] = None,
    related_type: Optional[str] = None,
    current_user: dict = Depends(require_admin)
):
    """Get all documents with optional filtering"""
    query = {}
    if related_id:
        query["related_id"] = related_id
    if related_type:
        query["related_type"] = related_type
    
    # Return without file_data for listing (too large)
    documents = await db.documents.find(
        query, 
        {"_id": 0, "file_data": 0}
    ).to_list(1000)
    return documents


@router.post("", response_model=dict)
async def upload_document(
    doc_data: DocumentCreate,
    current_user: dict = Depends(require_admin)
):
    """Upload a new document"""
    # Calculate file size
    try:
        file_size = len(base64.b64decode(doc_data.file_data))
    except:
        file_size = 0
    
    document = Document(
        filename=doc_data.filename,
        original_filename=doc_data.filename,
        file_type=doc_data.file_type,
        file_size=file_size,
        file_data=doc_data.file_data,
        related_id=doc_data.related_id,
        related_type=doc_data.related_type,
        description=doc_data.description,
        uploaded_by=current_user.get("user_id", "")
    )
    
    await db.documents.insert_one(document.model_dump())
    
    # Return without file_data
    result = document.model_dump()
    del result["file_data"]
    return result


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    current_user: dict = Depends(require_admin)
):
    """Get a specific document including file data"""
    doc = await db.documents.find_one({"id": document_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: dict = Depends(require_admin)
):
    """Download a document file"""
    doc = await db.documents.find_one({"id": document_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    file_data = base64.b64decode(doc.get("file_data", ""))
    
    # Determine media type
    file_type = doc.get("file_type", "application/octet-stream")
    media_type_map = {
        "pdf": "application/pdf",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xls": "application/vnd.ms-excel",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }
    media_type = media_type_map.get(file_type.lower(), "application/octet-stream")
    
    return Response(
        content=file_data,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{doc.get("original_filename", "document")}"'
        }
    )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(require_admin)
):
    """Delete a document"""
    result = await db.documents.delete_one({"id": document_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "success"}
