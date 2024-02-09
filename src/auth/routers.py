from typing import Annotated

from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.crud import get_user_profile
from src.auth.models import AuthUser
from src.auth.base_config import auth_backend, fastapi_users_auth, current_user
from src.auth.schemas import UserCreateInput, UserCreateOutput, UserProfile
from src.database import get_async_session

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

auth_router.include_router(fastapi_users_auth.get_auth_router(auth_backend))
auth_router.include_router(
    fastapi_users_auth.get_register_router(
        UserCreateOutput,
        UserCreateInput,
    ),
)

user_router = APIRouter(
    prefix="/users",
    tags=["User"],
)


@user_router.get(
    "/me",
    response_model=UserProfile,
    status_code=status.HTTP_200_OK,
)
async def get_profile(
    user: Annotated[AuthUser, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserProfile:
    return await get_user_profile(user=user, session=session)
