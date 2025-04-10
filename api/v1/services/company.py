from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid_extensions import uuid7

from api.v1.models.company import Company
from api.v1.schemas.company import CompanyCreate, CompanyUpdate, CompanyInDB
from api.core.base.services import Service

class CompanyService(Service):
    def create_company(self, db: Session, *, creator_id: str, company_in: CompanyCreate) -> Company:
        """Create a new company"""
        company = Company(
            id=str(uuid7()),
            creator_id=creator_id,
            **company_in.model_dump()
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        return company

    def get_company(self, db: Session, company_id: str) -> Optional[Company]:
        """Get a company by ID"""
        return db.query(Company).filter(Company.id == company_id).first()

    def get_companies(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = "active"
    ) -> List[Company]:
        """Get list of companies with optional filtering"""
        query = db.query(Company)
        if status:
            query = query.filter(Company.status == status)
        return query.offset(skip).limit(limit).all()

    def update_company(
        self, 
        db: Session,
        *,
        company: Company,
        company_in: CompanyUpdate
    ) -> Company:
        """Update a company"""
        update_data = company_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(company, field, value)
        
        db.add(company)
        db.commit()
        db.refresh(company)
        return company

    def delete_company(self, db: Session, *, company_id: str) -> Company:
        """Soft delete a company by setting status to inactive"""
        company = self.get_company(db, company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        company.status = "inactive"
        db.add(company)
        db.commit()
        return company

    def get_companies_by_creator(
        self,
        db: Session,
        creator_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Company]:
        """Get all companies created by a specific user"""
        return (
            db.query(Company)
            .filter(Company.creator_id == creator_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_companies(
        self,
        db: Session,
        *,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Company]:
        """Search companies by name or description"""
        return (
            db.query(Company)
            .filter(
                (Company.name.ilike(f"%{search_term}%")) |
                (Company.description.ilike(f"%{search_term}%"))
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
