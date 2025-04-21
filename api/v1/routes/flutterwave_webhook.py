# api/v1/routes/webhooks.py

from fastapi import APIRouter, Request, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.db.database import get_db
from api.v1.models import Payment, Subscription
from datetime import datetime, timedelta, timezone
import hmac
import hashlib
import httpx
import os

router = APIRouter()
FLUTTERWAVE_SECRET_KEY = os.getenv("FLW_SECRET_KEY")  # Store this securely
FLUTTERWAVE_WEBHOOK_HASH = os.getenv("FLW_WEBHOOK_HASH")

@router.post("/webhook/flutterwave", status_code=status.HTTP_200_OK)
async def flutterwave_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    received_hash = request.headers.get("verif-hash")
    if FLUTTERWAVE_WEBHOOK_HASH and received_hash != FLUTTERWAVE_WEBHOOK_HASH:
        raise HTTPException(status_code=403, detail="Invalid webhook hash")

    payload = await request.json()
    
    event = payload.get("event")
    data = payload.get("data", {})

    if event != "charge.completed":
        return {"message": "Ignored non-payment event"}

    # STEP 1: Extract transaction_id
    transaction_id = data.get("id")
    if not transaction_id:
        raise HTTPException(status_code=400, detail="Transaction ID not found")

    # STEP 2: Verify payment with Flutterwave
    async with httpx.AsyncClient() as client:
        verify_url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
        headers = {
            "Authorization": f"Bearer {FLUTTERWAVE_SECRET_KEY}"
        }
        response = await client.get(verify_url, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to verify transaction")

        verification_data = response.json().get("data")

    # STEP 3: Use tx_ref to find the subscription
    subscription_id = verification_data.get("tx_ref")
    subscription = await db.get(Subscription, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # STEP 4: Create a new Payment
    payment = Payment(
        subscription_id=subscription.id,
        amount=float(verification_data["amount"]),
        payment_date=datetime.now(timezone.utc),
        payment_method=verification_data["payment_type"],
        status="successful",
        invoice_url=verification_data.get("meta", {}).get("invoice_url", None)
    )
    db.add(payment)

    # STEP 5: Update subscription status/duration
    if subscription.status != "active":
        subscription.status = "active"

    # Extend subscription period
    if subscription.billing_cycle == "monthly":
        subscription.end_date += timedelta(days=30)
    elif subscription.billing_cycle == "yearly":
        subscription.end_date += timedelta(days=365)

    await db.commit()
    return {"message": "Payment verified and subscription updated"}
