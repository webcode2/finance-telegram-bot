import structlog
import resend
from app.config import settings

logger = structlog.get_logger(__name__)

resend.api_key = settings.resend_api_key

async def send_invite_email(to_email: str, invite_link: str):
    """Sends an invite email using Resend API."""
    if not settings.resend_api_key:
        logger.warning("Resend API key not configured. Skipping email.")
        return

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2c3e50;">Welcome to Premium!</h2>
            <p>Thank you for subscribing to our premium signals service.</p>
            <p>Please use the following single-use link to join our private Telegram channel:</p>
            <p style="margin: 20px 0;">
                <a href="{invite_link}" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Join Premium Channel</a>
            </p>
            <p>If the button doesn't work, copy and paste this link into your browser:</p>
            <p style="background: #f4f4f4; padding: 10px; border-radius: 4px; font-family: monospace;">{invite_link}</p>
            <p><small>Note: This link will expire in 7 days and can only be used once.</small></p>
        </body>
    </html>
    """
    
    try:
        # Resend SDK is synchronous, so run in thread
        import asyncio
        response = await asyncio.to_thread(
            resend.Emails.send,
            {
                "from": settings.email_from,
                "to": to_email,
                "subject": "Your Premium Telegram Invite Link",
                "html": html_content,
            }
        )
        logger.info("Sent invite email", to_email=to_email, response=str(response))
    except Exception as e:
        logger.error("Failed to send invite email", to_email=to_email, error=str(e))
