import asyncio
from typing import Any
import pytest

from httpx import AsyncClient, Response

from collections.abc import AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from src.main import app
from src.config import settings
from src.database import Base, get_async_session


DATABASE_URL_TEST = settings.db_url_postgresql

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = async_sessionmaker(
    engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        pass


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, Any, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture()
async def default_user_registration(ac: AsyncClient) -> Response:
    return await ac.post(
        "auth/register",
        json={
            "email": "user@example.com",
            "password": "123",
        },
    )


@pytest.fixture()
async def auth_user(ac: AsyncClient) -> Response:
    data = {"username": "user@example.com", "password": "123"}
    response = await ac.post(
        "auth/login",
        data=data,
    )
    ac.cookies.set(name="tripster", value=response.cookies.get("tripster"))
    return response


@pytest.fixture()
async def get_user(ac: AsyncClient) -> Response:
    response = await ac.get("users/me")
    return response


@pytest.fixture()
async def create_piblication(ac: AsyncClient) -> Response:
    responce = await ac.post("publication/?text=Privet")
    return responce
