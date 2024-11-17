import logging

from fastapi import APIRouter, HTTPException, status

from social_media.database import database, user_table
from social_media.models.user import UserIn
from social_media.security import (
    get_user,
    hash_password,
    authenticate_user,
    create_access_token,
)


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", status_code=201)
async def register(user: UserIn):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    hashed_password = hash_password(user.password)
    query = user_table.insert().values(email=user.email, password=hashed_password)
    logger.debug(query)
    await database.execute(query)
    return {"detail": "User created successfully"}


@router.post("/token")
async def login(user: UserIn):
    user = await authenticate_user(user.email, user.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}
