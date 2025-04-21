from api.v1.models.base_model import BaseTableModel
from uuid_extensions import uuid7
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, text, Boolean, Index, ForeignKey, Numeric, DateTime
from datetime import datetime, timezone
class LoginHistory(BaseTableModel):
    __tablename__ = "login_history"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    login_timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    ip_address = Column(String, nullable=True)
    device_info = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="login_history")
    
    __table_args__ = (
        Index('ix_login_history_user_id', 'user_id'),
        Index('ix_login_history_login_timestamp', 'login_timestamp'),
    )
    
    def __str__(self):
        return f"{self.user.email} - {self.login_timestamp}"