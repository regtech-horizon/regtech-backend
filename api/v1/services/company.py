from typing import List, Optional, Tuple
from sqlalchemy import func, text, bindparam, text, or_
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid_extensions import uuid7
from sqlalchemy.dialects.postgresql import JSONB
from api.v1.models.company import Company
from api.v1.schemas.company import CompanyCreate, CompanyUpdate, CompanyInDB, CompanyLogin
from api.core.base.services import Service

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
            result.append({
                "id": company.id,
                "name": company.company_name,
                "website": company.company_website,
                "services": [
                            [{"name": s["name"], "description": s["description"]}  # Map to objects
                            for s in (company.services if company.services else [])]
                        ],
                "lastFundingDate": company.last_funding_date,
                "employees": company.company_size,
                "acquisitions": 0,  # Placeholder for actual logic
                "niche": company.niche,
                "type": company.company_type,
                "location": company.country,
                "logo": company.logo,
            })
        return result, total_count
    
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
            "country": "country",
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
        
        # Handle services field - ensure it's an array
        if 'services' in update_data:
            db_update_data['services'] = update_data['services']
                
        # Handle founders field - ensure it's a proper array
        if 'founders' in update_data:
            db_update_data['founders'] = update_data['founders']
        
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
        """Search companies with pagination and filters"""
        
        # Base query
        query = db.query(
            Company.id,
            Company.company_name.label("name"),  # Alias company_name → name
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

            jsonb_condition = text("""
                jsonb_path_exists(services, :services_path) OR 
                jsonb_path_exists(founders, :founders_path)
            """).bindparams(
                bindparam('services_path', value={
                    "term": f"{search_term}",
                    "path": '$[*] ? (@.name like_regex $term || ".*" flag "i" || @.description like_regex $term || ".*" flag "i")'
                }, type_=JSONB),
                bindparam('founders_path', value={
                    "term": f"{search_term}",
                    "path": '$[*] ? (@.name like_regex $term || ".*" flag "i" || @.role like_regex $term || ".*" flag "i" || @.bio like_regex $term || ".*" flag "i")'
                }, type_=JSONB)
            )

            name_filter = Company.company_name.ilike(f"%{search_term}%")
            desc_filter = Company.description.ilike(f"%{search_term}%")
            country_filter = Company.country.ilike(f"%{search_term}%")
            
            # New service filter using JSONB path
            # service_filter = func.jsonb_path_exists(
            #     Company.services,
            #     text("""$[*] ? (
            #         @.name like_regex :term || '.*' flag "i" || 
            #         @.description like_regex :term || '.*' flag "i"
            #     )"""),  # Handles partial matches
            #     {'term': search_term}
            # )

            # founder_filter = func.jsonb_path_exists(
            #     Company.founders,
            #     text("""$[*] ? (
            #         @.name like_regex :term || '.*' flag "i" ||
            #         @.role like_regex :term || '.*' flag "i" ||
            #         @.bio like_regex :term || '.*' flag "i"
            #     )"""),
            #     {'term': search_term}
            # )
            
            query = query.filter(or_(
            name_filter,
            desc_filter,
            country_filter,
            jsonb_condition
        )
            )
        
        # Apply filters
        if country:
            countries = [country.strip() for country in country.split(",")]
            # Use OR condition for multiple countries
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
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        companies = query.offset((page - 1) * per_page).limit(per_page).all()
        
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