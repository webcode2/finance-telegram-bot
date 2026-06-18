import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import health, admin, webhook, users, checkout, plans, telegram, cron
from app.config import settings
from app.bot_instance import bot_app

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer() # Use JSONRenderer for prod
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API Application starting up")
    
    # Initialize and start the Telegram Bot application
    await bot_app.initialize()
    await bot_app.start()
    
    # Register webhook if configured
    if settings.webhook_url:
        telegram_webhook_url = f"{settings.webhook_url.rstrip('/')}/webhook/telegram"
        await bot_app.bot.set_webhook(url=telegram_webhook_url)
        logger.info(f"Registered Telegram Webhook: {telegram_webhook_url}")
    else:
        logger.warning("WEBHOOK_URL not set. Telegram Webhook will not be registered automatically.")
        
    yield
    
    logger.info("API Application shutting down")
    # Stop the Telegram Bot application
    await bot_app.stop()
    await bot_app.shutdown()

app = FastAPI(
    title="FinanceBot API",
    description="Backend API for the Finance Telegram Bot",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to Netlify domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router)
app.include_router(webhook.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(checkout.router)
app.include_router(plans.router)
app.include_router(telegram.router)
app.include_router(cron.router)

@app.middleware("http")
async def structlog_middleware(request: Request, call_next):
    log = logger.bind(
        method=request.method,
        url=str(request.url),
        client=request.client.host if request.client else None
    )
    log.info("Request started")
    response = await call_next(request)
    log.info("Request completed", status_code=response.status_code)
    return response
