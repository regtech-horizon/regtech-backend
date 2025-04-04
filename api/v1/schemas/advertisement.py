from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from typing import List
from datetime import datetime
from datetime import date

class AdvertisementBase(BaseModel):
    company_id: str
    ad_type: str
    ad_content: str
    placement: str
    start_date: date
    end_date: date
    performance_metrics: Optional[str] = None

class AdvertisementCreate(AdvertisementBase):
    pass

class AdvertisementUpdate(BaseModel):
    ad_type: Optional[str] = None
    ad_content: Optional[str] = None
    placement: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    performance_metrics: Optional[str] = None

class AdvertisementInDB(AdvertisementBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AdvertisementData(AdvertisementInDB):
    class Config:
        from_attributes = True

class AdvertisementResponse(BaseModel):
    status: str
    status_code: int
    message: str
    data: AdvertisementData

class AllAdvertisementsResponse(BaseModel):
    status: str
    status_code: int
    message: str
    page: int
    per_page: int
    total: int
    data: List[AdvertisementData]
