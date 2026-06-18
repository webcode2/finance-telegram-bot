from fastapi import APIRouter, Request, Depends, HTTPException
import structlog
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from app.database.connection import get_db
from app.database.models import User, UserStatus, Subscription, SubscriptionPlan, Payment, PaymentStatus, WebhookEvent
from app.paystack_service.webhook import verify_webhook_signature, parse_charge_success
from app.telegram_api.invite_links import generate_invite_link
from app.email_service.resend import send_invite_email

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/webhook", tags=["webhooks"])

@router.post("/paystack")
async def paystack_webhook(request: Request, db = Depends(get_db)):
    """Receives Paystack webhooks (alternative to Google Cloud function or called by it)"""
    event = await verify_webhook_signature(request)
    
    # Idempotency check
    event_id = str(event.get('data', {}).get('reference') or event.get('id'))
    
    event_ref = db.collection('webhook_events').document(event_id)
    if event_ref.get().exists:
        logger.info("Webhook already processed", event_id=event_id)
        return {"status": "already_processed"}
        
    if event.get('event') == 'charge.success':
        data = await parse_charge_success(event)
        if data and data.get("telegram_id") and data.get("plan_type"):
            await process_successful_payment(data, db)
            
    # Record event
    webhook_event = WebhookEvent(id=event_id)
    event_ref.set(webhook_event.model_dump())
    
    return {"status": "success"}

async def process_successful_payment(data: dict, db):
    """Handles the business logic after a successful payment using Firestore."""
    telegram_id = str(data["telegram_id"])
    plan_type = data["plan_type"]
    session_id = data["session_id"]
    amount = data["amount_total"]
    email = data["customer_email"]
    
    logger.info("Processing successful payment", telegram_id=telegram_id, plan_type=plan_type)
    
    # 1. Get user
    user_ref = db.collection('users').document(telegram_id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        logger.error("User not found for payment", telegram_id=telegram_id)
        return
        
    interval = data.get("interval", "monthly")
    
    start_date = datetime.utcnow()
    if interval == "hourly":
        end_date = start_date + timedelta(hours=1)
    elif interval == "weekly":
        end_date = start_date + relativedelta(weeks=1)
    elif interval == "monthly":
        end_date = start_date + relativedelta(months=1)
    elif interval == "quarterly" or interval == "quaterly":
        end_date = start_date + relativedelta(months=3)
    elif interval == "biannually":
        end_date = start_date + relativedelta(months=6)
    elif interval == "annually" or interval == "yearly":
        end_date = start_date + relativedelta(years=1)
    else:
        # Default to 30 days if unrecognized
        end_date = start_date + timedelta(days=30)
        
    # We use a batch write to ensure all related docs are created together
    batch = db.batch()
    
    # Update User
    batch.update(user_ref, {
        "subscription_status": UserStatus.PREMIUM.value,
        "subscription_end_date": end_date
    })
    
    # 2. Record payment
    payment_ref = db.collection('payments').document(session_id)
    payment = Payment(
        user_id=telegram_id,
        paystack_reference=session_id,
        amount=amount,
        status=PaymentStatus.COMPLETED
    )
    batch.set(payment_ref, payment.model_dump())
    
    # 3. Record subscription
    sub_ref = db.collection('subscriptions').document()
    subscription = Subscription(
        user_id=telegram_id,
        plan_type=SubscriptionPlan(plan_type),
        start_date=start_date,
        end_date=end_date
    )
    batch.set(sub_ref, subscription.model_dump())
    
    # Commit batch
    batch.commit()
    
    # 4. Generate invite link and send email (if provided)
    invite_link = await generate_invite_link(int(telegram_id), db)
    
    if email and invite_link:
        await send_invite_email(email, invite_link)
