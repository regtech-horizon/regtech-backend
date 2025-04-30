# schemas/notification.py
from pydantic import BaseModel
from datetime import datetime

class NotificationBase(BaseModel):
    user_id: str
    title: str
    message: str
    category: str = "system"
    action_url: str | None = None
    priority: int = 0

class NotificationCreate(NotificationBase):
    pass

class NotificationOut(NotificationBase):
    id: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True