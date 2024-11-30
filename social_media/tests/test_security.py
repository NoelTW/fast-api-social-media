import pytest
from fastapi import HTTPException
from jose import jwt

from social_media.security import (
    ALGORITHM,
    SECRURITY_KEY,
    access_token_expire_minutes,
    authenticate_user,
    confirm_token_expire_minutes,
    create_access_token,
    create_confirmation_token,
    create_credentials_exception,
    get_current_user,
    get_subject_for_token_type,
    get_user,
    hash_password,
    verify_password,
)


def test_create_credentials_exception():
    exception = create_credentials_exception("test")
    assert exception.status_code == 401
    assert exception.detail == "test"
    assert exception.headers == {"WWW-Authenticate": "Bearer"}


def test_access_token_expire_minutes():
    assert access_token_expire_minutes() == 30


def test_confirm_token_expire_minutes():
    assert confirm_token_expire_minutes() == 1440


def test_create_access_token():
    email = "test@example.com"
    token = create_access_token(email)

    assert {"sub": email, "type": "access"}.items() <= jwt.decode(
        token=token, key=SECRURITY_KEY, algorithms=ALGORITHM
    ).items()


def test_create_confirmation_token():
    email = "test@example.com"
    token = create_confirmation_token(email)

    assert {"sub": email, "type": "confirmation"}.items() <= jwt.decode(
        token=token, key=SECRURITY_KEY, algorithms=ALGORITHM
    ).items()


def test_get_subject_for_token_type_valid_confirmation():
    email = "test@example.com"
    token = create_confirmation_token(email)
    assert get_subject_for_token_type(token, "confirmation") == email


def test_get_subject_for_token_type_valid_access():
    email = "test@example.com"
    token = create_access_token(email)
    assert get_subject_for_token_type(token, "access") == email


def test_get_subject_for_token_type_expired(mocker):
    email = "test@example.com"
    mocker.patch("social_media.security.access_token_expire_minutes", return_value=-1)
    token = create_access_token(email)
    with pytest.raises(HTTPException) as exc_info:
        get_subject_for_token_type(token, "access")
        assert exc_info.detail == "Token has expired"


def test_get_subject_for_token_type_invalid():
    token = "Invalid token"
    with pytest.raises(HTTPException) as exc_info:
        get_subject_for_token_type(token, "access")
        assert exc_info.detail == "Invalid token"


def test_get_subject_for_token_type_missing_sub():
    email = "test@example.com"
    token = create_access_token(email)
    subject = get_subject_for_token_type(token, "access")
    assert subject == email
    payload = jwt.decode(token, SECRURITY_KEY, algorithms=[ALGORITHM])
    # Test
    del payload["sub"]
    token_without_sub = jwt.encode(payload, SECRURITY_KEY, algorithm=ALGORITHM)
    with pytest.raises(HTTPException) as exc_info:
        get_subject_for_token_type(token_without_sub, "access")
    assert exc_info.value.detail == "Token missing 'sub' field"


def test_get_subject_for_token_type_wrong_type():
    email = "test@example.com"
    token = create_access_token(email)
    with pytest.raises(HTTPException) as exc_info:
        get_subject_for_token_type(token, "confirmation")
    assert exc_info.value.detail == "Invalid token type, expeted 'confirmation'"


@pytest.mark.anyio
async def test_password_hashes():
    password = "1234"
    hashed_password = hash_password(password)
    assert verify_password(password, hashed_password)


@pytest.mark.anyio
async def test_get_user(confirmed_user: dict):
    user = await get_user(confirmed_user["email"])
    assert user.email == confirmed_user["email"]


@pytest.mark.anyio
async def test_get_user_not_found():
    user = await get_user("test@example.com")
    assert user is None


@pytest.mark.anyio
async def test_authenticate_user(confirmed_user: dict):
    user = await authenticate_user(confirmed_user["email"], confirmed_user["password"])
    assert user.email == confirmed_user["email"]


@pytest.mark.anyio
async def test_authenticate_user_not_found():
    with pytest.raises(HTTPException) as exc_info:
        await authenticate_user("test@example.com", "1234")
    assert exc_info.value.detail == "Invalid email or password!"


@pytest.mark.anyio
async def test_authenticate_user_worng_password(confirmed_user: dict):
    with pytest.raises(HTTPException) as exc_info:
        await authenticate_user(
            email=confirmed_user["email"], password="wrong password"
        )
    assert exc_info.value.detail == "Invalid email or password!"


@pytest.mark.anyio
async def test_get_current_user(confirmed_user: dict):

    token = create_access_token(confirmed_user["email"])
    user = await get_current_user(token)
    assert user.email == confirmed_user["email"]


@pytest.mark.anyio
async def test_get_current_user_token_invalid_token():
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user("invalid token")
    assert exc_info.value.detail == "Invalid token"


@pytest.mark.anyio
async def test_get_current_user_token_expired(confirmed_user: dict, mocker):
    with pytest.raises(HTTPException) as exc_info:
        mocker.patch(
            "social_media.security.access_token_expire_minutes", return_value=-1
        )
        token = create_access_token(confirmed_user["email"])
        await get_current_user(token)
    assert exc_info.value.status_code == 401
    assert "Token has expired" in exc_info.value.detail


@pytest.mark.anyio
async def test_get_current_user_wrong_type_token(confirmed_user: dict):
    token = create_confirmation_token(confirmed_user["email"])
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token)
    assert exc_info.value.detail == "Invalid token type, expeted 'access'"
