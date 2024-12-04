import pytest

from social_media.tasks import send_simple_mail, APIResponseError
import httpx


@pytest.mark.anyio
async def test_send_simple_mail(mock_httpx_client):
    await send_simple_mail(to="test@example.com", subject="test", body="test")
    mock_httpx_client.post.assert_called_once()


@pytest.mark.anyio
async def test_send_simple_mail_error(mock_httpx_client):
    mock_httpx_client.post.return_value = httpx.Response(
        status_code=400, content="Error", request=httpx.Request("POST", "//")
    )
    with pytest.raises(APIResponseError) as exc_info:
        await send_simple_mail(to="test@example.com", subject="test", body="test")
    assert "400" in str(exc_info.value)
