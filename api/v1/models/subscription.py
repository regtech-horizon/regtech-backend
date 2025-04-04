from api.v1.models.base_model import BaseTableModel
from uuid_extensions import uuid7
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, text, Boolean, Index, ForeignKey, Numeric, Date

class Subscription(BaseTableModel):
    __tablename__ = "subscriptions"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    tier = Column(String, nullable=False)
    billing_cycle = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String, nullable=False, default="active")
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    company = relationship("Company", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_subscriptions_user_id', 'user_id'),
        Index('ix_subscriptions_company_id', 'company_id'),
        Index('ix_subscriptions_status', 'status'),
    )
    
    def __str__(self):
        return f"{self.tier} - {self.status}"