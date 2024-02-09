import uuid

from fastapi_users.schemas import CreateUpdateDictModel, BaseUser
from pydantic import BaseModel, EmailStr


class UserCreateOutput(BaseUser[uuid.UUID]):
    id: uuid.UUID
    email: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        from_attributes = True


class UserCreateInput(CreateUpdateDictModel):
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    """Profile model."""

    id: uuid.UUID
    user_id: uuid.UUID


class UserProfileUpdate(BaseModel):
    """Profile update model."""

    ...
