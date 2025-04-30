from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import csv
from io import StringIO

from api.db.database import get_db
from api.v1.models import User, Company
from api.v1.services.user import user_service
from api.utils.success_response import success_response

favorites_router = APIRouter(prefix="/favorites", tags=["Favorites"])

@favorites_router.get("", response_model=List[Company])
async def get_user_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    """Get all favorite companies for current user"""
    return current_user.favorites

@favorites_router.delete("/{company_id}")
async def remove_favorite(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    """Remove a company from favorites"""
    company = next((c for c in current_user.favorites if str(c.id) == company_id), None)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found in favorites"
        )
    
    current_user.favorites.remove(company)
    db.commit()
    
    return success_response(
        message="Company removed from favorites",
        status_code=status.HTTP_200_OK
    )

@favorites_router.get("/export")
async def export_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    """Export favorites as CSV"""
    def generate_csv():
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Company Name", "Website", "Services", 
            "Niche", "Location", "Employees", 
            "Last Funding Date", "Date Saved"
        ])
        
        # Data
        for company in current_user.favorites:
            writer.writerow([
                company.name,
                company.website,
                ", ".join(company.services),
                company.niche,
                company.location,
                company.employees,
                company.last_funding_date,
                # Assuming you have a relationship attribute for when it was favorited
                company.added_at.strftime("%Y-%m-%d")  
            ])
        
        output.seek(0)
        return output.getvalue()
    
    response = StreamingResponse(
        iter([generate_csv()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=my-favorites.csv"
        }
    )
    
    return response