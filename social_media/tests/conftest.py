import os
from typing import AsyncGenerator, Generator

from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from pytest import fixture

os.environ["ENV_STATE"] = "test"

from social_media.database import database
from social_media.main import app


@fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@fixture
def client() -> Generator:
    with TestClient(app) as client:
        yield client
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
