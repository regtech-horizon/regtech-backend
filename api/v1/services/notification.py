# crud/notifications.py
from sqlalchemy.orm import Session
from api.v1.models.notification import Notification
from api.v1.services.user import user_service
from api.db.database import get_db
from fastapi import Depends


# websockets/notifications.py
from fastapi import HTTPException, WebSocket, WebSocketDisconnect, status
from typing import Dict
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_notification(self, user_id: int, notification: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(
                json.dumps(notification)
            )

manager = ConnectionManager()

async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    token: str
):
    # Validate JWT token here (use your existing auth logic)
    # Example pseudo-code:
    current_user = await user_service.get_current_user(token)
    if current_user.id != user_id:
        await websocket.close(code=1008)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission Denied! Kindly Sign in again!"
        )
        return
    
    await manager.connect(user_id, websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)

from fastapi import BackgroundTasks

# api/v1/services/notification.py
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks, Depends
import asyncio
import json

from api.v1.models.notification import Notification
from api.db.database import get_db

class NotificationService:
    def __init__(self, db: Session, bg_tasks: BackgroundTasks = None):
        self.db = db
        self.bg_tasks = bg_tasks
    
    def create_notification(
        self, 
        title: str, 
        message: str, 
        user_id: str = None, 
        company_id: str = None, 
        category: str = "system", 
        action_url: str = None, 
        priority: int = 0
    ) -> Notification:
        notification = Notification(
            title=title,
            message=message,
            user_id=user_id,
            company_id=company_id,
            category=category,
            action_url=action_url,
            priority=priority
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_user_notifications(self, user_id: str, limit: int = 15):
        return self.db.query(Notification)\
            .filter(Notification.user_id == user_id)\
            .order_by(Notification.created_at.desc())\
            .limit(limit)\
            .all()

    def get_company_notifications(self, company_id: str, limit: int = 15):
        return self.db.query(Notification)\
            .filter(Notification.company_id == company_id)\
            .order_by(Notification.created_at.desc())\
            .limit(limit)\
            .all()

    def mark_notification_as_read(self, notification_id: str):
        notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if notification:
            notification.is_read = True
            self.db.commit()
            self.db.refresh(notification)
        return notification

    async def send_immediate_notification(self, notification_data: dict):
        """Send notification immediately"""
        self.create_notification(
            title=notification_data.get('title'),
            message=notification_data.get('message'),
            user_id=notification_data.get('user_id'),
            company_id=notification_data.get('company_id'),
            category=notification_data.get('category', 'system'),
            action_url=notification_data.get('action_url'),
            priority=notification_data.get('priority', 0)
        )

    def schedule_notification(self, notification_data: dict, delay_seconds: int = 0):
        """Schedule notification with delay (using background tasks)"""
        if self.bg_tasks:
            self.bg_tasks.add_task(
                self._delayed_notification,
                notification_data,
                delay_seconds
            )

    async def _delayed_notification(self, notification_data: dict, delay: int):
        await asyncio.sleep(delay)
        await self.send_immediate_notification(notification_data)

# Factory function to get notification service
def get_notification_service(db: Session = Depends(get_db), bg_tasks: BackgroundTasks = None):
    return NotificationService(db, bg_tasks)