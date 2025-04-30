from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class Social(BaseModel):
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    website: Optional[str] = None

class CompanyFounder(BaseModel):
    name: str
    role: Optional[str] = None
    bio: Optional[str] = None 
    avatar: Optional[str] = None
    social: Optional[Social] = None

class SocialMedia(BaseModel):
    platform : str
    url : str

class ServiceModel(BaseModel):
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True
        validate_by_name = True

class CompanyBase(BaseModel):
    acquisitions: Optional[int] = None
    company_type: Optional[str] = None
    company_name: Optional[str] = None
    company_email: Optional[EmailStr] = None
    company_phone: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    year_founded: Optional[int] = None
    headquarters: Optional[str] = None
    social_media: Optional[List[SocialMedia]] = None
    services: Optional[List[ServiceModel]] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    status: Optional[str] = "active"
    last_funding_date: Optional[str] = None
    niche: Optional[str] = None
    founders: Optional[List[CompanyFounder]] = None

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
    services: Optional[List[ServiceModel]] = None
    logo: Optional[str] = None
    social_media_linkedIn: Optional[str] = None
    social_media_ig: Optional[str] = None   
    social_media_X: Optional[str] = None
    status: Optional[str] = None
    founders: Optional[List[CompanyFounder]] = None

class CompanyLogin(BaseModel):
    email: EmailStr
    password: str

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
    founders: Optional[List[CompanyFounder]] = None
    services: Optional[List[ServiceModel]] = None
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


class CompanyListResponse(BaseModel):
    id: str
    name: str  # Matches the SQLAlchemy label
    website: Optional[str] = None
    services: List[ServiceModel] = []
    lastFundingDate: Optional[datetime] = None
    employees: Optional[str] = None
    acquisitions: Optional[int] = None
    type: Optional[str] = None
    country: Optional[str] = None
    logo: Optional[str] = None
    niche: Optional[str] = None

    class Config:
        from_attributes = True
        validate_by_name = True

class PaginationData(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int

class CompanySearchItem(BaseModel):
    id: str
    name: str
    website: Optional[str] = None
    lastFundingDate: Optional[str] = None
    employees: Optional[str] = None
    acquisitions: Optional[int] = 0
    type: Optional[str] = None
    country: Optional[str] = None
    logo: Optional[str] = None
    niche: Optional[str] = None
    services: Optional[List[dict]] = []
    founders: Optional[List[dict]] = []
    
    class Config:
        from_attributes = True

class CompanySearchResponse(BaseModel):
    data: List[CompanySearchItem]
    pagination: PaginationData
    
    class Config:
        from_attributes = True

class SuccessResponse(BaseModel):
    status: str
    status_code: int
    message: str
    data: Optional[CompanyInDB] = None

class ListSuccessResponse(SuccessResponse):
    data: Optional[List[CompanyListResponse]] = None
    pagination: PaginationData

class CompanySearch(BaseModel):
    country: Optional[str] = None  # (headquarters)
    size: Optional[str] = None     # (company_size)
    niche: Optional[str] = None
    year_founded: Optional[int] = None
    search_term: Optional[str] = None