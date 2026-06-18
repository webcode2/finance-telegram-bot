import structlog
from fastapi import APIRouter, Header, HTTPException, Depends
from app.config import settings
from app.bot_instance import bot_app
from app.database.connection import get_db
from app.scheduled_jobs.signals import send_daily_signals
from app.scheduled_jobs.subscriptions import check_subscriptions

logger = structlog.get_logger(__name__)

router = APIRouter(
    prefix="/cron",
    tags=["cron"]
)

def verify_cron_secret(x_cron_secret: str = Header(None)):
    if x_cron_secret != settings.cron_secret:
        logger.warning("Unauthorized cron attempt", provided_secret=x_cron_secret)
        raise HTTPException(status_code=401, detail="Invalid Cron Secret")
    return True

@router.post("/daily-signals")
async def cron_daily_signals(authorized: bool = Depends(verify_cron_secret)):
    """Triggered daily to send signals."""
    logger.info("Cron endpoint hit: /daily-signals")
    try:
        db = get_db()
        await send_daily_signals(bot_app.bot, db)
        return {"status": "success", "message": "Daily signals sent"}
    except Exception as e:
        logger.error(f"Error in daily signals cron: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/check-subscriptions")
async def cron_check_subscriptions(authorized: bool = Depends(verify_cron_secret)):
    """Triggered periodically to expire and warn subscriptions."""
    logger.info("Cron endpoint hit: /check-subscriptions")
    try:
        db = get_db()
        await check_subscriptions(bot_app.bot, db)
        return {"status": "success", "message": "Subscriptions checked"}
    except Exception as e:
        logger.error(f"Error in check subscriptions cron: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
