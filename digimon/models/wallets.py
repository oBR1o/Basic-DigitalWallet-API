from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select

class BaseWallet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    merchant_name: str | None = None
    balance: float = 0.0


class CreatedWallet(BaseWallet):
    pass


class UpdatedWallet(BaseWallet):
    pass

class Wallet(BaseWallet):
    id: int


class DBWallet(Wallet, SQLModel, table=True):
    __tablename__ = "wallets"
    id: Optional[int] = Field(default=None, primary_key=True)

    merchant_id: int = Field(default=None, foreign_key="merchants.id")