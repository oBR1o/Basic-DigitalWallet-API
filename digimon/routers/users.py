from fastapi import APIRouter,  HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jwt.exceptions import InvalidTokenError

from typing import Optional, Annotated

from sqlmodel import Field, SQLModel, create_engine, Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from .. import security

from .. import models

from ..models.users import User , DBUser, CreatedUser,  UpdatedUser


router = APIRouter(prefix="/users", tags=["user"])

@router.post("")
async def create_user(
    user: CreatedUser,
    password: str,
    session: Annotated[AsyncSession, Depends(models.get_session)]   
) -> User | None:
    data = user.dict()
    dbuser = DBUser(**data)
    dbuser.hashed_password = security.get_password_hash(password)
    session.add(dbuser)
    await session.commit()
    await session.refresh(dbuser)

    return dbuser


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: Annotated[AsyncSession, Depends(security.get_current_activate_user)],):
    return current_user


@router.get("/me/items")
async def read_own_items(
    current_user: Annotated[User, Depends(security.get_current_activate_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]


