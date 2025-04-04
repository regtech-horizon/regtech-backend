from api.v1.models.base_model import BaseTableModel
from uuid_extensions import uuid7
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, text, Boolean, Index, ForeignKey, Numeric, Date, Text
class Advertisement(BaseTableModel):
    __tablename__ = "advertisements"
    
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    ad_type = Column(String, nullable=False)
    ad_content = Column(Text, nullable=False)
    placement = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    performance_metrics = Column(String, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="advertisements")
    
    __table_args__ = (
        Index('ix_advertisements_company_id', 'company_id'),
        Index('ix_advertisements_ad_type', 'ad_type'),
    )
    
    def __str__(self):
        return f"{self.ad_type} - {self.company.name}"
