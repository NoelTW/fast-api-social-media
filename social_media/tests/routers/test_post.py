import pytest

from httpx import AsyncClient


async def create_post(body: str, async_client: AsyncClient) -> dict:
    response = await async_client.post("/posts/post", json={"body": body})
    return response.json()


async def create_comment(post_id: int, body: str, async_client: AsyncClient):
    response = await async_client.post(
        "/posts/comment", json={"post_id": post_id, "body": body}
    )
    return response.json()


@pytest.fixture()
async def created_post(async_client: AsyncClient):
    yield await create_post("Test post", async_client)


@pytest.fixture()
async def created_comment(
    created_post: dict,
    async_client: AsyncClient,
):
    yield await create_comment(created_post["id"], "Test comment", async_client)


@pytest.mark.anyio
async def test_create_post(async_client: AsyncClient):
    body = "Test post"
    response = await async_client.post("/posts/post", json={"body": body})
    assert response.status_code == 201
    assert response.json().items() >= {"id": 0, "body": body}.items()


@pytest.mark.anyio
async def test_create_post_missing_body(async_client: AsyncClient):
    response = await async_client.post("/posts/post", json={})
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_all_posts(async_client: AsyncClient, created_post: dict):
    response = await async_client.get("/posts/post")
    assert response.status_code == 200
    assert response.json() == [created_post]


@pytest.mark.anyio
async def test_create_comment(async_client: AsyncClient, created_post: dict):
    body = "Test comment"
    response = await async_client.post(
        "/posts/comment", json={"post_id": created_post["id"], "body": body}
    )
    assert response.status_code == 201
    assert (
        response.json().items()
        >= {"id": 0, "post_id": created_post["id"], "body": body}.items()
    )


@pytest.mark.anyio
async def test_create_comment_missing_body(
    async_client: AsyncClient, created_post: dict
):
    response = await async_client.post(
        "/posts/comment", json={"post_id": created_post["id"]}
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_comments_on_post(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/posts/post/{created_post['id']}/comment")
    assert response.status_code == 200
    assert response.json() == [created_comment]


@pytest.mark.anyio
async def test_get_comments_on_post_empty(
    async_client: AsyncClient, created_post: dict
):
    response = await async_client.get(f"/posts/post/{created_post['id']}/comment")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_get_post_with_comments(
    async_client: AsyncClient,
    created_post: dict,
    created_comment: dict,
):
    response = await async_client.get(f"/posts/post/{created_post['id']}")
    assert response.status_code == 200
    assert response.json() == {"post": created_post, "comments": [created_comment]}


@pytest.mark.anyio
async def test_get_post_with_comments_empty(
    async_client: AsyncClient,
):
    response = await async_client.get("/posts/post/2")
    assert response.status_code == 404
