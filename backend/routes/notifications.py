"""
Notification routes.
"""
from fastapi import APIRouter, Depends
from typing import List
from datetime import datetime, timezone

from database import db
from auth import require_admin
from models.notification import Notification, NotificationCreate

router = APIRouter(prefix="/notifications", tags=["Notifications"])


async def create_notification(notification_data: NotificationCreate):
    """Helper function to create a notification"""
    notification = Notification(
        type=notification_data.type,
        title=notification_data.title,
        message=notification_data.message,
        related_id=notification_data.related_id,
        related_type=notification_data.related_type
    )
    await db.notifications.insert_one(notification.model_dump())
    return notification


@router.get("", response_model=List[Notification])
async def get_notifications(current_user: dict = Depends(require_admin)):
    """Get all notifications (most recent first)"""
    notifications = await db.notifications.find(
        {}, {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return notifications


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(require_admin)
):
    """Mark a notification as read"""
    result = await db.notifications.update_one(
        {"id": notification_id},
        {"$set": {"is_read": True}}
    )
    if result.modified_count == 0:
        return {"status": "not_found"}
    return {"status": "success"}


@router.put("/read-all")
async def mark_all_notifications_read(current_user: dict = Depends(require_admin)):
    """Mark all notifications as read and delete them"""
    # Delete all notifications (as per the UI behavior)
    await db.notifications.delete_many({})
    return {"status": "success", "message": "All notifications cleared"}
