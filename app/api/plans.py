from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import httpx
from app.config import settings
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/plans", tags=["plans"])

class SubscriptionPlanInfo(BaseModel):
    name: str
    price_label: str
    plan_type: str

@router.get("/", response_model=List[SubscriptionPlanInfo])
async def get_plans():
    url = "https://api.paystack.co/plan"
    headers = {
        "Authorization": f"Bearer {settings.paystack_secret_key}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
            plans = []
            if data.get("status") and data.get("data"):
                for plan in data["data"]:
                    amount_in_naira = plan.get("amount", 0) / 100
                    plans.append(
                        SubscriptionPlanInfo(
                            name=plan.get("name", "Unknown Plan"),
                            price_label=f"₦{amount_in_naira:,.2f}",
                            plan_type=plan.get("plan_code", "")
                        )
                    )
            return plans
    except Exception as e:
        logger.error("Failed to fetch plans from Paystack", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch subscription plans")

