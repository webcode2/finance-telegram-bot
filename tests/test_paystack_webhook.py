import pytest
from unittest.mock import patch, MagicMock
from app.main import app
from app.database.connection import get_db

@pytest.mark.asyncio
async def test_paystack_webhook_already_processed(async_client):
    # Setup mock DB to simulate an already processed event
    mock_db = MagicMock()
    mock_event_doc = MagicMock()
    mock_event_doc.exists = True
    
    def collection_mock(name):
        coll = MagicMock()
        if name == 'webhook_events':
            coll.document.return_value.get.return_value = mock_event_doc
        return coll
    mock_db.collection.side_effect = collection_mock
    
    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        # Mock signature verification to bypass security for the test
        with patch("app.api.webhook.verify_webhook_signature", return_value={"data": {"reference": "test_123"}, "event": "charge.success"}):
            response = await async_client.post("/webhook/paystack", json={})
            assert response.status_code == 200
            assert response.json()["status"] == "already_processed"
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_paystack_webhook_success(async_client):
    # Setup mock DB to simulate a new event
    mock_db = MagicMock()
    mock_batch = MagicMock()
    mock_db.batch.return_value = mock_batch
    
    mock_event_doc = MagicMock()
    mock_event_doc.exists = False
    
    mock_user_doc = MagicMock()
    mock_user_doc.exists = True
    
    def collection_mock(name):
        coll = MagicMock()
        if name == 'webhook_events':
            coll.document.return_value.get.return_value = mock_event_doc
        elif name == 'users':
            coll.document.return_value.get.return_value = mock_user_doc
        return coll
    mock_db.collection.side_effect = collection_mock
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # Mock signature verification
    event_payload = {
        "event": "charge.success",
        "data": {
            "reference": "test_123",
            "metadata": {
                "custom_fields": [
                    {"variable_name": "telegram_id", "value": "123456"},
                    {"variable_name": "plan_type", "value": "monthly"}
                ]
            },
            "amount": 500000,
            "customer": {"email": "test@test.com"},
            "plan": {"interval": "monthly"}
        }
    }
    
    try:
        with patch("app.api.webhook.verify_webhook_signature", return_value=event_payload), \
             patch("app.api.webhook.generate_invite_link", return_value="https://t.me/invite/123"), \
             patch("app.api.webhook.send_invite_email") as mock_email:
            
            response = await async_client.post("/webhook/paystack", json=event_payload)
            
            assert response.status_code == 200
            assert response.json()["status"] == "success"
            mock_email.assert_called_once_with("test@test.com", "https://t.me/invite/123")
    finally:
        app.dependency_overrides.clear()
