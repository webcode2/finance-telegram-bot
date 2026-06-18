import pytest
import httpx

@pytest.mark.asyncio
async def test_get_plans_success(async_client, mock_paystack_api):
    # Mock the Paystack API response
    mock_paystack_api.get("/plan").respond(
        status_code=200,
        json={
            "status": True,
            "message": "Plans retrieved",
            "data": [
                {
                    "name": "Test Plan",
                    "amount": 500000, # 5000 NGN
                    "plan_code": "PLN_123"
                }
            ]
        }
    )

    response = await async_client.get("/plans/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Plan"
    assert data[0]["price_label"] == "₦5,000.00"
    assert data[0]["plan_type"] == "PLN_123"

@pytest.mark.asyncio
async def test_get_plans_paystack_failure(async_client, mock_paystack_api):
    # Mock a Paystack failure
    mock_paystack_api.get("/plan").respond(status_code=500)

    response = await async_client.get("/plans/")
    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to fetch subscription plans"
