from fastapi import status
from src.tests.confest import get_auth_token, BASE_URL
import httpx
import pytest


@pytest.mark.asyncio
async def test_create_comment_for_signal():
    token = await get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "comment": "Test Comment",
        "signal_id": 21
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
        response = await client.post(f"{BASE_URL}/comment-service/api/v1/create-comment/", json=data, headers=headers)
        assert response.status_code == status.HTTP_200_OK



@pytest.mark.asyncio
async def test_get_all_comments_from_signal():
    token = await get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
        response  = await client.get(f"{BASE_URL}/comment-service/api/v1/get-comments-from-signal/{21}/",  headers=headers)
        assert response.status_code == status.HTTP_200_OK
        


@pytest.mark.asyncio
async def test_delete_comment():
    token = await get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{BASE_URL}/comment-service/api/v1/delete-comment/{7}/", headers=headers)
        assert response.status_code == status.HTTP_200_OK

