import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock

from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient, Request, Response
from pytest import fixture

os.environ["ENV_STATE"] = "test"

from social_media.database import database, user_table
from social_media.main import app


@fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@fixture
def client() -> Generator:
    yield TestClient(app)


@fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    yield
    await database.disconnect()


@fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=client.base_url
    ) as ac:
        yield ac


@fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {"email": "test@example.com", "password": "1234"}
    await async_client.post("/users/register", json=user_details)
    query = user_table.select().where(user_table.c.email == user_details["email"])
    # TODO: check if -> user_details = await database.fetch_one(query) works
    user = await database.fetch_one(query)
    user_details["id"] = user.id
    return user_details


@fixture()
async def confirmed_user(registered_user: dict) -> dict:
    query = (
        user_table.update()
        .where(user_table.c.email == registered_user["email"])
        .values(confirmed=True)
    )
    await database.execute(query)
    return registered_user


@fixture()
async def logged_in_token(async_client: AsyncClient, confirmed_user: dict):
    response = await async_client.post("users/token", json=confirmed_user)
    print(response.json())
    return response.json()["access_token"]


@fixture(autouse=True)
def mock_httpx_client(mocker):
    mocked_client = mocker.patch("social_media.tasks.httpx.AsyncClient")
    mocked_async_client = Mock()
    response = Response(status_code=200, content="OK", request=Request("POST", "//"))
    mocked_async_client.post = AsyncMock(return_value=response)
    mocked_client.return_value.__aenter__.return_value = mocked_async_client
    return mocked_async_client
