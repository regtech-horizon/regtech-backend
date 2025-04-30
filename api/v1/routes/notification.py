from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.v1.models.notification import Notification

from ..schemas.notification import NotificationOut, NotificationCreate
from api.db.database import get_db
from api.v1.services.user import user_service
from ..services.notification import NotificationService, get_notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.post("/", response_model=NotificationOut)
async def create_user_notification(
    notification: NotificationCreate,
    notification_service: NotificationService = Depends(get_notification_service),
    current_user: dict = Depends(user_service.get_current_user)
):
    """Create a new notification (typically called internally)"""
    if current_user.id != notification.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create notifications for other users"
        )
    return notification_service.create_notification(
        title=notification.title,
        message=notification.message,
        user_id=notification.user_id,
        category=notification.category,
        action_url=notification.action_url if hasattr(notification, 'action_url') else None,
        priority=notification.priority if hasattr(notification, 'priority') else 0
    )

@router.get("/", response_model=List[NotificationOut])
async def get_current_user_notifications(
    skip: int = 0,
    limit: int = 100,
    notification_service: NotificationService = Depends(get_notification_service),
    current_user: dict = Depends(user_service.get_current_user)
):
    """Get authenticated user's notifications"""
    return notification_service.get_user_notifications(
        user_id=current_user.id, 
        limit=limit
    )

@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    notification_service: NotificationService = Depends(get_notification_service),
    current_user: dict = Depends(user_service.get_current_user)
):
    """Mark a notification as read"""
    success = notification_service.mark_notification_as_read(notification_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return {"status": "marked_as_read"}