from dirty_equals import IsUUID

from fastapi_users.authentication.strategy.jwt import decode_jwt
from fastapi import status
from httpx import AsyncClient, Response

from src.config import settings


async def test_user_registration(ac: AsyncClient, default_user_registration: Response):
    assert default_user_registration.json() == {
        "id": IsUUID(4),
        "email": f"{default_user_registration.json()['email']}",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
    }
    assert default_user_registration.status_code == status.HTTP_201_CREATED


async def test_user_login(
    ac: AsyncClient, default_user_registration: Response, auth_user: Response
):
    assert auth_user.status_code == status.HTTP_204_NO_CONTENT
    assert (
        decode_jwt(
            auth_user.cookies.get("tripster"),
            settings.SECRET_KEY,
            audience=["fastapi-users:auth"],
        )["sub"]
        == default_user_registration.json()["id"]
    )
