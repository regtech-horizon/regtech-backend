from typing import Annotated, Optional, Literal
from fastapi import Depends, APIRouter, Request, status, Query, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.company import CompanyCreate, CompanyLogin, CompanyUpdate
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
            detail=f"Failed to create company: {str(e)}",
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


@company_router.get("/all")
async def get_all_companies(
    db: Session = Depends(get_db),
    status = "active"
):
    companies = company_service.fetch_all(db, status=status)
    return companies

@company_router.get("/{company_id}")
async def get_company(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    company = company_service.get_company(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Company retrieved successfully",
        data=company
    )

@company_router.put("/{company_id}")
async def update_company(
    company_id: str,
    schema: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    company = company_service.get_company(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Check if the current user is the creator of the company
    if company.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this company"
        )
    
    updated_company = company_service.update(db, company=company, company_in=schema)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Company updated successfully",
        data=updated_company
    )
