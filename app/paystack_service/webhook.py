import hmac
import hashlib
from fastapi import Request, HTTPException
import structlog
from app.config import settings

logger = structlog.get_logger(__name__)

async def verify_webhook_signature(request: Request) -> dict:
    """Verifies the Paystack webhook signature and returns the event payload."""
    sig_header = request.headers.get("x-paystack-signature")
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing signature")

    body = await request.body()
    secret = settings.paystack_secret_key.encode("utf-8")
    
    hash_value = hmac.new(secret, body, hashlib.sha512).hexdigest()
    
    if hash_value != sig_header:
        logger.error("Invalid webhook signature")
        raise HTTPException(status_code=400, detail="Invalid signature")
        
    try:
        payload = await request.json()
        return payload
    except Exception as e:
        logger.error("Error parsing webhook JSON", error=str(e))
        raise HTTPException(status_code=400, detail="Invalid JSON")

async def parse_charge_success(event: dict):
    """Extracts relevant details from a Paystack charge.success event."""
    if event.get("event") != "charge.success":
        return None
        
    data = event.get("data", {})
    metadata = data.get("metadata", {})
    custom_fields = metadata.get("custom_fields", [])
    
    # Sometimes metadata is direct, sometimes inside custom_fields
    telegram_id = metadata.get("telegram_id")
    plan_type = metadata.get("plan_type")
    
    if not telegram_id and custom_fields:
        for field in custom_fields:
            if field.get("variable_name") == "telegram_id":
                telegram_id = field.get("value")
            if field.get("variable_name") == "plan_type":
                plan_type = field.get("value")

    customer = data.get("customer", {})
    plan_obj = data.get("plan", {})
    
    return {
        "telegram_id": int(telegram_id) if telegram_id else None,
        "plan_type": plan_type,
        "session_id": data.get("reference"),
        "amount_total": data.get("amount"),
        "customer_email": customer.get("email"),
        "interval": plan_obj.get("interval", "monthly")
    }
