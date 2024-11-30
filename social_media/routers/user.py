import logging

from fastapi import APIRouter, HTTPException, Request, status

from social_media.database import database, user_table
from social_media.models.user import UserIn
from social_media.security import (
    authenticate_user,
    create_access_token,
    create_comfirmation_token,
    get_subject_for_token_type,
    get_user,
    hash_password,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", status_code=201)
async def register(user: UserIn, request: Request):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    hashed_password = hash_password(user.password)
    query = user_table.insert().values(email=user.email, password=hashed_password)
    logger.debug(query)
    await database.execute(query)
    return {
        "detail": "User created. Please comfirm your email!",
        "comfirmation": request.url_for(
            "comfirm_email", token=create_comfirmation_token(user.email)
        ),
    }


@router.post("/token")
async def login(user: UserIn):
    user = await authenticate_user(user.email, user.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/comfirm/{token}")
async def comfirm_email(token: str):
    email = get_subject_for_token_type(token, "comfirmation")
    query = (
        user_table.update().where(user_table.c.email == email).values(comfirmed=True)
    )
    logger.debug(query)
    await database.execute(query)
    return {"detail": "Email confirmed successfully"}
