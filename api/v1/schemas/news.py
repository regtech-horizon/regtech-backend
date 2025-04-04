from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from typing import List
from datetime import datetime
from datetime import date

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
