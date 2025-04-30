from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from api.v1.models import Subscription, SubscriptionPlan

class SubscriptionService:
    
    def get_user_subscription(self, db: Session, user_id: str) -> Optional[Subscription]:
        """Get active user subscription"""
        return db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status.in_(["active", "cancelled"])
        ).order_by(Subscription.created_at.desc()).first()

    def cancel_subscription(self, db: Session, user_id: str) -> Subscription:
        """Cancel a subscription"""
        subscription = self.get_user_subscription(db, user_id)
        
        if not subscription:
            raise ValueError("No active subscription found")
            
        if subscription.status == "cancelled":
            raise ValueError("Subscription already cancelled")
            
        subscription.status = "cancelled"
        subscription.ends_at = subscription.next_billing_date
        
        db.commit()
        db.refresh(subscription)
        
        # TODO: Integrate with payment provider webhook
        return subscription

    def reactivate_subscription(self, db: Session, user_id: str) -> Subscription:
        """Reactivate a cancelled subscription"""
        subscription = self.get_user_subscription(db, user_id)
        
        if not subscription:
            raise ValueError("No subscription found")
            
        if subscription.status != "cancelled":
            raise ValueError("Only cancelled subscriptions can be reactivated")
            
        subscription.status = "active"
        subscription.ends_at = None
        
        # Calculate next billing date
        if subscription.next_billing_date < datetime.now():
            interval = subscription.plan.billing_interval
            if interval == "month":
                subscription.next_billing_date = datetime.now() + timedelta(days=30)
            else:  # year
                subscription.next_billing_date = datetime.now() + timedelta(days=365)
        
        db.commit()
        db.refresh(subscription)
        
        # TODO: Integrate with payment provider
        return subscription

subscription_service = SubscriptionService()