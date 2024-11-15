from fastapi import FastAPI
from contextlib import asynccontextmanager
from social_media.routers.post import router as post_router
from social_media.database import database

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(router=post_router, prefix="/posts", tags=["posts"])
