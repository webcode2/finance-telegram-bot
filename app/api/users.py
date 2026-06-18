from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.database.models import User
from app.telegram_bot.utils import get_or_create_user

router = APIRouter(prefix="/users", tags=["users"])

class UserRequest(BaseModel):
    telegram_id: int
    username: Optional[str] = None

@router.post("/", response_model=User)
async def create_or_get_user(req: UserRequest):
    try:
        user = await get_or_create_user(req.telegram_id, req.username)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
