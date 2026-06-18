# Migration Roadmap: Distributed Decomposition (Monolith -> Microservices)

- [x] Boundary 1: API Layer Isolation
  - Extract FastAPI application from `app/main.py` into `app/api.py`.
  - Ensure REST routing (`/health`, `/admin`, `/webhook`) functions identically without Telegram loop.
- [x] Boundary 2: Bot Core Isolation
  - Extract Telegram polling logic into `app/bot.py`.
  - Verify all CommandHandlers and ConversationHandlers are cleanly imported.
- [x] Boundary 3: Background Job Isolation
  - Extract `AsyncIOScheduler` into `app/worker.py`.
  - Instantiate headless Telegram bot instance to ensure outbound broadcast capability without incoming polling.
- [x] Boundary 4: Cleanup
  - Terminate the legacy `app/main.py` monolith.
