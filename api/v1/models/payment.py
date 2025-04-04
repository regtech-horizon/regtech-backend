from api.v1.models.base_model import BaseTableModel
from uuid_extensions import uuid7
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, text, Boolean, Index, ForeignKey, Numeric, DateTime, Float
from datetime import datetime
class Payment(BaseTableModel):
    __tablename__ = "payments"
    
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    payment_method = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    invoice_url = Column(String, nullable=True)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="payments")
    
    __table_args__ = (
        Index('ix_payments_subscription_id', 'subscription_id'),
        Index('ix_payments_status', 'status'),
    )
    
    def __str__(self):
        return f"{self.amount} - {self.status}"
