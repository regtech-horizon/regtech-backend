from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from typing import List
from datetime import datetime

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
