import structlog
import httpx
from app.config import settings

logger = structlog.get_logger(__name__)

async def create_checkout_session(telegram_id: int, plan_type: str, email: str) -> str:
    """Creates a Paystack checkout session and returns the authorization URL."""
    # plan_type is now directly the Paystack plan_code (e.g. PLN_xxxx)
    plan_code = plan_type
    
    if not plan_code.startswith("PLN_"):
        raise ValueError(f"Invalid plan code: {plan_code}")

    url_plan = f"https://api.paystack.co/plan/{plan_code}"
    url_init = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.paystack_secret_key}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # First, fetch the exact amount of the plan from Paystack
            plan_response = await client.get(url_plan, headers=headers)
            plan_response.raise_for_status()
            plan_data = plan_response.json()
            if not plan_data.get("status"):
                raise ValueError("Failed to retrieve plan details from Paystack")
            
            amount = plan_data["data"]["amount"]

            # Initialize checkout session with the retrieved amount
            payload = {
                "email": email,
                "amount": amount,
                "plan": plan_code,
                "callback_url": settings.paystack_success_url,
                "metadata": {
                    "telegram_id": str(telegram_id),
                    "plan_type": plan_type,
                    "cancel_action": settings.paystack_cancel_url
                }
            }
            
            response = await client.post(url_init, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status"):
                auth_url = data["data"]["authorization_url"]
                logger.info("Checkout session created", telegram_id=telegram_id, plan_type=plan_type)
                return auth_url
            else:
                raise ValueError(f"Paystack error: {data.get('message')}")
    except httpx.HTTPStatusError as e:
        error_body = e.response.text if hasattr(e, 'response') else str(e)
        logger.error("HTTP Error creating checkout session", error=error_body, telegram_id=telegram_id)
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error("Error creating checkout session", error=repr(e), traceback=error_trace, telegram_id=telegram_id)
        raise
