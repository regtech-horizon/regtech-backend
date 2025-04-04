from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from typing import List
from datetime import datetime

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