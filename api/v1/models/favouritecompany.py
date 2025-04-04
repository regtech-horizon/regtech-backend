from api.v1.models.base_model import BaseTableModel
from uuid_extensions import uuid7
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, text, Boolean, Index, ForeignKey, Numeric

class FavoriteCompany(BaseTableModel):
    __tablename__ = "favorite_companies"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="favorite_companies")
    company = relationship("Company", back_populates="favorite_by")
    
    __table_args__ = (
        Index('ix_favorite_companies_user_id', 'user_id'),
        Index('ix_favorite_companies_company_id', 'company_id'),
    )
    
    def __str__(self):
        return f"{self.user.email} - {self.company.name}"