from pydantic import BaseModel, EmailStr, Field, StringConstraints, validator, root_validator
from typing import Optional, List, Dict, Any, Literal, Annotated
from datetime import datetime, date
from uuid import UUID

# Payment schemas
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