import pytest
import httpx
from fastapi import status
from datetime import datetime, timedelta
from pathlib import Path
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


BASE_URL = "http://localhost:8000"


@pytest.mark.asyncio
async def get_auth_token():
    login_data = {"username": "wendy", "password": "python$_venv"}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/auth-login/", data=login_data)
        return response.json().get("access_token")


@pytest.mark.asyncio
async def test_create_signal():
    token = await get_auth_token()

    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "title": "Test Signal",
        "signal_for_coin": "BTC",
        "when": datetime.now().isoformat(),
        "when_end": (datetime.now() + timedelta(days=1)).isoformat(),
        "short_or_long": "long",
    }

    current_dir = Path(__file__).parent
    picture_path = current_dir / "test_picture.jpg"

    files = {"signal_picture": picture_path.open("rb")}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/signal/service/api/v1/create-signal/",
            data=data,
            files=files,
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK
        json_response = response.json()
        assert json_response["title"] == data["title"]


@pytest.mark.asyncio
async def test_get_all_signals():

    token = await get_auth_token()

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
        response = await client.get(
            f"{BASE_URL}/signal/service/api/v1/get-all-signals/", headers=headers
        )

        assert response.status_code == 200
        json_response = response.json()
        assert isinstance(json_response, list)  # Проверка, что вернулся список сигналов


@pytest.mark.asyncio
async def test_get_signal():
    token = await get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    signal_id = 5
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as client:
        response = await client.get(
            f"{BASE_URL}/signal/service/api/v1/get-signal/{signal_id}/", headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert "id" in response.json()


@pytest.mark.asyncio
async def test_update_signal():
    token = await get_auth_token()

    headers = {"Authorization": f"Bearer {token}"}

    signal_id = 5

    data = {
        "title": "Updated Signal",
        "signal_for_coin": "Bitcoin",
        "when": "2024-11-01T10:58:30.69629",
        "when_end": "2024-11-01T10:58:30.69629",
        "short_or_long": "Long",
    }
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{BASE_URL}/signal/service/api/v1/update-signal/{signal_id}/",
            headers=headers,
            json=data,
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_delete_signal():
    token = await get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    signal_id = 24
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BASE_URL}/signal/service/api/v1/delete-signal/{signal_id}/",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def get_user_signals():
    token = await get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    user_id = 2
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as client:
        response = await client.get(
            f"{BASE_URL}/signal/service/api/v1/get-user-signals/{user_id}/",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK


##### All Tests passed 5/5
#### Nice
