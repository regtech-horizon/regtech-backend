from typing import Optional, List, Dict, Any

from pydantic import BaseModel, EmailStr, Field, ConfigDict
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
    platform: str
    url: str

class ServiceModel(BaseModel):
    name: str
    description: Optional[str] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )

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
    services: Optional[List[ServiceModel]] = None  # Changed from JSONB to List
    description: Optional[str] = None
    logo: Optional[str] = None
    status: Optional[str] = "active"
    last_funding_date: Optional[str] = None
    niche: Optional[str] = None
    founders: Optional[List[CompanyFounder]] = None  # Changed from JSONB to List

    model_config = ConfigDict(
        extra="ignore",  # Ignore extra fields
        protected_namespaces=(),
        arbitrary_types_allowed=True,
        from_attributes=True
    )

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    company_name: Optional[str] = None
    company_type: Optional[str] = None
    company_email: Optional[EmailStr] = None
    company_phone: Optional[str] = None
    company_website: Optional[str] = None
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
    niche: Optional[str] = None
    acquisitions: Optional[int] = None
    last_funding_date: Optional[str] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )

class CompanyLogin(BaseModel):
    email: EmailStr
    password: str

class CompanyInDB(CompanyBase):
    id: str
    creator_id: str
    created_at: datetime
    updated_at: datetime
    
    company_password: str = Field(exclude=True)
    
    model_config = ConfigDict(
        from_attributes=True
    )

class CompanyData(BaseModel):
    id: str
    name: str
    company_type: Optional[str] = None
    company_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    company_size: Optional[str] = None
    year_founded: Optional[int] = None
    headquarters: Optional[str] = None
    description: Optional[str] = None
    founders: Optional[List[CompanyFounder]] = None  # Changed from JSONB to List
    services: Optional[List[ServiceModel]] = None  # Changed from JSONB to List
    logo: Optional[str] = None
    social_media_linkedIn: Optional[str] = None
    social_media_ig: Optional[str] = None
    social_media_X: Optional[str] = None
    status: str
    last_funding_date: Optional[str] = None
    niche: Optional[str] = None
    creator_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )

class CompanyResponse(BaseModel):
    status: str
    status_code: int
    message: str
    data: CompanyInDB

class CompanyResponseData(BaseModel):
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
    founders: Optional[List[CompanyFounder]] = None  # Changed from JSONB to List
    services: Optional[List[ServiceModel]] = None  # Changed from JSONB to List
    lastFundingDate: Optional[datetime] = None
    employees: Optional[str] = None
    description: Optional[str] = None
    year_founded: Optional[int] = None
    headquarters: Optional[str] = None
    acquisitions: Optional[int] = None
    type: Optional[str] = None
    country: Optional[str] = None
    logo: Optional[str] = None
    niche: Optional[str] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )

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
    founders: Optional[List[CompanyFounder]] = None  # Changed from JSONB to List
    services: Optional[List[ServiceModel]] = None  # Changed from JSONB to List
    
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )

class CompanySearchResponse(BaseModel):
    data: List[CompanySearchItem]
    pagination: PaginationData
    
    model_config = ConfigDict(
        from_attributes=True
    )

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

class CompanyChangePasswordSchema(BaseModel):
    """Schema for changing company password"""
    current_password: str = Field(..., description="Current company password")
    new_password: str = Field(..., description="New company password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "oldPassword123",
                "new_password": "newSecurePassword456"
            }
        }
