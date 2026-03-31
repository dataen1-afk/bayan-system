"""
Notification routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from typing import List, Optional
from datetime import datetime, timezone

from database import db
from auth import get_current_user, security
from models.notification import Notification, NotificationCreate

router = APIRouter(prefix="/notifications", tags=["Notifications"])


async def create_notification_helper(
    notification_type: str, 
    title: str, 
    message: str, 
    related_id: str = None, 
    related_type: str = None
):
    """Helper function to create a notification"""
    notification = Notification(
        type=notification_type,
        title=title,
        message=message,
        related_id=related_id,
        related_type=related_type
    )
    notification_doc = notification.model_dump()
    notification_doc['created_at'] = notification_doc['created_at'].isoformat()
    await db.notifications.insert_one(notification_doc)
    return notification


@router.get("")
async def get_notifications(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    limit: int = 20, 
    unread_only: bool = False
):
    """Get admin notifications"""
    await get_current_user(credentials)
    
    query = {}
    if unread_only:
        query['is_read'] = False
    
    notifications = await db.notifications.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    unread_count = await db.notifications.count_documents({"is_read": False})
    
    return {
        "notifications": notifications,
        "unread_count": unread_count
    }


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Mark a notification as read"""
    await get_current_user(credentials)
    
    result = await db.notifications.update_one(
        {"id": notification_id},
        {"$set": {"is_read": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as read"}


@router.put("/read-all")
async def mark_all_notifications_read(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Mark all notifications as read and clear them"""
    await get_current_user(credentials)
    
    # Delete all notifications to prevent accumulation
    await db.notifications.delete_many({})
    
    return {"message": "All notifications cleared"}
