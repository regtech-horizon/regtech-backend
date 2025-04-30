from typing import List, Optional
from fastapi import Depends, APIRouter, Request, status, Query, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.company import (
    CompanyCreate,
    CompanyFounder,
    CompanyLogin,
    CompanyUpdate,
    CompanyInDB,
    CompanyListResponse,
    ServiceModel,
    SuccessResponse,
    ListSuccessResponse,
    PaginationData,
    CompanySearchResponse
)
from api.db.database import get_db
from api.v1.services.company import company_service
from api.v1.services.user import user_service


company_router = APIRouter(
    prefix="/company",
    tags=["Companies"],
    dependencies=[]
)

public_router = APIRouter(
    prefix="/public/companies",
    tags=["Public Companies"],
    dependencies=[]
)



@company_router.post("/register", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
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

@company_router.post("/login",  response_model=CompanyInDB)
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


@company_router.get("/all", response_model=ListSuccessResponse)
async def get_all_companies(
    db: Session = Depends(get_db),
    status = "active",
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
):
    companies, total_count = company_service.fetch_all(
        db, 
        status=status, 
        page=int(page),
        per_page=int(per_page)
    )
    return {
        "status": "success",
        "status_code": 200,
        "message": "Companies retrieved successfully",
        "data": companies,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total_count,
            "total_pages": (total_count + per_page - 1) // per_page
        }
    }


@company_router.get("/{company_id}", response_model=SuccessResponse)
async def get_company(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    company = company_service.get_company(db, company_id=company_id)
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
    company = company_service.get_company(db, company_id=company_id)
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


@company_router.get("/creator/me", response_model=ListSuccessResponse)
async def get_my_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    companies = company_service.get_companies_by_creator(
        db, creator_id=current_user.id, skip=skip, limit=limit
    )
    return success_response(
        status_code=status.HTTP_200_OK,
        message="User's companies retrieved successfully",
        data=companies
    )

@public_router.get(
    "/search",
    response_model=CompanySearchResponse,  # Now properly defined
)
async def search_companies(
    search_term: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    size: Optional[str] = Query(None),
    niche: Optional[str] = Query(None),
    year_founded_min: Optional[int] = Query(None),
    year_founded_max: Optional[int] = Query(None),
    sort_by: str = Query("relevance"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db),
):
    companies_rows, total_count = company_service.search_companies(
        db,
        search_term=search_term,
        country=country,
        size=size,
        niche=niche,
        year_founded_min=year_founded_min,
        year_founded_max=year_founded_max,
        sort_by=sort_by,
        page=int(page),
        per_page=int(per_page)
    )
    
    # Convert Row objects to dictionaries
    companies = []
    for row in companies_rows:
        # Convert the Row to a dict, handling the nested JSON fields
        company_dict = {
            "id": row.id,
            "name": row.name,
            "website": row.website,
            "lastFundingDate": row.lastFundingDate,
            "employees": row.employees,
            "acquisitions": row.acquisitions if row.acquisitions else 0,
            "type": row.type,
            "country": row.country,
            "logo": row.logo,
            "niche": row.niche,
            # Handle nested JSON properly
            "services": row.services if row.services else [],
            "founders": row.founders if row.founders else []
        }
        companies.append(company_dict)
    
    # Create the properly structured response
    return {
        "data": companies,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total_count,
            "total_pages": (total_count + per_page - 1) // per_page
        }
    }

@company_router.delete("/{company_id}", response_model=CompanyInDB)
async def delete_company(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    company = company_service.get_company(db, company_id=company_id)
    
    if company.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this company"
        )
    
    deleted_company = company_service.delete(db, company_id=company_id)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Company deleted successfully",
        data=deleted_company
    )