from fastapi import APIRouter,  HTTPException

from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select

from ..models import (
    Merchant,
    CreatedMerchant,
    UpdatedMerchant,
    MerchantList,
    DBMerchant,
    engine,
)

router = APIRouter(prefix="/merchants", tags=["merchant"])

@router.post("")
async def create_merchant(merchant: CreatedMerchant) -> Merchant:
    print("created_merchant", merchant)
    data = merchant.dict()
    dbmerchant = DBMerchant(**data)
    with Session(engine) as session:
        session.add(dbmerchant)
        session.commit()
        session.refresh(dbmerchant)

    return Merchant.from_orm(dbmerchant)


@router.get("")
async def read_merchants(page: int = 1, page_size: int = 10) -> MerchantList:
    with Session(engine) as session:
        merchants = session.exec(select(DBMerchant).offset((page - 1) * page_size).limit(page_size)).all()
    return MerchantList.from_orm(dict(merchants=merchants, page_size=0, page=0, size_per_page=0))


@router.get("/{merchant_id}")
async def read_merchant(merchant_id: int) -> Merchant:
    with Session(engine) as session:
        db_merchant = session.get(DBMerchant, merchant_id)
        if db_merchant:
            return Merchant.from_orm(db_merchant)
    raise HTTPException(status_code=404, detail="Merchant not found")


@router.put("/{merchant_id}")
async def update_merchant(merchant_id: int, merchant: UpdatedMerchant) -> Merchant:
    print("updated_merchant", merchant)
    data = merchant.dict()
    with Session(engine) as session:
        db_merchant = session.get(DBMerchant, merchant_id)
        db_merchant.sqlmodel_update(data)
        session.add(db_merchant)
        session.commit()
        session.refresh(db_merchant)

    return Merchant.from_orm(db_merchant)


@router.delete("/{merchant_id}")
async def delete_merchant(merchant_id: int) -> dict:
    with Session(engine) as session:
        db_merchant = session.get(DBMerchant, merchant_id)
        session.delete(db_merchant)
        session.commit()
    return dict(message=f"delete success")