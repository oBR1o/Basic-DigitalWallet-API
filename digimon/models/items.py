from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select

from . import merchants


class BaseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str | None = None
    price: float = 0.12
    tax: float | None = None
    merchant_id: int | None
    user_id: int | None = 1
    quantity: int = 1


class CreatedItem(BaseItem):
    pass

class UpdatedItem(BaseItem):
    pass


class Item(BaseItem):
    id: int
    merchant_id: int


class DBItem(Item, SQLModel, table=True):
    __tablename__ = "items"
    id: int = Field(default=None, primary_key=True)
    merchant_id: int = Field(default=None, foreign_key="merchants.id")

    user_id: int = Field(default=None, foreign_key="users.id")


class ItemList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[Item]
    page: int
    page_count: int
    size_per_page: int
