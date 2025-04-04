from api.v1.models.base_model import BaseTableModel
from uuid_extensions import uuid7
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, text, Boolean, Index, ForeignKey, Numeric, DateTime, Text
from datetime import datetime

class AuditTrail(BaseTableModel):
    __tablename__ = "audit_trail"
    
    admin_id = Column(String, ForeignKey("users.id"), nullable=False)
    action_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    affected_table = Column(String, nullable=False)
    affected_record_id = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    admin = relationship("User", back_populates="audit_trails")
    
    __table_args__ = (
        Index('ix_audit_trail_admin_id', 'admin_id'),
        Index('ix_audit_trail_action_type', 'action_type'),
        Index('ix_audit_trail_affected_table', 'affected_table'),
    )
    
    def __str__(self):
        return f"{self.action_type} - {self.affected_table}"