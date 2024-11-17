import pytest

from social_media.security import get_user


@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    user = await get_user(registered_user["email"])
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_user_not_found():
    user = await get_user("test@example.com")
    assert user is None
