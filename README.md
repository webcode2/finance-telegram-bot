# FinanceBot

A production-ready Telegram finance bot with Stripe payments, a FastAPI backend, PostgreSQL database, and Netlify Functions. Built with domain-driven architecture for robust scalability and service isolation.

## Features
- **Subscription Management**: Supports Monthly, Quarterly, and Yearly plans via Stripe.
- **Premium Signals**: Delivers daily mock signals to premium subscribers.
- **Automated Expiry Checks**: Periodic worker runs to detect expired subscriptions.
- **Webhook Integration**: Stripe webhook parsed safely via Netlify Serverless Functions.
- **Invite Delivery**: Telegram invite link generation and Resend email integration.

## Local Development Setup

1. **Clone and Install**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Copy `.env.template` to `.env` and fill in your test credentials.
   ```bash
   cp .env.template .env
   ```

3. **Database Setup**
   Run the postgres container and migrations:
   ```bash
   docker-compose up -d db
   alembic upgrade head
   ```

4. **Run Locally**
   Start the FastAPI server (which automatically spawns the Telegram Bot and Scheduler in the background):
   ```bash
   uvicorn app.main:app --reload
   ```

## Architecture Notes
To adhere to microservice boundaries and domain-driven design, the project structure is strictly decoupled:
- **Telegram Bot Domain** (`app/telegram_bot`)
- **Payment Domain** (`app/stripe_service` & `functions/`)
- **Notification Domain** (`app/email_service` & `app/telegram_api`)
- **Worker Domain** (`app/scheduled_jobs`)
- **API Domain** (`app/api`)

These can be separated into their own repositories as the project scales.
