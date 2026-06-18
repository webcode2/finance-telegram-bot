import structlog
import asyncio
from typing import Optional
from app.database.models import User, UserStatus
from app.database.connection import get_db

logger = structlog.get_logger(__name__)

async def get_or_create_user(telegram_id: int, username: Optional[str]) -> User:
    """Gets an existing user or creates a new one based on telegram_id using Firestore."""
    # Firestore Python SDK is synchronous, so we execute directly or via to_thread
    # For a low-latency telegram bot, standard sync execution is usually fine, but if we need to wrap
    # in asyncio.to_thread we can. For simplicity, we just call the SDK synchronously.
    
    db = get_db()
    user_ref = db.collection('users').document(str(telegram_id))
    doc = await asyncio.to_thread(user_ref.get)

    if doc.exists:
        data = doc.to_dict()
        user = User(**data)
        
        # Update username if it changed
        if user.username != username:
            user.username = username
            await asyncio.to_thread(user_ref.update, {"username": username})
            
        return user
    else:
        logger.info("Creating new user in Firestore", telegram_id=telegram_id)
        user = User(
            telegram_id=telegram_id,
            username=username,
            subscription_status=UserStatus.FREE
        )
        # Convert pydantic model to dict, handling datetimes (firestore handles them automatically or we can isoformat)
        # We'll use model_dump but let firestore handle dates if we just use standard dicts
        user_dict = user.model_dump()
        await asyncio.to_thread(user_ref.set, user_dict)
        return user

async def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
    """Gets a user by telegram_id from Firestore."""
    db = get_db()
    user_ref = db.collection('users').document(str(telegram_id))
    doc = await asyncio.to_thread(user_ref.get)
    
    if doc.exists:
        return User(**doc.to_dict())
    return None
