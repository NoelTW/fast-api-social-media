import datetime
import logging
import secrets
import os


from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from social_media.database import database, user_table

logger = logging.getLogger(__name__)


SECRURITY_KEY = os.environ.get("SECRURITY_KEY")

if SECRURITY_KEY is None:  # Generate a key if not found
    SECRURITY_KEY = secrets.token_urlsafe(32)
    print(
        f"Generated new security key: {SECRURITY_KEY}.  Store this securely as an environment variable!"
    )

# SECRURITY_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"])

credetial_exption = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credetial",
    headers={"WWW-Authenticate": "Bearer"},
)


def asses_token_expire_minutes() -> int:
    return 30


def create_access_token(email: str) -> str:
    logger.debug("Creating access token", extra={"email": email})
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=asses_token_expire_minutes()
    )
    jwt_data = {"sub": email, "exp": expire}
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
        raise credetial_exption
    if not verify_password(password, user.password):
        raise credetial_exption
    return user


async def get_current_user(token: str):
    # logger.debug("Getting current user", extra={"token": token})
    try:
        payload = jwt.decode(token, SECRURITY_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credetial_exption
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except JWTError as e:
        raise credetial_exption from e
    user = await get_user(email=email)
    return user
