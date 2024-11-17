import logging

from social_media.database import database, user_table

logger = logging.getLogger(__name__)


async def get_user(email: str):
    logger.debug("Feching user from database", extra={"emai": email})
    query = user_table.select().where(user_table.c.email == email)
    result = await database.fetch_one(query)
    return result if result else None
