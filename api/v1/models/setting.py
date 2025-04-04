from api.v1.models.base_model import BaseTableModel
from uuid_extensions import uuid7
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, text, Boolean, Index, ForeignKey, Numeric, DateTime
from datetime import datetime

class Setting(BaseTableModel):
    __tablename__ = "settings"
    
    key = Column(String, nullable=False, unique=True)
    value = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    __table_args__ = (
        Index('ix_settings_key', 'key'),
    )
    
    def __str__(self):
        return self.key     