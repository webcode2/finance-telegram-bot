from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.paystack_service.checkout import create_checkout_session

router = APIRouter(prefix="/checkout", tags=["checkout"])

class CheckoutRequest(BaseModel):
    telegram_id: int
    plan_type: str
    email: str

class CheckoutResponse(BaseModel):
    url: str

@router.post("/", response_model=CheckoutResponse)
async def api_create_checkout(req: CheckoutRequest):
    try:
        url = await create_checkout_session(req.telegram_id, req.plan_type, req.email)
        return CheckoutResponse(url=url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
