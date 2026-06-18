import structlog
from datetime import datetime, timedelta

logger = structlog.get_logger(__name__)

async def check_subscriptions(bot, db):
    """Checks for expired subscriptions and sends warnings using Firestore."""
    logger.info("Running subscription expiry checker...")
    
    now = datetime.utcnow()
    
    # 1. Expire past due subscriptions
    expired_users_query = db.collection('users').where('subscription_status', '==', 'premium').where('subscription_end_date', '<=', now).get()
    
    batch = db.batch()
    expired_count = 0
    
    for doc in expired_users_query:
        user_data = doc.to_dict()
        telegram_id = user_data.get('telegram_id')
        
        # Update in batch
        batch.update(doc.reference, {"subscription_status": "expired"})
        expired_count += 1
        
        try:
            await bot.send_message(
                chat_id=telegram_id,
                text="⚠️ Your premium subscription has expired. Use /prices to renew and regain access to premium signals."
            )
        except Exception as e:
            logger.error("Failed to send expiry message", telegram_id=telegram_id, error=str(e))
            
    if expired_count > 0:
        batch.commit()
        logger.info("Expired subscriptions", count=expired_count)
        
    # 2. Send 1-day warnings
    one_day_from_now = now + timedelta(days=1)
    window_start_1 = one_day_from_now - timedelta(minutes=30)
    window_end_1 = one_day_from_now + timedelta(minutes=30)
    
    # Firestore allows only one inequality filter per query (which must be on the same field)
    # This is fine since both are on subscription_end_date
    warning_users_1 = db.collection('users').where('subscription_status', '==', 'premium') \
                        .where('subscription_end_date', '>=', window_start_1) \
                        .where('subscription_end_date', '<=', window_end_1).get()
                        
    for doc in warning_users_1:
        user_data = doc.to_dict()
        telegram_id = user_data.get('telegram_id')
        try:
            await bot.send_message(
                chat_id=telegram_id,
                text="⏰ Reminder: Your premium subscription expires in 24 hours. Use /prices to renew."
            )
        except Exception as e:
            logger.error("Failed to send 1-day warning", telegram_id=telegram_id, error=str(e))

    # 3. Send 3-day warnings
    three_days_from_now = now + timedelta(days=3)
    window_start_3 = three_days_from_now - timedelta(minutes=30)
    window_end_3 = three_days_from_now + timedelta(minutes=30)
    
    warning_users_3 = db.collection('users').where('subscription_status', '==', 'premium') \
                        .where('subscription_end_date', '>=', window_start_3) \
                        .where('subscription_end_date', '<=', window_end_3).get()
                        
    for doc in warning_users_3:
        user_data = doc.to_dict()
        telegram_id = user_data.get('telegram_id')
        try:
            await bot.send_message(
                chat_id=telegram_id,
                text="⏰ Reminder: Your premium subscription expires in 3 days. Use /prices to renew."
            )
        except Exception as e:
            logger.error("Failed to send 3-day warning", telegram_id=telegram_id, error=str(e))
