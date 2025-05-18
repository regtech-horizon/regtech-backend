from typing import List, Optional, Tuple
from sqlalchemy import func, text, or_
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid_extensions import uuid7
import json
from api.v1.models.company import Company
from api.v1.schemas.company import CompanyCreate, CompanyUpdate, CompanyInDB, CompanyLogin
from api.core.base.services import Service
from api.v1.services.user import user_service
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Outputs to console
    ]
)

logger = logging.getLogger(__name__)

DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 10  # We had used 10 items per page
MAX_PER_PAGE = 100

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
            "company_password": "company_password",
            "country": "country"
        }
        
        # Copy mapped fields
        for source, target in field_mapping.items():
            if source in company_data and company_data[source] is not None:
                if source == "company_password":
                    db_company_data[target] = user_service.hash_password(company_data[source])
                else:
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
        
        # Handle services field - ensure it's an array
        if 'services' in company_data:
            db_company_data['services'] = company_data['services']

        # Handle founders field - ensure it's a proper array
        if 'founders' in company_data:
            db_company_data['founders'] = company_data['founders']
        
        # Create the company with the processed data
        company = Company(**db_company_data)
        db.add(company)
        db.commit()
        db.refresh(company)
        return company

    def fetch(self, db: Session, *, company_login: CompanyLogin, user_id: str) -> Optional[Company]:
        """Login in"""
        company = db.query(Company).filter(Company.company_email == company_login.email,
        Company.creator_id == user_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        if not user_service.verify_password(company_login.password, company.company_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )
        return company

    def fetch_all(
        self, 
        db: Session, 
        *, 
        status: Optional[str] = "active",
        page: int = DEFAULT_PAGE,
        per_page: int = DEFAULT_PER_PAGE
    ) -> Tuple[List[dict], int]:
        """Get paginated and filtered list of companies."""
        # Create the base query
        base_query = db.query(Company)
        if status:
            base_query = base_query.filter(Company.status == status)
        
        # Get total count before pagination
        total_count = base_query.count()
        
        # Apply pagination to get the results
        companies = base_query.offset((page - 1) * per_page).limit(per_page).all()
        
        result = []
        for company in companies:
            # Create properly formatted services array - remove the extra nesting
            services_array = [
                {"name": s["name"], "description": s["description"]}
                for s in (company.services if company.services else [])
            ]

            result.append({
                "id": company.id,
                "name": company.company_name,
                "website": company.company_website,
                "services": services_array,  # Use the properly formatted array
                "lastFundingDate": company.last_funding_date,
                "description": company.description,
                "headquarters": company.headquarters,
                "year_founded": company.year_founded,
                "employees": company.company_size,
                "acquisitions": 0,  # Placeholder for actual logic
                "niche": company.niche,
                "type": company.company_type,
                "location": company.country,
                "logo": company.logo,
            })
        return result, total_count
    
    def update(self, db: Session, *, company: Company, company_in: CompanyUpdate) -> Company:
        try:
            update_data = company_in.model_dump(exclude_unset=True)
            
            # Update direct fields
            for field, value in update_data.items():
                if hasattr(company, field) and value is not None:
                    setattr(company, field, value)
            
            # Handle special cases
            if 'services' in update_data:
                company.services = update_data['services'] or []
                
            if 'founders' in update_data:
                company.founders = update_data['founders'] or []
                
            db.add(company)
            db.commit()
            db.refresh(company)
            
            return company
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update company: {str(e)}"
            )

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
        search_term: Optional[str] = None,
        country: Optional[str] = None,
        size: Optional[str] = None,
        niche: Optional[str] = None,
        year_founded_min: Optional[int] = None,
        year_founded_max: Optional[int] = None,
        sort_by: str = "relevance",
        page: int = DEFAULT_PAGE,
        per_page: int = DEFAULT_PER_PAGE
    ) -> Tuple[List[Company], int]:
        """Search companies with pagination and filters with safe JSON array handling"""
        
        # Base query
        query = db.query(
            Company.id,
            Company.company_name.label("name"),
            Company.company_website.label("website"),
            Company.last_funding_date.label("lastFundingDate"),
            Company.company_size.label("employees"),
            Company.acquisitions,
            Company.company_type.label("type"),
            Company.country,
            Company.logo,
            Company.niche,
            Company.services,
            Company.founders
        ).filter((Company.status == "active") | (Company.status == "completed"))
        
        # Text search
        if search_term:
            name_filter = Company.company_name.ilike(f"%{search_term}%")
            desc_filter = Company.description.ilike(f"%{search_term}%")
            country_filter = Company.country.ilike(f"%{search_term}%")
            niche_filter = Company.niche.ilike(f"%{search_term}%")
            
            # Safe array access using EXISTS with array_elements and type checking
            services_filter = text("""
                jsonb_typeof(services) = 'array' AND
                EXISTS (
                    SELECT 1 FROM jsonb_array_elements(services) AS service
                    WHERE 
                        service->>'name' ILIKE :search_term OR
                        service->>'description' ILIKE :search_term
                )
            """).bindparams(search_term=f"%{search_term}%")
            
            founders_filter = text("""
                jsonb_typeof(founders) = 'array' AND
                EXISTS (
                    SELECT 1 FROM jsonb_array_elements(founders) AS founder
                    WHERE 
                        founder->>'name' ILIKE :search_term OR
                        founder->>'role' ILIKE :search_term OR
                        founder->>'bio' ILIKE :search_term
                )
            """).bindparams(search_term=f"%{search_term}%")
            
            query = query.filter(or_(
                name_filter,
                desc_filter,
                country_filter,
                niche_filter,
                services_filter,
                founders_filter
            ))
        
        # Apply filters
        if country:
            countries = [country.strip() for country in country.split(",")]
            country_filters = [Company.country.ilike(f"%{c}%") for c in countries]
            query = query.filter(or_(*country_filters))
        
        if size:
            sizes = [size.strip() for size in size.split(",")]
            size_filters = [Company.company_size == s for s in sizes]
            query = query.filter(or_(*size_filters))
        
        if niche:
            niches = [n.strip() for n in niche.split(",")]
            niche_filters = [Company.niche == n for n in niches]
            query = query.filter(or_(*niche_filters))
        
        if year_founded_min:
            query = query.filter(Company.year_founded >= year_founded_min)
        
        if year_founded_max:
            query = query.filter(Company.year_founded <= year_founded_max)
        
        # Apply sorting
        if sort_by == "name":
            query = query.order_by(Company.company_name)
        elif sort_by == "founded":
            query = query.order_by(Company.year_founded.desc())
        elif sort_by == "employees":
            query = query.order_by(Company.company_size.desc())
        else:  # relevance
            query = query.order_by(Company.created_at.desc())
        
        # Get total count before pagination - Using a safer approach to count
        try:
            subquery = query.subquery()
            total_count = db.query(func.count()).select_from(subquery).scalar()
        except Exception as e:
            logger.error(f"Error counting results: {str(e)}")
            total_count = 0
        
        # Apply pagination
        try:
            companies = query.offset((page - 1) * per_page).limit(per_page).all()
        except Exception as e:
            logger.error(f"Error fetching companies: {str(e)}")
            companies = []
        
        return companies, total_count
    
    def get_company(self, db: Session, *, company_id: str) -> Company:
        """Get a company by ID."""
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        return company

company_service = CompanyService()

def change_password(
    self,
    db: Session,
    company: Company,
    current_password: str,
    new_password: str
):
    """
    Change company password
    
    Args:
        db: Database session
        company: Company object
        current_password: Current password
        new_password: New password to set
        
    Raises:
        HTTPException: If the current password is incorrect
        HTTPException: If the new password is the same as the current password
    """
    # Verify current password matches
    if company.company_password != current_password:
        raise HTTPException(
            status_code=400, 
            detail="Incorrect current password"
        )
    
    # Check if new password is different from current
    if current_password == new_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Current Password and New Password cannot be the same"
        )
    
    # Update password
    company.company_password = new_password
    db.commit()
    db.refresh(company)