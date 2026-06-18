import structlog
import httpx
from app.config import settings
from app.database.models import InviteLink

logger = structlog.get_logger(__name__)

async def generate_invite_link(user_id: int, db) -> str | None:
    """Generates a single-use invite link via Telegram API and stores it in Firestore."""
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/createChatInviteLink"
    
    # 7 days in seconds
    expire_date = 604800
    
    import time
    expire_timestamp = int(time.time()) + expire_date
    
    payload = {
        "chat_id": settings.telegram_chat_id,
        "name": f"Premium Invite {user_id}",
        "expire_date": expire_timestamp,
        "member_limit": 1
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if data.get("ok"):
                invite_link_str = data["result"]["invite_link"]
                
                # Store in DB (Firestore)
                db_link = InviteLink(
                    user_id=str(user_id),
                    link=invite_link_str
                )
                link_ref = db.collection('invite_links').document()
                link_ref.set(db_link.model_dump())
                
                logger.info("Generated invite link", user_id=user_id)
                return invite_link_str
            else:
                logger.error("Failed to generate invite link", error=data.get("description"))
                return None
    except Exception as e:
        logger.error("Error communicating with Telegram API", error=str(e))
        return None
