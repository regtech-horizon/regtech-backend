from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid_extensions import uuid7
import json

from api.v1.models.company import Company
from api.v1.schemas.company import CompanyCreate, CompanyUpdate, CompanyInDB, CompanyLogin
from api.core.base.services import Service

class CompanyService(Service):
    def create(self, db: Session, *, creator_id: str, company_in: CompanyCreate) -> Company:
        """Create a new company"""
        # Check if company with same email already exists
        if company_in.company_email:
            existing_company = db.query(Company).filter(
                Company.company_email == company_in.company_email
            ).first()
            if existing_company:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Company with this email already exists"
                )

        # Convert the company_in to a dictionary
        company_data = company_in.model_dump()
        
        # Create a new dictionary with only the fields we want to save
        db_company_data = {
            "creator_id": creator_id,
            "id": str(uuid7())
        }
        
        # Map fields from company_data to db_company_data
        field_mapping = {
            "company_type": "company_type",
            "company_name": "company_name", 
            "company_email": "company_email",
            "company_phone": "company_phone",
            "company_website": "company_website",
            "company_size": "company_size",
            "year_founded": "year_founded",
            "headquarters": "headquarters",
            "description": "description",
            "status": "status",
            "logo": "logo",
            "last_funding_date": "last_funding_date",
            "niche": "niche",
            "company_password": "company_password"
        }
        
        # Copy mapped fields
        for source, target in field_mapping.items():
            if source in company_data and company_data[source] is not None:
                db_company_data[target] = company_data[source]
        
        # Handle social_media field specifically
        if 'social_media' in company_data and company_data['social_media']:
            # Initialize social media fields
            social_media_linkedIn = None
            social_media_ig = None
            social_media_X = None
            
            # Map social media objects to their respective fields
            for item in company_data['social_media']:
                platform = item.get('platform', '').lower()
                url = item.get('url', '')
                
                if 'linkedin' in platform:
                    social_media_linkedIn = url
                elif 'instagram' in platform or 'ig' in platform:
                    social_media_ig = url
                elif 'x' in platform or 'twitter' in platform:
                    social_media_X = url
            
            # Add the mapped social media fields
            if social_media_linkedIn:
                db_company_data['social_media_linkedIn'] = social_media_linkedIn
            if social_media_ig:
                db_company_data['social_media_ig'] = social_media_ig
            if social_media_X:
                db_company_data['social_media_X'] = social_media_X
        
        # Handle services field - ensure it's a string
        if 'services' in company_data and company_data['services'] is not None:
            if isinstance(company_data['services'], list):
                db_company_data['services'] = ', '.join(company_data['services'])
            else:
                db_company_data['services'] = str(company_data['services'])
        
        # Handle founders field - ensure it's a proper array
        if 'founders' in company_data:
            if company_data['founders'] is None:
                db_company_data['founders'] = []
            elif isinstance(company_data['founders'], str):
                db_company_data['founders'] = [company_data['founders']]
            elif isinstance(company_data['founders'], list):
                db_company_data['founders'] = company_data['founders']
            else:
                db_company_data['founders'] = [str(company_data['founders'])]
        
        # Create the company with the processed data
        company = Company(**db_company_data)
        db.add(company)
        db.commit()
        db.refresh(company)
        return company

    def fetch(self, db: Session, *, company_login: CompanyLogin, user_id: str) -> Optional[Company]:
        """Login in"""
        company = db.query(Company).filter(Company.company_email == company_login.email,
        Company.creator_id == user_id,
        Company.company_password == company_login.password).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        return company

    def fetch_all(
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

    def update(
        self, 
        db: Session,
        *,
        company: Company,
        company_in: CompanyUpdate
    ) -> Company:
        """Update a company"""
        update_data = company_in.model_dump(exclude_unset=True)
        
        # Create a new dictionary with only the fields we want to update
        db_update_data = {}
        
        # Map fields from update_data to db_update_data
        field_mapping = {
            "name": "company_name",
            "company_type": "company_type",
            "contact_name": "company_name",  # Assuming this maps to company_name
            "email": "company_email",
            "phone": "company_phone",
            "website": "company_website",
            "company_size": "company_size",
            "year_founded": "year_founded",
            "headquarters": "headquarters",
            "description": "description",
            "logo": "logo",
            "social_media_linkedIn": "social_media_linkedIn",
            "social_media_ig": "social_media_ig",
            "social_media_X": "social_media_X",
            "status": "status"
        }
        
        # Copy mapped fields
        for source, target in field_mapping.items():
            if source in update_data and update_data[source] is not None:
                db_update_data[target] = update_data[source]
        
        # Handle social_media field specifically if it's being updated
        if 'social_media' in update_data and update_data['social_media']:
            # Initialize social media fields
            social_media_linkedIn = None
            social_media_ig = None
            social_media_X = None
            
            # Map social media objects to their respective fields
            for item in update_data['social_media']:
                platform = item.get('platform', '').lower()
                url = item.get('url', '')
                
                if 'linkedin' in platform:
                    social_media_linkedIn = url
                elif 'instagram' in platform or 'ig' in platform:
                    social_media_ig = url
                elif 'x' in platform or 'twitter' in platform:
                    social_media_X = url
            
            # Add the mapped social media fields
            if social_media_linkedIn:
                db_update_data['social_media_linkedIn'] = social_media_linkedIn
            if social_media_ig:
                db_update_data['social_media_ig'] = social_media_ig
            if social_media_X:
                db_update_data['social_media_X'] = social_media_X
        
        # Handle services field - ensure it's a string
        if 'services' in update_data and update_data['services'] is not None:
            if isinstance(update_data['services'], list):
                db_update_data['services'] = ', '.join(update_data['services'])
            else:
                db_update_data['services'] = str(update_data['services'])
        
        # Handle founders field - ensure it's a proper array
        if 'founders' in update_data:
            if update_data['founders'] is None:
                db_update_data['founders'] = []
            elif isinstance(update_data['founders'], str):
                db_update_data['founders'] = [update_data['founders']]
            elif isinstance(update_data['founders'], list):
                db_update_data['founders'] = update_data['founders']
            else:
                db_update_data['founders'] = [str(update_data['founders'])]
        
        # Update the company with the processed data
        for field, value in db_update_data.items():
            setattr(company, field, value)
        
        db.add(company)
        db.commit()
        db.refresh(company)
        return company

    def delete(self, db: Session, *, company_id: str) -> Company:
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

company_service = CompanyService()