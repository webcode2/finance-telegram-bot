from fastapi import APIRouter, Depends, HTTPException, Header
import structlog
from typing import List

from app.database.connection import get_db
from app.config import settings

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])

async def verify_admin_key(x_admin_key: str = Header(...)):
    """Verifies the admin API key."""
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    return True

@router.get("/users", dependencies=[Depends(verify_admin_key)])
async def list_users(skip: int = 0, limit: int = 100, db = Depends(get_db)):
    """Lists all users."""
    users_ref = db.collection('users').offset(skip).limit(limit).get()
    users = []
    for doc in users_ref:
        u = doc.to_dict()
        users.append({
            "telegram_id": u.get("telegram_id"),
            "username": u.get("username"),
            "status": u.get("subscription_status")
        })
    return users

@router.get("/user/{telegram_id}", dependencies=[Depends(verify_admin_key)])
async def get_user(telegram_id: str, db = Depends(get_db)):
    """Gets details for a specific user using their telegram_id."""
    doc = db.collection('users').document(telegram_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
        
    u = doc.to_dict()
    return {
        "telegram_id": u.get("telegram_id"),
        "username": u.get("username"),
        "status": u.get("subscription_status"),
        "end_date": u.get("subscription_end_date")
    }

@router.get("/stats", dependencies=[Depends(verify_admin_key)])
async def get_stats(db = Depends(get_db)):
    """Returns basic system stats."""
    
    users_col = db.collection('users')
    total_users_query = users_col.count()
    total_users_result = total_users_query.get()
    total_users = total_users_result[0][0].value
    
    premium_users_query = users_col.where('subscription_status', '==', 'premium').count()
    premium_users_result = premium_users_query.get()
    premium_users = premium_users_result[0][0].value
    
    payments = db.collection('payments').where('status', '==', 'completed').get()
    total_revenue_cents = sum(p.to_dict().get('amount', 0) for p in payments)
    
    return {
        "total_users": total_users,
        "premium_users": premium_users,
        "total_revenue_cents": total_revenue_cents
    }
