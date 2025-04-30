# api/v1/models/activity_log.py
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from api.db.database import Base
from datetime import datetime
import uuid

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String, nullable=False)  # search, favorite, newsletter, company
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ActivityLog {self.activity_type} for user {self.user_id}>"