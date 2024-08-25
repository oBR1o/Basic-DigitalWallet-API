import typing
import jwt

from fastapi import Depends, HTTPException, status, Path, Query
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from typing import Annotated

from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import ValidationError

from . import models
from . import security
from . import config
from .models.users import User , DBUser, TokenData

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

settings = config.get_settings()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[models.AsyncSession, Depends(models.get_session)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        user_id: int = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except jwt.JWTError as e:
        print(e)
        raise credentials_exception

    user = await session.get(DBUser, user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_activate_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user

async def get_current_active_superuser(
    current_user: typing.Annotated[User, Depends(get_current_user)],
) -> User:
    if "admin" not in current_user.roles:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user