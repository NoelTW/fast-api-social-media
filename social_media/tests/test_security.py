import pytest
from fastapi import HTTPException
from jose import jwt

from social_media.security import (
    ALGORITHM,
    SECRURITY_KEY,
    asses_token_expire_minutes,
    authenticate_user,
    create_access_token,
    credetial_exption,
    get_current_user,
    get_user,
    hash_password,
    verify_password,
)


def test_asses_token_expire_minutes():
    assert asses_token_expire_minutes() == 30


def test_create_access_token():
    email = "test@example.com"
    token = create_access_token(email)

    assert {"sub": email}.items() <= jwt.decode(
        token=token, key=SECRURITY_KEY, algorithms=ALGORITHM
    ).items()


@pytest.mark.anyio
async def test_password_hashes():
    password = "1234"
    hashed_password = hash_password(password)
    assert verify_password(password, hashed_password)


@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    user = await get_user(registered_user["email"])
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_user_not_found():
    user = await get_user("test@example.com")
    assert user is None


@pytest.mark.anyio
async def test_authenticate_user(registered_user: dict):
    user = await authenticate_user(
        registered_user["email"], registered_user["password"]
    )
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_authenticate_user_not_found():
    with pytest.raises(HTTPException) as e:
        await authenticate_user("test@example.com", "1234")
        assert e.value == credetial_exption


@pytest.mark.anyio
async def test_authenticate_user_worng_password(registered_user: dict):
    with pytest.raises(HTTPException) as e:
        await authenticate_user(
            email=registered_user["email"], password="wrong password"
        )
        assert e.value == credetial_exption


@pytest.mark.anyio
async def test_get_current_user(registered_user: dict):

    token = create_access_token(registered_user["email"])
    user = await get_current_user(token)
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_current_user_token_invalid_token():
    with pytest.raises(HTTPException) as e:
        await get_current_user("invalid token")
        assert e.value == credetial_exption


@pytest.mark.anyio
async def test_get_current_user_token_expired(registered_user: dict):
    import datetime
    import asyncio

    token = create_access_token(registered_user["email"])
    payload = jwt.decode(token, SECRURITY_KEY, algorithms=[ALGORITHM])
    payload["exp"] = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        seconds=1
    )
    await asyncio.sleep(1.1)
    token = jwt.encode(payload, SECRURITY_KEY, algorithm=ALGORITHM)
    with pytest.raises(HTTPException) as e:
        await get_current_user(token)
        assert e.value.status_code == 401
        assert "Token has expired" in e.value.detail
