from fastapi import status
import pytest
import httpx
from src.tests.confest import get_auth_token, BASE_URL


@pytest.mark.asyncio
async def test_create_view_for_signal():
    token = await get_auth_token()
    signal_id = 21
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/view-service/api/v1/create-view-for-signal/{signal_id}/",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_user_views():
    token = await get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        response = await client.get(
            f"{BASE_URL}/view-service/api/v1/get-views/", headers=headers
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_views_from_signal():
    token = await get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    signal_id = 7
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/view-service/api/v1/get-views-from-signal/{signal_id}/",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
