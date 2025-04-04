from api.v1.models.base_model import BaseTableModel
from uuid_extensions import uuid7
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, text, Boolean, Index, ForeignKey, Numeric, Date, Integer, Text, DateTime
from datetime import datetime
class CompanyProfile(BaseTableModel):
    __tablename__ = "company_profile"
    
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, unique=True)
    profile_views = Column(Integer, nullable=False, default=0)
    clicks = Column(Integer, nullable=False, default=0)
    additional_metrics = Column(String, nullable=True)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="profile")
    
    __table_args__ = (
        Index('ix_company_profile_company_id', 'company_id'),
    )
    
    def __str__(self):
        return f"Profile for {self.company.name}"