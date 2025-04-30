from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from api.db.database import get_db
from api.v1.models import Subscription, User
from api.v1.services.subscription import subscription_service
from api.v1.services.user import user_service
from api.utils.success_response import success_response

subscription_router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

@subscription_router.get("/current")
async def get_current_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    """Get current user's subscription"""
    subscription = subscription_service.get_user_subscription(db, current_user.id)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )
    
    return success_response(
        data={
            "plan_id": subscription.plan_id,
            "plan_name": subscription.plan.name,
            "amount": subscription.plan.price,
            "interval": subscription.plan.billing_interval,
            "status": subscription.status,
            "features": subscription.plan.features,
            "next_billing_date": subscription.next_billing_date,
            "payment_history": [
                {
                    "id": payment.id,
                    "date": payment.created_at,
                    "amount": payment.amount,
                    "status": payment.status,
                    "description": f"{subscription.plan.name} Payment"
                }
                for payment in subscription.payments.order_by(
                    Subscription.created_at.desc()
                ).limit(3).all()
            ]
        }
    )

@subscription_router.post("/cancel")
async def cancel_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    """Cancel current subscription"""
    try:
        subscription = subscription_service.cancel_subscription(db, current_user.id)
        return success_response(
            message="Subscription cancelled successfully",
            data={
                "status": subscription.status,
                "ends_at": subscription.ends_at
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@subscription_router.post("/reactivate")
async def reactivate_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    """Reactivate a cancelled subscription"""
    try:
        subscription = subscription_service.reactivate_subscription(db, current_user.id)
        return success_response(
            message="Subscription reactivated successfully",
            data={
                "status": subscription.status,
                "next_billing_date": subscription.next_billing_date
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )