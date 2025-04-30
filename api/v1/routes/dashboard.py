from fastapi import APIRouter, Depends, HTTPException, status

import logging
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User, Company, ActivityLog, Notification
from api.utils.success_response import success_response
from api.v1.routes.user import user_router

dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
# dashboard_router = user_router

@dashboard_router.get("", status_code=200)
async def get_dashboard_data(

    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    """
    Get dashboard overview data for the current user
    """
    try:
        # Get basic statistics
        stats = {
            "savedSearches": 12,  # Replace with actual query
            "favorites": 8,        # Replace with actual query
            "newsletters": 3,      # Replace with actual query
            "activities": 15,      # Replace with actual query
            
            "companies": db.query(Company).filter(Company.creator_id == current_user.id).count()
        }
        
        # Get recent activities (last 15)
        # activities = db.query(ActivityLog)\
        #     .filter(ActivityLog.u == current_user.id)\
        #     .order_by(ActivityLog.created_at.desc())\
        #     .limit(15)\
        #     .all()
        
        # formatted_activities = [
        #     {
        #         "id": str(act.id),
        #         "type": act.activity_type,
        #         "title": act.title,
        #         "description": act.description,
        #         "timestamp": act.created_at.strftime("%b %d, %Y at %I:%M %p"),
        #         "read": act.read
        #     }
        #     for act in activities
        # ]
        
        # Get notifications (last 15)
        notifications = db.query(Notification)\
            .filter(Notification.user_id == current_user.id)\
            .order_by(Notification.created_at.desc())\
            .limit(15)\
            .all()
        
        formatted_notifications = [
            {
                "id": str(notif.id),
                "title": notif.title,
                "message": notif.message,
                "timestamp": notif.created_at.strftime("%b %d, %Y at %I:%M %p"),
                "read": notif.is_read
            }
            for notif in notifications
        ]
        
        # Get user's companies
        companies = db.query(Company)\
            .filter(Company.creator_id == current_user.id)\
            .order_by(Company.updated_at.desc())\
            .all()
        
        formatted_companies = [
            {
                "id": str(comp.id),
                "name": comp.company_name,
                "niche": comp.niche or "Not specified",
                "lastUpdated": comp.updated_at.strftime("%b %d, %Y"),
                "status": "active"  # Replace with actual status logic
            }
            for comp in companies
        ]
        
        return success_response(
            status_code=200,
            message="Dashboard data retrieved successfully",
            data={
                "stats": stats,
                # "recentActivities": formatted_activities,
                "notifications": formatted_notifications,
                "companies": formatted_companies
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving dashboard data: {str(e)}"
        )

# @dashboard_router.get("", status_code=status.HTTP_200_OK)
# async def get_dashboard_data(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(user_service.get_current_user)
# ):
#     """
#     Get dashboard overview data for the current user
#     """
#     # Basic, guaranteed-to-work implementation
#     return success_response(
#         status_code=200,
#         message="Dashboard data retrieved successfully",
#         data={
#             "stats": {
#                 "savedSearches": 0,
#                 "favorites": 0,
#                 "newsletters": 0,
#                 "activities": 0,
#                 "companies": 0
#             },
#             "recentActivities": [],
#             "notifications": [],
#             "companies": []
#         }
#     )

# @dashboard_router.post("", status_code=status.HTTP_200_OK, dependencies=[])
# async def get_dashboard_data_test():
#     """
#     Get dashboard overview data for the current user
#     """
#     # Basic, guaranteed-to-work implementation
#     return success_response(
#         status_code=200,
#         message="Dashboard data retrieved successfully",
#         data={
#             "stats": {
#                 "savedSearches": 0,
#                 "favorites": 0,
#                 "newsletters": 0,
#                 "activities": 0,
#                 "companies": 0
#             },
#             "recentActivities": [],
#             "notifications": [],
#             "companies": []
#         }
#     )
