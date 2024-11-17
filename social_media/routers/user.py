import logging
from fastapi import APIRouter, HTTPException, status

from social_media.models.user import UserIn
from social_media.security import get_user
from social_media.database import user_table, database

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", status_code=201)
async def register(user: UserIn):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    # TODO: setting encryption to password later
    query = user_table.insert().values(email=user.email, password=user.password)
    logger.debug(query)
    await database.execute(query)
    return {"detail": "User created successfully"}
