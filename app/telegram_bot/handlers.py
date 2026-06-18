import structlog
from telegram import Update
from telegram.ext import ContextTypes
from app.telegram_bot.api_client import api_get_or_create_user, api_create_checkout, api_get_plans
from app.telegram_bot.keyboards import get_subscription_keyboard, get_profile_keyboard
from telegram.ext import ConversationHandler

logger = structlog.get_logger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    user = update.effective_user
    if not user:
        return

    db_user = await api_get_or_create_user(user.id, user.username)
    
    # Provide immediate feedback if returning from Paystack
    if context.args:
        arg = context.args[0]
        if arg == "success":
            await update.message.reply_text("🎉 Payment Successful! Your transaction is currently processing in the background. You will receive your premium access shortly.")
            return
        elif arg == "cancel":
            await update.message.reply_text("❌ Payment Cancelled. You have not been charged.")
            return
            
    welcome_text = (
        "Welcome to the Upwork Demo Bot!\n\n"
        "I'm Israel, Saviour. This is a demonstration of my Telegram bot with a microservices backend, integrating payments and Firebase.\n"
        f"Your current status is: {db_user.subscription_status.upper()}\n\n"
        "Use /prices to view DEMO subscription plans.\n"
        "Use /about to learn more about my services and hire me."
    )
    
    await update.message.reply_text(welcome_text)
    logger.info("User started bot", telegram_id=user.id)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /about command."""
    text = (
        "👨‍💻 *About the Developer*\n\n"
        "I'm Saviour Israel, a backend and distributed systems architect. You can hire me for your next project!\n\n"
        "💼 *Hire Me*\n"
        "• Upwork Rate: $10/hour\n"
        "• Portfolio: [studio.elastrocloud.com](https://studio.elastrocloud.com)\n\n"
        "🔗 *Connect*\n"
        "• GitHub: [webcode2](https://github.com/webcode2)\n"
        "• LinkedIn: [Saviour Israel](https://linkedin.com/in/saviour-israel-2134631ab)\n"
        "• WhatsApp: +2348128991543\n"
        "• Email: savior@elastrocloud.com | saviorisrael@gmail.com"
    )
    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

async def prices_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /prices command."""
    user = update.effective_user
    if not user:
        return
        
    await api_get_or_create_user(user.id, user.username)
    plans = await api_get_plans()
    
    text = "Choose a subscription plan to get access to premium signals:"
    keyboard = get_subscription_keyboard(plans)
    
    await update.message.reply_text(text, reply_markup=keyboard)

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /profile command."""
    user = update.effective_user
    if not user:
        return
        
    db_user = await api_get_or_create_user(user.id, user.username)
    is_premium = db_user.subscription_status == "premium"
    
    expiry_text = f"Ends on: {db_user.subscription_end_date.strftime('%Y-%m-%d')}" if db_user.subscription_end_date else "N/A"
    
    text = (
        "👤 *Your Profile*\n\n"
        f"ID: `{db_user.telegram_id}`\n"
        f"Status: *{db_user.subscription_status.upper()}*\n"
        f"Premium Expiry: {expiry_text}\n"
    )
    
    keyboard = get_profile_keyboard(is_premium)
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /signal command."""
    user = update.effective_user
    if not user:
        return
        
    db_user = await api_get_or_create_user(user.id, user.username)
    
    if db_user.subscription_status != "premium":
        await update.message.reply_text(
            "⚠️ This command is for premium users only.\n"
            "Use /prices to upgrade your subscription."
        )
        return
        
    mock_signal = (
        "📈 *PREMIUM SIGNAL*\n\n"
        "Asset: BTC/USD\n"
        "Action: BUY\n"
        "Entry: $65,000 - $66,000\n"
        "Target 1: $68,000\n"
        "Target 2: $71,000\n"
        "Stop Loss: $63,000\n"
        "Confidence: High\n\n"
        "Source: Mock Data"
    )
    
    await update.message.reply_text(mock_signal, parse_mode="Markdown")

WAITING_EMAIL = 1

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles all button clicks except plans (handled in plan_callback)."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
            
    if data == "signal":
        await signal_command(update, context) # Re-use command logic
        
    elif data == "upgrade":
        await prices_command(update, context) # Re-use command logic

async def plan_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles plan selection and prompts for email."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    # plan_type is the Paystack plan code, which contains underscores (e.g., PLN_xxxx)
    plan_type = data.split("_", 1)[1]
    context.user_data['plan_type'] = plan_type
    
    await query.edit_message_text(f"Please reply with your email address to proceed with the {plan_type} subscription:")
    return WAITING_EMAIL

import re

async def email_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receives email and generates Paystack link."""
    user = update.effective_user
    email = update.message.text.strip()
    plan_type = context.user_data.get('plan_type')
    
    logger.info("Received email input for checkout", email=email, plan_type=plan_type, telegram_id=user.id)
    
    if not plan_type:
        await update.message.reply_text("Please select a plan first using /prices.")
        return ConversationHandler.END

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        await update.message.reply_text("⚠️ That doesn't look like a valid email address. Please try again by typing a valid email:")
        return WAITING_EMAIL

    try:
        checkout_url = await api_create_checkout(user.id, plan_type, email)
        await update.message.reply_text(f"Click the link below to pay for your {plan_type} subscription:\n{checkout_url}")
    except Exception as e:
        logger.error("Failed to create checkout session via API", error=str(e))
        await update.message.reply_text("Sorry, an error occurred while generating your payment link. Please make sure you are using a valid plan and email.")
        
    return ConversationHandler.END

async def cancel_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels the payment flow."""
    await update.message.reply_text("Payment cancelled.")
    return ConversationHandler.END
