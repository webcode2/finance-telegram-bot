from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from app.config import settings
from app.telegram_bot.handlers import (
    start_command, prices_command, profile_command, signal_command,
    button_callback, plan_callback, email_input, cancel_payment, WAITING_EMAIL
)

def init_bot_app() -> Application:
    # Initialize bot application
    bot_app = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .build()
    )
    
    # Add handlers
    bot_app.add_handler(CommandHandler("start", start_command))
    bot_app.add_handler(CommandHandler("prices", prices_command))
    bot_app.add_handler(CommandHandler("profile", profile_command))
    bot_app.add_handler(CommandHandler("signal", signal_command))
    
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(plan_callback, pattern="^plan_")],
        states={
            WAITING_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email_input)]
        },
        fallbacks=[CommandHandler("cancel", cancel_payment)]
    )
    bot_app.add_handler(conv_handler)
    bot_app.add_handler(CallbackQueryHandler(button_callback))
    
    return bot_app

# Global instance
bot_app = init_bot_app()
