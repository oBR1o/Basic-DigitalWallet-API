from fastapi import APIRouter,  HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jwt.exceptions import InvalidTokenError

from typing import Optional, Annotated

from sqlmodel import Field, SQLModel, create_engine, Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from .. import security

from .. import models

from ..models.users import User , DBUser, CreatedUser,  UpdatedUser, ChangePassword


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

@router.put("/{user_id}/change_password")
async def change_password(
    user_id: int,
    password_update: ChangePassword,
    current_user: Annotated[User, Depends(security.get_current_activate_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> dict(): # type: ignore
    user = await session.get(DBUser, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not security.verify_password(
        password_update.current_password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password is incorrect",
        )
    
    user.hashed_password = security.get_password_hash(password_update.new_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return {"message": "Password changed successfully"}

