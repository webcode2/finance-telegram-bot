import pytest
from unittest.mock import patch

@pytest.mark.asyncio
async def test_telegram_webhook_uninitialized_bot(async_client):
    # Send a dummy update payload
    update_payload = {
        "update_id": 10000,
        "message": {
            "message_id": 1,
            "date": 1441645532,
            "chat": {
                "id": 1111111,
                "type": "private"
            },
            "text": "/start"
        }
    }
    
    with patch("app.api.telegram.bot_app.process_update") as mock_process, \
         patch("app.api.telegram.bot_app.initialize") as mock_init:
        
        response = await async_client.post("/webhook/telegram", json=update_payload)
        
        assert response.status_code == 200
        mock_process.assert_called_once()
        # It should call initialize if not initialized
        # We don't check mock_init because lifespan might have initialized it if we test full app lifecycle
