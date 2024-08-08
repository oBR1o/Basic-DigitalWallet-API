from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError

from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from passlib.context import CryptContext

from pydantic import BaseModel

from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from . import config

from . import models
from .models.users import User , DBUser

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(tags=["authentication"])

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db.values():
        return DBUser(**db)

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data : dict, expires_delta: timedelta | None = None):
    settings = config.get_settings()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
):
    settings = config.get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    result = await session.exec(
        select(DBUser).where(DBUser.username == token_data.username)
    )
    db_user = result.all()
    db_user = db_user[0]
    db_user = db_user.dict()
    if db_user is None:
        raise credentials_exception
    user = get_user(db_user, username=token_data.username)
    return user

async def get_current_activate_user(
        current_user: Annotated[User, Depends(get_current_user)]):
        if current_user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> Token:
    settings = config.get_settings()

    result = await session.exec(
        select(DBUser).where(DBUser.username == form_data.username)
    )
    db_user = result.all()
    db_user = db_user[0]
    db_user = db_user.dict()
    print(db_user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Incorrect username or password")
    
    user = authenticate_user(db_user, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    acces_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return Token(access_token=acces_token, token_type="bearer")