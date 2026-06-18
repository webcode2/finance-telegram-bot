# FinanceBot Handoff Document

## System Overview
FinanceBot is architected using decoupled domains, preparing it for a microservices distributed environment while acting as a centralized entry point (`main.py`) for ease of deployment on Railway.

### Components:
- **FastAPI Core**: Handles incoming API requests (admin/health).
- **Telegram Bot (PTB)**: Attached to FastAPI's lifespan, running fully async.
- **APScheduler**: Attached to FastAPI's lifespan, handling daily jobs and hourly checks.
- **PostgreSQL Database**: Accessed via SQLAlchemy (asyncpg) with connection pooling and Alembic for migrations.
- **Netlify Functions**: An isolated function to handle burst traffic from Stripe Webhooks.

## Architecture Decisions & DDD
- **Blast Radius Control**: If the Netlify function goes down, the core Telegram bot stays alive.
- **Async-First**: All network operations (Telegram API, Resend, Database) are `async` or use `asyncio.to_thread()` to avoid blocking the main thread.
- **Idempotency**: Webhook events are tracked in the `webhook_events` table to prevent duplicate processing.

## Deployment Steps

### 1. Railway (Core Backend)
1. Link your GitHub repository to a new Railway project.
2. Add a PostgreSQL database service in Railway.
3. Deploy the application. Railway will use `railway.json` to configure the build (`Dockerfile`) and health checks (`/health`).
4. Apply the database migrations: Railway will run `/app/start.sh` which executes `alembic upgrade head` before starting `uvicorn`.

### 2. Netlify (Webhook Function)
1. Link your GitHub repository to a new Netlify site.
2. Netlify will use `netlify.toml` to build the `functions/` directory.
3. Provide the required Environment Variables in the Netlify dashboard.

## Transitioning from Test to Production
1. **Stripe**: Change from Test Mode to Live Mode. Update `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, and Price IDs.
2. **Telegram**: Switch the Bot Token to the live bot if you used a test bot.
3. **Resend**: Use a verified production domain for `EMAIL_FROM`.
4. **Environment Variables**: Ensure `FASTAPI_BASE_URL` in Netlify points to your live Railway domain.

## Troubleshooting Guide
- **Webhooks failing**: Check the Netlify function logs. Ensure `STRIPE_WEBHOOK_SECRET` matches the one provided by the Stripe dashboard for that specific endpoint.
- **Database Connection Issues**: If Railway restarts frequently due to `pool_size`, ensure you are not leaking connections. The code uses `AsyncSessionLocal` context managers properly, so leaks should not occur.
- **Bot Not Responding**: Check the Railway logs. Ensure `TELEGRAM_BOT_TOKEN` is correct. The bot runs concurrently via FastAPI's `@asynccontextmanager lifespan`.
