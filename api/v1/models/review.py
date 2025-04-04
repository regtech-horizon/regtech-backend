from api.v1.models.base_model import BaseTableModel
from uuid_extensions import uuid7
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, text, Boolean, Index, ForeignKey, Numeric, Date, Integer, Text

class Review(BaseTableModel):
    __tablename__ = "reviews"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    review_text = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    company = relationship("Company", back_populates="reviews")
    
    __table_args__ = (
        Index('ix_reviews_user_id', 'user_id'),
        Index('ix_reviews_company_id', 'company_id'),
        Index('ix_reviews_rating', 'rating'),
    )
    
    def __str__(self):
        return f"{self.rating}/5 - {self.user.email}"