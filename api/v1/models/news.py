from api.v1.models.base_model import BaseTableModel
from uuid_extensions import uuid7
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, text, Boolean, Index, ForeignKey, Numeric, Date, Text

class News(BaseTableModel):
    __tablename__ = "news"
    
    title = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    publication_date = Column(Date, nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    status = Column(String, nullable=False, default="draft")
    
    # Relationships
    author = relationship("User", back_populates="news_articles")
    
    __table_args__ = (
        Index('ix_news_author_id', 'author_id'),
        Index('ix_news_status', 'status'),
        Index('ix_news_publication_date', 'publication_date'),
    )
    
    def __str__(self):
        return self.title
