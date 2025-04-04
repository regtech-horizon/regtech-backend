from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator
from typing import List
from datetime import datetime
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
