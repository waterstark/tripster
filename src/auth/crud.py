from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.auth.schemas import UserCreateInput


async def add_user(user: UserCreateInput, session: AsyncSession):
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


# async def get_user_profile(
#     user: AuthUser,
#     session: AsyncSession,
# ) -> UserProfile:
#     """Get user profile."""
#     stmt = select(UserSettings).filter_by(user_id=user.id)
#     profile = await session.execute(stmt)
#     return schemas.UserProfile.validate(profile.scalars().first())
