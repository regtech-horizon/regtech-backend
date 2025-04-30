from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.v1.models.base_model import BaseTableModel
from datetime import datetime, timezone

from uuid_extensions import uuid7

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.v1.models.base_model import BaseTableModel
from datetime import datetime, timezone
from uuid_extensions import uuid7

class Notification(BaseTableModel):
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid7()), index=True)
    
    # Foreign keys - at least one should be non-null
    user_id = Column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    company_id = Column(
        String, ForeignKey("companies.id", ondelete="CASCADE"), nullable=True
    )
    
    # Notification content
    title = Column(String(100))
    message = Column(String(500))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    category = Column(String(50))  # e.g., "system", "message", "alert"
    action_url = Column(String(200), nullable=True)  # URL for notification click
    priority = Column(Integer, default=0)  # 0=normal, 1=important, 2=critical
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    company = relationship("Company", back_populates="notifications")
    
    # Add a check constraint to ensure either user_id or company_id is not null
    __table_args__ = (
        CheckConstraint('(user_id IS NOT NULL) OR (company_id IS NOT NULL)', 
                        name='check_notification_recipient'),
    )