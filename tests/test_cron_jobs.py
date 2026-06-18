import pytest
from unittest.mock import patch
from app.config import settings

@pytest.mark.asyncio
async def test_cron_daily_signals_unauthorized(async_client):
    response = await async_client.post("/cron/daily-signals")
    assert response.status_code == 401
    
    response = await async_client.post("/cron/daily-signals", headers={"x-cron-secret": "wrong"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_cron_daily_signals_authorized(async_client, mock_firebase):
    # Mock send_daily_signals
    with patch("app.api.cron.send_daily_signals") as mock_send:
        response = await async_client.post("/cron/daily-signals", headers={"x-cron-secret": settings.cron_secret})
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        mock_send.assert_called_once()

@pytest.mark.asyncio
async def test_cron_check_subscriptions_authorized(async_client, mock_firebase):
    # Mock check_subscriptions
    with patch("app.api.cron.check_subscriptions") as mock_check:
        response = await async_client.post("/cron/check-subscriptions", headers={"x-cron-secret": settings.cron_secret})
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        mock_check.assert_called_once()
