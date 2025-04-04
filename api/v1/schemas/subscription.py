from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from typing import List
from datetime import datetime
from datetime import date
class SubscriptionBase(BaseModel):
    user_id: str
    company_id: str
    tier: str
    billing_cycle: str
    start_date: date
    end_date: date
    status: str = "active"

class SubscriptionCreate(BaseModel):
    company_id: str
    tier: str
    billing_cycle: str
    start_date: date
    end_date: date

class SubscriptionUpdate(BaseModel):
    tier: Optional[str] = None
    billing_cycle: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None

class SubscriptionInDB(SubscriptionBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SubscriptionData(SubscriptionInDB):
    class Config:
        from_attributes = True

class SubscriptionResponse(BaseModel):
    status: str
    status_code: int
    message: str
    data: SubscriptionData

class AllSubscriptionsResponse(BaseModel):
    status: str
    status_code: int
    message: str
    page: int
    per_page: int
    total: int
    data: List[SubscriptionData]
