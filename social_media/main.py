from fastapi import FastAPI
from social_media.routers.post import router as post_router


app = FastAPI()

app.include_router(router=post_router, prefix="/posts", tags=["posts"])
