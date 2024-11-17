import os
from typing import AsyncGenerator, Generator

from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
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
async def logged_in_token(async_client: AsyncClient, registered_user: dict):
    response = await async_client.post("users/token", json=registered_user)
    print(response.json())
    return response.json()["access_token"]
