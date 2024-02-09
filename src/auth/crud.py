from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.auth.schemas import UserCreateInput, UserCreateOutput, UserProfile


async def add_user(user: UserCreateInput, session: AsyncSession) -> UserCreateOutput:
    stmt = (
        insert(AuthUser)
        .values(
            {
                AuthUser.email: user.email,
                AuthUser.hashed_password: user.password,
            },
        )
        .returning(AuthUser)
    )

    user = (await session.execute(stmt)).scalar_one_or_none()
    await session.commit()
    return user


async def get_user_profile(
    user: AuthUser,
    session: AsyncSession,
) -> UserProfile:
    """Get user profile."""
    stmt = select(AuthUser).filter_by(id=user.id)
    result = await session.execute(stmt)
    profile = result.scalars().first()
    return UserCreateOutput.model_validate(profile)
