import httpx
from typing import Optional
import structlog
from datetime import datetime
from pydantic import BaseModel

logger = structlog.get_logger(__name__)

import os
port = os.getenv("PORT", "8000")
API_BASE_URL = f"http://127.0.0.1:{port}"

# Minimal User model for bot to consume without importing DB models
class BotUser(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    subscription_status: str
    subscription_end_date: Optional[datetime] = None

async def api_get_or_create_user(telegram_id: int, username: Optional[str]) -> BotUser:
    """Fetches user details from the backend API instead of hitting DB directly."""
    url = f"{API_BASE_URL}/users/"
    payload = {"telegram_id": telegram_id, "username": username}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        return BotUser(**data)

async def api_create_checkout(telegram_id: int, plan_type: str, email: str) -> str:
    """Initializes checkout session via backend API."""
    url = f"{API_BASE_URL}/checkout/"
    payload = {
        "telegram_id": telegram_id,
        "plan_type": plan_type,
        "email": email
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        return data["url"]

async def api_get_plans() -> list:
    """Fetches the available subscription plans from the backend API."""
    url = f"{API_BASE_URL}/plans/"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=30.0)
        response.raise_for_status()
        return response.json()

