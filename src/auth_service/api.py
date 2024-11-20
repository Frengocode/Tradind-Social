from fastapi import security, Depends, HTTPException, APIRouter
from src.uitils.uitils import AuthUitils
import httpx


auth_service = APIRouter(tags=["Auth"])


@auth_service.post("/auth-login/", response_model=dict)
async def login(request: security.OAuth2PasswordRequestForm = Depends()):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8000/user-service/api/v1/get-user-by-username-password/{request.username}/{request.password}"
        )

    if response.status_code == 200:
        user_data = response.json()
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail="Invalid credentials or external service error",
        )

    access_token = AuthUitils.create_access_token(
        data={"sub": user_data.get("username")}
    )

    return {"access_token": access_token, "token_type": "bearer"}
