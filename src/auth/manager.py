import logging
import uuid
from typing import Annotated, Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin

from src.auth.models import AuthUser
from src.auth.utils import get_user_db
from src.config import settings
from src.database import Base

logging.basicConfig(filename="example.log", filemode="w", level=logging.DEBUG)
logger = logging.getLogger("tripser_logger")


class UserManager(UUIDIDMixin, BaseUserManager[AuthUser, uuid.UUID]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_register(
        self, user: AuthUser, request: Optional[Request] = None
    ):
        logger.info(f"User {user.id} has registered.")


async def get_user_manager(user_db: Annotated[Base, Depends(get_user_db)]):
    yield UserManager(user_db)
