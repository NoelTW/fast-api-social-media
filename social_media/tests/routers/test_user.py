import pytest
from httpx import AsyncClient


async def register_user(async_client: AsyncClient, email: str, password: str):
    response = await async_client.post(
        "/users/register", json={"email": email, "password": password}
    )
    return response


@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    email = "test@example.com"
    password = "1234"
    response = await register_user(async_client, email, password)
    assert response.status_code == 201
    assert "User created successfully" in response.json()["detail"]


@pytest.mark.anyio
async def test_register_user_already_registered(
    async_client: AsyncClient, registered_user: dict
):
    email = registered_user["email"]
    password = "1234"
    response = await register_user(async_client, email, password)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]
