from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from typing import List
from datetime import datetime

class SocialMedia(BaseModel):
    platform : str
    url : str
class CompanyBase(BaseModel):
    company_type: Optional[str] = None
    company_name: Optional[str] = None
    company_email: Optional[EmailStr] = None
    company_phone: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    year_founded: Optional[int] = None
    headquarters: Optional[str] = None
    social_media: Optional[List[SocialMedia]] = None
    services: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    status: Optional[str] = "active"
    last_funding_date: Optional[str] = None
    niche: Optional[str] = None
    company_password: Optional[str] = None
    founders: Optional[List[str]] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    company_type: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    company_size: Optional[str] = None
    year_founded: Optional[int] = None
    headquarters: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    social_media_linkedIn: Optional[str] = None
    social_media_ig: Optional[str] = None
    social_media_X: Optional[str] = None
    status: Optional[str] = None

class CompanyInDB(CompanyBase):
    id: str
    creator_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CompanyData(BaseModel):
    id: str
    name: str
    company_type: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    company_size: Optional[str] = None
    year_founded: Optional[int] = None
    headquarters: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    social_media_linkedIn: Optional[str] = None
    social_media_ig: Optional[str] = None
    social_media_X: Optional[str] = None
    status: str
    creator_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CompanyResponse(BaseModel):
    status: str
    status_code: int
    message: str
    data: CompanyData

class AllCompaniesResponse(BaseModel):
    status: str
    status_code: int
    message: str
    page: int
    per_page: int
    total: int
    data: List[CompanyData]
