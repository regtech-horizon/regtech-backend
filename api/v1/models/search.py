from api.v1.models.base_model import BaseTableModel
from uuid_extensions import uuid7
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, text, Boolean, Index, ForeignKey, Numeric, Date, Text
class SavedSearch(BaseTableModel):
    __tablename__ = "saved_searches"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    search_parameters = Column(Text, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="saved_searches")
    
    __table_args__ = (
        Index('ix_saved_searches_user_id', 'user_id'),
    )
    
    def __str__(self):
        return f"Search by {self.user.email}"