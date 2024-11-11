from pytest import fixture
from typing import Generator, AsyncGenerator
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from social_media.main import app
from social_media.routers.post import comment_table, post_table


@fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@fixture
def client() -> Generator:
    with TestClient(app) as client:
        yield client


@fixture(autouse=True)
def db() -> Generator:
    post_table.clear()
    comment_table.clear()
    yield


@fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=client.base_url
    ) as ac:
        yield ac
