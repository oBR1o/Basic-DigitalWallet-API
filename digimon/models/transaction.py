from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select


class BaseTransaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_price: float
    quantity: int



class CreatedMerchant(BaseTransaction):
    pass

class UpdatedMerchant(BaseTransaction):
    pass


class Transaction(BaseTransaction):
    id: int


class DBTransaction(Transaction, SQLModel, table=True):
    __tablename__ = "transactions"
    id: Optional[int] = Field(default=None, primary_key=True)


class TransactionList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trainsactions: list[Transaction]
    page: int
    page_size: int
    size_per_page: int
