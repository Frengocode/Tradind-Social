import httpx
import pytest


BASE_URL = "http://localhost:8000"


@pytest.mark.asyncio
async def get_auth_token():
    login_data = {"username": "username12", "password": "testpass1231"}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/auth-login/", data=login_data)
        return response.json().get("access_token")
