import structlog
from datetime import datetime

logger = structlog.get_logger(__name__)

async def send_daily_signals(bot, db):
    """Sends the daily signal to all premium users."""
    logger.info("Running daily signal job...")
    
    # Get all premium users from Firestore
    users_ref = db.collection('users').where('subscription_status', '==', 'premium').get()
    
    signal_text = (
        "📈 *DAILY PREMIUM SIGNAL*\n\n"
        "Asset: ETH/USD\n"
        "Action: BUY\n"
        "Entry: $3,500 - $3,550\n"
        "Target: $3,800\n"
        "Stop Loss: $3,350\n"
        "Confidence: High\n\n"
        "_This is an automated daily signal._\n"
        "Source: Mock Data"
    )
    
    for doc in users_ref:
        user_data = doc.to_dict()
        telegram_id = user_data.get('telegram_id')
        if not telegram_id: continue
        
        try:
            await bot.send_message(
                chat_id=telegram_id,
                text=signal_text,
                parse_mode="Markdown"
            )
            logger.info("Sent daily signal", telegram_id=telegram_id)
        except Exception as e:
            logger.error("Failed to send daily signal", telegram_id=telegram_id, error=str(e))
