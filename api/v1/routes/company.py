from typing import Annotated, Optional, Literal
from fastapi import Depends, APIRouter, Request, status, Query, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.company import CompanyCreate, CompanyLogin
from api.db.database import get_db
from api.v1.services.company import company_service
from api.v1.services.user import user_service


company_router = APIRouter(prefix="/company", tags=["Companies"])


@company_router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_company(
    schema: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    try:
        company_created = company_service.create(db, creator_id = current_user.id, company_in = schema)
        return success_response(
            status_code=status.HTTP_201_CREATED,
            message="Company created successfully",
            data=company_created
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create company: {str(e)}"
        )

@company_router.post("/login")
async def login_company(
    schema: CompanyLogin,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    company_login = company_service.fetch(db, company_login = schema, user_id = current_user.id)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Company logged in successfully",
        data=company_login
    )

