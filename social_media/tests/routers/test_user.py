from fastapi import Request, HTTPException
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
    assert "User created. Please comfirm your email!" in response.json()["detail"]


@pytest.mark.anyio
async def test_register_user_already_registered(
    async_client: AsyncClient, registered_user: dict
):
    email = registered_user["email"]
    password = "1234"
    response = await register_user(async_client, email, password)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


@pytest.mark.anyio
async def test_login_user_not_exists(async_client: AsyncClient):
    response = await async_client.post(
        "/users/token", json={"email": "test@example.com", "password": "1234"}
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_login_user(async_client: AsyncClient, registered_user: dict):
    response = await async_client.post(
        "users/token",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.anyio
async def test_comfirm_user(async_client: AsyncClient, mocker):
    spy = mocker.spy(Request, "url_for")
    await register_user(async_client, email="test@example.com", password="1234")
    comfirmation_url = str(spy.spy_return)
    response = await async_client.get(comfirmation_url)

    assert response.status_code == 200
    assert {"detail": "Email confirmed successfully"}.items() <= response.json().items()


@pytest.mark.anyio
async def test_comfirm_user_invalid_token(async_client: AsyncClient):
    response = await async_client.get("users/comfirm/invalid_token")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_comfirm_user_expired(async_client: AsyncClient, mocker):
    mocker.patch("social_media.security.comfirm_token_expire_minutes", return_value=-1)
    spy = mocker.spy(Request, "url_for")
    await register_user(async_client, email="test@example.com", password="1234")
    comfirmation_url = str(spy.spy_return)
    response = await async_client.get(comfirmation_url)
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired"
