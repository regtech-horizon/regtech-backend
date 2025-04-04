from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from typing import List
from datetime import datetime

class PaymentBase(BaseModel):
    subscription_id: str
    amount: float
    payment_method: str
    status: str = "pending"
    invoice_url: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    amount: Optional[float] = None
    payment_method: Optional[str] = None
    status: Optional[str] = None
    invoice_url: Optional[str] = None

class PaymentInDB(PaymentBase):
    id: str
    payment_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaymentData(PaymentInDB):
    class Config:
        from_attributes = True

class PaymentResponse(BaseModel):
    status: str
    status_code: int
    message: str
    data: PaymentData

class AllPaymentsResponse(BaseModel):
    status: str
    status_code: int
    message: str
    page: int
    per_page: int
    total: int
    data: List[PaymentData]
