import datetime
import logging

# import secrets
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from social_media.database import database, user_table

logger = logging.getLogger(__name__)


# SECRURITY_KEY = secrets.token_urlsafe(32)
SECRURITY_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNzMyOTYzMTg3fQ.oNUlVqGnu4vIz7LjT8sMi8xS2NPJGH3RWeJ-CEUeuv8"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"])


def create_credentials_exception(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def access_token_expire_minutes() -> int:
    return 30


def comfirm_token_expire_minutes() -> int:
    return 1440


def get_subject_for_token_type(
    token: str, _type: Literal["access", "comfirmation"]
) -> str:
    try:
        payload = jwt.decode(token, SECRURITY_KEY, algorithms=[ALGORITHM])

    except ExpiredSignatureError as e:
        raise create_credentials_exception("Token has expired") from e
    except JWTError as e:
        raise create_credentials_exception("Invalid token") from e
    email: str = payload.get("sub")
    if email is None:
        raise create_credentials_exception("Token missing 'sub' field")
    toeken_type = payload.get("type")
    if _type != toeken_type or _type is None:
        raise create_credentials_exception(f"Invalid token type, expeted '{_type}'")
    return email


def create_access_token(email: str) -> str:
    logger.debug(
        "Creating access token",
        extra={"email": email},
    )
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=access_token_expire_minutes()
    )
    jwt_data = {"sub": email, "exp": expire, "type": "access"}
    return jwt.encode(jwt_data, SECRURITY_KEY, algorithm=ALGORITHM)


def create_comfirmation_token(email: str) -> str:
    logger.debug("Creating comfirmation token", extra={"email": email})
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=comfirm_token_expire_minutes()
    )
    jwt_data = {"sub": email, "exp": expire, "type": "comfirmation"}
    return jwt.encode(jwt_data, SECRURITY_KEY, algorithm=ALGORITHM)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(email: str):
    logger.debug("Feching user from database", extra={"emai": email})
    query = user_table.select().where(user_table.c.email == email)
    result = await database.fetch_one(query)
    return result if result else None


async def authenticate_user(email: str, password: str) -> str:
    logger.debug("Authenticating user", extra={"email": email})
    user = await get_user(email)
    if not user:
        raise create_credentials_exception("Invalid email or password!")
    if not verify_password(password, user.password):
        raise create_credentials_exception("Invalid email or password!")
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    # logger.debug("Getting current user", extra={"token": token})
    email = get_subject_for_token_type(token, "access")
    user = await get_user(email=email)
    if user is None:
        raise create_credentials_exception("Could not find user for this token!")
    return user
