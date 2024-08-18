from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select, UniqueConstraint


class BaseUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    disabled: bool | None = None



class CreatedUser(BaseUser):
    pass

class UpdatedUser(BaseUser):
    pass


class User(BaseUser):
    id: int

class ChangePassword(BaseModel):
    current_password: str
    new_password: str


class DBUser(User, SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("username"),)
    id: int = Field(default=None, primary_key=True)
    hashed_password: str
