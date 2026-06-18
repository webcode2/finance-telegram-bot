from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_subscription_keyboard(plans: list) -> InlineKeyboardMarkup:
    """Returns the inline keyboard with dynamically fetched subscription plans."""
    keyboard = []
    for plan in plans:
        button_text = f"{plan['name']} - {plan['price_label']}"
        callback_data = f"plan_{plan['plan_type']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
        
    return InlineKeyboardMarkup(keyboard)

def get_profile_keyboard(is_premium: bool) -> InlineKeyboardMarkup:
    """Returns the profile keyboard based on subscription status."""
    if is_premium:
        keyboard = [
            [InlineKeyboardButton("Get Premium Signal", callback_data="signal")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("Upgrade to Premium", callback_data="upgrade")],
        ]
    return InlineKeyboardMarkup(keyboard)
