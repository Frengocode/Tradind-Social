from fastapi import status
from pathlib import Path
import httpx
import pytest


BASE_URL = "http://localhost:8000"


@pytest.mark.asyncio
async def get_auth_token():
    login_data = {"username": "username12", "password": "testpass1231"}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/auth-login/", data=login_data)
        return response.json().get("access_token")


@pytest.mark.asyncio
async def test_create_news():

    token = await get_auth_token()

    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "news_title": "Скоро Ethir Взлетит",
    }

    current_dir = Path(__file__).parent
    picture_path = current_dir / "test_picture.jpg"

    files = {"news_picture": picture_path.open("rb")}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/news-service/api/v1/create-news/",
            files=files,
            data=data,
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_all_news():
    token = await get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        response = await client.get(
            f"{BASE_URL}/news-service/api/v1/get-all-news/", headers=headers
        )
        assert response.status_code == 200
        json_response = response.json()
        assert isinstance(json_response, list)


@pytest.mark.asyncio
async def test_get_news():
    token = await get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    news_id = 6
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/news-service/api/v1/get-news/{news_id}/", headers=headers
        )
        assert "id" in response.json()
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_delete_news():
    token = await get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    news_id = 34
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BASE_URL}/news-service/api/v1/delete-news/{news_id}/", headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
