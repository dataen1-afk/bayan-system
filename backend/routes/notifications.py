"""
Notification routes (PostgreSQL / app_documents).
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.exc import SQLAlchemyError

from auth import get_current_user, security
from models.notification import Notification
from notifications_pg import (
    delete_all_notifications,
    insert_notification_document,
    list_notifications,
    mark_notification_read,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

DB_UNAVAILABLE_DETAIL = "Database temporarily unavailable. Please try again shortly."


async def create_notification_helper(
    notification_type: str,
    title: str,
    message: str,
    related_id: str = None,
    related_type: str = None,
):
    """Helper function to create a notification"""
    notification = Notification(
        type=notification_type,
        title=title,
        message=message,
        related_id=related_id,
        related_type=related_type,
    )
    notification_doc = notification.model_dump()
    notification_doc["created_at"] = notification_doc["created_at"].isoformat()
    try:
        await insert_notification_document(notification_doc)
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE_DETAIL)
    return notification


@router.get("")
async def get_notifications(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    limit: int = 20,
    unread_only: bool = False,
):
    """Get admin notifications"""
    await get_current_user(credentials)

    try:
        notifications, unread_count = await list_notifications(
            limit=limit, unread_only=unread_only
        )
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE_DETAIL)

    return {
        "notifications": notifications,
        "unread_count": unread_count,
    }


@router.put("/read-all")
async def mark_all_notifications_read(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Mark all notifications as read and clear them (must be registered before /{id}/read)."""
    await get_current_user(credentials)
    try:
        await delete_all_notifications()
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE_DETAIL)

    return {"message": "All notifications cleared"}


@router.put("/{notification_id}/read")
async def mark_notification_read_route(
    notification_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Mark a notification as read"""
    await get_current_user(credentials)

    try:
        ok = await mark_notification_read(notification_id)
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE_DETAIL)

    if not ok:
        raise HTTPException(status_code=404, detail="Notification not found")

    return {"message": "Notification marked as read"}
