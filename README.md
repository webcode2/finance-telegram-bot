# FinanceBot

A production-ready Telegram finance bot with Paystack payments, a FastAPI backend, and Google Cloud Firestore. Built with domain-driven architecture for robust scalability and service isolation.

## Features
- **Subscription Management**: Supports multiple plans (Monthly, Quarterly, Yearly) via Paystack.
- **Premium Signals**: Delivers premium signals to subscribers.
- **Automated Expiry Checks**: Periodic worker runs to detect expired subscriptions.
- **Webhook Integration**: Securely parses and processes Paystack webhooks.
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

3. **Run Locally**
   Start the FastAPI server (which automatically spawns the Telegram Bot and Scheduler in the background):
   ```bash
   uvicorn main:app --reload
   ```

## Google Cloud Hosting (Cloud Run)

Follow these steps to deploy the bot to Google Cloud Run:

1. **Enable Firestore API**
   Enable the Firestore API for your Google Cloud Project:
   ```bash
   gcloud services enable firestore.googleapis.com --project=YOUR_PROJECT_ID
   ```

2. **Create Firestore Database**
   Initialize the default Firestore Native database in your chosen region (e.g., `us-central1`):
   ```bash
   gcloud firestore databases create --project=YOUR_PROJECT_ID --location=us-central1
   ```

3. **Deploy to Cloud Run**
   Cloud Run will automatically build the container from source using the `Procfile` and deploy it. Make sure your `.env` variables are properly configured or injected via Google Cloud Secret Manager / Environment Variables.
   ```bash
   gcloud run deploy finance-bot \
     --source . \
     --region=us-central1 \
     --project=YOUR_PROJECT_ID
   ```

4. **Update Webhooks**
   After deployment, copy the provided Cloud Run URL and set it as your webhook in the Paystack Dashboard:
   `https://<YOUR-CLOUD-RUN-URL>/webhook/paystack`

## Architecture Notes
To adhere to microservice boundaries and domain-driven design, the project structure is decoupled:
- **Telegram Bot Domain** (`app/telegram_bot`)
- **Payment Domain** (`app/paystack_service`)
- **Notification Domain** (`app/email_service` & `app/telegram_api`)
- **Worker Domain** (`app/scheduled_jobs`)
- **API Domain** (`app/api`)

These can be separated into their own microservices as the project scales.
