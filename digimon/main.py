from fastapi import FastAPI,  HTTPException

from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select


class BaseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str | None = None
    price: float = 0.12
    tax: float | None = None


class CreatedItem(BaseItem):
    pass

class UpdatedItem(BaseItem):
    pass


class Item(BaseItem):
    id: int


class DBItem(Item, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ItemList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[Item]
    page: int
    page_size: int
    size_per_page: int


connect_args = {}

engine = create_engine(
    "postgresql+pg8000://postgres:123456@localhost/digimondb",
    echo=True,
    connect_args=connect_args,
)


SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.post("/items")
async def create_item(item: CreatedItem) -> Item:
    print("created_item", item)
    data = item.dict()
    dbitem = DBItem(**data)
    with Session(engine) as session:
        session.add(dbitem)
        session.commit()
        session.refresh(dbitem)

    return Item.from_orm(dbitem)


@app.get("/items")
async def read_items() -> ItemList:
    with Session(engine) as session:
        items = session.exec(select(DBItem)).all()
    return ItemList.from_orm(dict(items=items, page_size=0, page=0, size_per_page=0))


@app.get("/items/{item_id}")
async def read_item(item_id: int) -> Item:
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        if db_item:
            return Item.from_orm(db_item)
    raise HTTPException(status_code=404, detail="Item not found")


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: UpdatedItem) -> Item:
    print("updated_item", item)
    data = item.dict()
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        db_item.sqlmodel_update(data)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)

    return Item.from_orm(db_item)


@app.delete("/items/{item_id}")
async def delete_item(item_id: int) -> dict:
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        session.delete(db_item)
        session.commit()
    return dict(message=f"delete success")


class BaseMerchant(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str | None = None
    telephone: str | None = None
    email: str | None = None
    age: int | None = None

class CreatedMerchant(BaseMerchant):
    pass

class UpdatedMerchant(BaseMerchant):
    pass


class Merchant(BaseMerchant):
    id: int


class MarchantList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    merchants: list[Merchant]
    page: int
    page_size: int
    size_per_page: int

class DBMerchant(Merchant, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

@app.post("/merchants")
async def create_merchant(item: CreatedMerchant)-> Merchant:
    data = item.dict()
    db_merchant = DBMerchant(**data)
    with Session(engine) as session:
        session.add(db_merchant)
        session.commit()
        session.refresh(db_merchant)

    return Merchant.from_orm(db_merchant)

@app.get("/merchants")
async def read_merchants(page: int = 1, page_size: int = 10) -> MarchantList:
    with Session(engine) as session:
        merchants = session.exec(select(DBMerchant).offset((page - 1) * page_size).limit(page_size)).all()
    return MarchantList.from_orm(dict(merchants=merchants, page_size= page_size, page= page, size_per_page= len(merchants)))

@app.get("/merchants/{merchant_id}")
async def read_merchant(merchant_id: int) -> Merchant:
    with Session(engine) as session:
        db_merchant = session.get(DBMerchant, merchant_id)
        if db_merchant:
            return Merchant.from_orm(db_merchant)
    raise HTTPException(status_code=404, detail="Merchant not found")

@app.put("/merchants/{merchant_id}")
async def update_merchant(merchant_id: int, merchant: UpdatedMerchant) -> Merchant:
    data = merchant.dict()
    with Session(engine) as session:
        db_merchant = session.get(DBMerchant, merchant_id)
        db_merchant.sqlmodel_update(data)
        session.add(db_merchant)
        session.commit()
        session.refresh(db_merchant)
    return Merchant.from_orm(db_merchant)

@app.delete("/merchants/{merchant_id}")
async def delete_merchant(merchant_id: int) -> dict:
    with Session(engine) as session:
        db_merchant = session.get(DBMerchant, merchant_id)
        session.delete(db_merchant)
        session.commit()
    return dict(message=f"delete success")


class BaseTransaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_price = float
    quantity: int = 1

class CreatedTransaction(BaseTransaction):
    pass

class UpdatedTransaction(BaseTransaction):
    pass

class Transaction(BaseTransaction):
    id: int

class TransactionList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transactions: list[Transaction]
    page: int
    page_size: int
    size_per_page: int


class BaseWallet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    balance: float = 0.0

class CreateWallet(BaseWallet):
    pass

class UpdatedWallet(BaseWallet):
    pass

class Wallet(BaseWallet):
    id: int