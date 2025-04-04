from pydantic import BaseModel, EmailStr, Field, StringConstraints, validator, root_validator
from typing import Optional, List, Dict, Any, Literal, Annotated
from datetime import datetime, date
from uuid import UUID

# User schemas
class UserBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    role: Optional[str] = "user"
    status: Optional[str] = "active"

class UserCreate(BaseModel):
    """Schema to create a user"""
    email: EmailStr
    password: Annotated[
        str, StringConstraints(
            min_length=8,
            max_length=64,
            strip_whitespace=True
        )
    ]
    confirm_password: Annotated[
        str, 
        StringConstraints(
            min_length=8,
            max_length=64,
            strip_whitespace=True
        ),
        Field(exclude=True)  # exclude confirm_password field
    ]
    first_name: Annotated[
        str, StringConstraints(
            min_length=2,
            max_length=30,
            strip_whitespace=True
        )
    ]
    last_name: Annotated[
        str, StringConstraints(
            min_length=2,
            max_length=30,
            strip_whitespace=True
        )
    ]
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserUpdate(BaseModel):
    """Schema to update a user"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    status: Optional[str] = None

class UserInDB(UserBase):
    id: str
    is_active: bool
    is_superadmin: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserData(BaseModel):
    id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    role: str
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    status: str
    status_code: int
    message: str
    data: UserData

class AllUsersResponse(BaseModel):
    status: str
    status_code: int
    message: str
    page: int
    per_page: int
    total: int
    data: List[UserData]

class AdminCreateUser(UserCreate):
    """Admin schema to create a user"""
    is_superadmin: Optional[bool] = False

class AdminCreateUserResponse(BaseModel):
    status: str
    status_code: int
    message: str
    data: UserData

# Company schemas
class CompanyBase(BaseModel):
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
    status: Optional[str] = "active"

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

# Subscription schemas
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

# Payment schemas
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

# Review schemas
class ReviewBase(BaseModel):
    company_id: str
    rating: int
    review_text: Optional[str] = None

class ReviewCreate(ReviewBase):
    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    review_text: Optional[str] = None
    
    @validator('rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating must be between 1 and 5')
        return v

class ReviewInDB(BaseModel):
    id: str
    user_id: str
    company_id: str
    rating: int
    review_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ReviewData(ReviewInDB):
    class Config:
        from_attributes = True

class ReviewResponse(BaseModel):
    status: str
    status_code: int
    message: str
    data: ReviewData

class AllReviewsResponse(BaseModel):
    status: str
    status_code: int
    message: str
    page: int
    per_page: int
    total: int
    data: List[ReviewData]

# Advertisement schemas
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

# News schemas
class NewsBase(BaseModel):
    title: str
    summary: str
    content: str
    publication_date: date
    status: str = "draft"

class NewsCreate(NewsBase):
    pass

class NewsUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    publication_date: Optional[date] = None
    status: Optional[str] = None

class NewsInDB(NewsBase):
    id: str
    author_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class NewsData(NewsInDB):
    class Config:
        from_attributes = True

class NewsResponse(BaseModel):
    status: str
    status_code: int
    message: str
    data: NewsData

class AllNewsResponse(BaseModel):
    status: str
    status_code: int
    message: str
    page: int
    per_page: int
    total: int
    data: List[NewsData]

# SavedSearch schemas
class SavedSearchBase(BaseModel):
    search_parameters: str

class SavedSearchCreate(SavedSearchBase):
    pass

class SavedSearchUpdate(BaseModel):
    search_parameters: Optional[str] = None

class SavedSearchInDB(SavedSearchBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SavedSearchData(SavedSearchInDB):
    class Config:
        from_attributes = True

class SavedSearchResponse(BaseModel):
    status: str
    status_code: int
    message: str
    data: SavedSearchData

class AllSavedSearchesResponse(BaseModel):
    status: str
    status_code: int
    message: str
    page: int
    per_page: int
    total: int
    data: List[SavedSearchData]

# FavoriteCompany schemas
class FavoriteCompanyBase(BaseModel):
    company_id: str

class FavoriteCompanyCreate(FavoriteCompanyBase):
    pass

class FavoriteCompanyInDB(FavoriteCompanyBase):
    id: str
    user_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class FavoriteCompanyData(FavoriteCompanyInDB):
    class Config:
        from_attributes = True

class FavoriteCompanyResponse(BaseModel):
    status: str
    status_code: int
    message: str
    data: FavoriteCompanyData

class AllFavoriteCompaniesResponse(BaseModel):
    status: str
    status_code: int
    message: str
    page: int
    per_page: int
    total: int
    data: List[FavoriteCompanyData]