from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    telegram_bot_token: str
    telegram_chat_id: int
    paystack_secret_key: str
    paystack_public_key: str
    paystack_hourly_plan_code: str
    paystack_monthly_plan_code: str
    paystack_quarterly_plan_code: str
    paystack_yearly_plan_code: str
    paystack_success_url: str
    paystack_cancel_url: str
    resend_api_key: str
    email_from: str
    admin_telegram_ids: List[int]
    admin_api_key: str = "default_unsafe_key"
    
    # Webhook and Cron Configuration
    webhook_url: Optional[str] = None
    cron_secret: str = "default_unsafe_secret"

    # Rate Limiting
    rate_limit_calls: int = 5
    rate_limit_period: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
