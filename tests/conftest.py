import pytest
import respx
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, patch
from app.main import app

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client

@pytest.fixture(autouse=True)
def mock_firebase(monkeypatch):
    """Mock Firebase Admin SDK to avoid real DB connections during tests."""
    mock_db = MagicMock()
    mock_batch = MagicMock()
    mock_db.batch.return_value = mock_batch
    
    # Mock specific collections and queries as needed per test
    monkeypatch.setattr("app.database.connection.get_db", lambda: mock_db)
    return mock_db

@pytest.fixture
def mock_paystack_api():
    """Mock the external Paystack API using respx."""
    with respx.mock(base_url="https://api.paystack.co") as respx_mock:
        yield respx_mock
