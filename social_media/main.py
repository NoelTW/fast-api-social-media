import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

from social_media.database import database
from social_media.logging_config import configure_logging
from social_media.routers.post import router as post_router
from social_media.routers.user import router as user_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

app.add_middleware(CorrelationIdMiddleware)


app.include_router(router=post_router, prefix="/posts", tags=["posts"])
app.include_router(router=user_router, prefix="/users", tags=["users"])


@app.exception_handler(HTTPException)
async def http_exception_handler_loggin(request, exc):
    logger.error(f"HTTP exception: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)
