from fastapi import status
from pathlib import Path
import pytest
import httpx

BASE_URL = "http://localhost:8000"


@pytest.mark.asyncio
async def get_auth_token():
    login_data = {"username": "username12", "password": "testpass1231"}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/auth-login/", data=login_data)
        return response.json().get("access_token")


@pytest.mark.asyncio
async def test_create_account():
    data = {
        "username": (None, "nolik"),
        "email": (None, "kazira21@gmail.com"),
        "name": (None, "Test user for testing"),
        "password": (None, "boskazir123"),
    }

    current_dir = Path(__file__).parent
    picture_path = current_dir / "test_picture.jpg"

    files = {**data, "profile_picture": picture_path.open("rb")}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/user-service/api/v1/sign-up/", files=files
        )


        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_user_by_username_password():
    username = "admin"
    password = "admin123321"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/user-service/api/v1/get-user-by-username-password/{username}/{password}"
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_user_by_username():
    username = "admin"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/user-service/api/v1/get-user/{username}/"
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_user_by_id():
    token = await get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    user_id = 2
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/user-service/api/v1/get-user-by-pk/{user_id}/", headers=headers
        )
        response.status_code == status.HTTP_200_OK
