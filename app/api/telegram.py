import structlog
from fastapi import APIRouter, Request, Response
from telegram import Update
from app.bot_instance import bot_app

logger = structlog.get_logger(__name__)

router = APIRouter(
    prefix="/webhook/telegram",
    tags=["telegram"]
)

@router.post("")
async def telegram_webhook(request: Request):
    """
    Handle incoming Telegram updates.
    """
    try:
        data = await request.json()
        update = Update.de_json(data, bot_app.bot)
        
        # Initialize bot application if it hasn't been initialized yet
        if not bot_app._initialized:
            await bot_app.initialize()
            
        await bot_app.process_update(update)
        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Error processing telegram update: {e}", exc_info=True)
        return Response(status_code=500)
