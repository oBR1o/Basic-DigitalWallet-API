from fastapi import APIRouter,  HTTPException, Depends

from typing import Optional, Annotated

from sqlmodel import Field, SQLModel, create_engine, Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from .. import models

router = APIRouter(prefix="/merchants", tags=["merchant"])

@router.post("")
async def create_merchant(
    merchant: models.CreatedMerchant,
    session: Annotated[AsyncSession,Depends(models.get_session)], 
    ) -> models.Merchant:
    print("created_merchant", merchant)
    data = merchant.dict()
    dbmerchant = models.DBMerchant(**data)
    session.add(dbmerchant)
    await session.commit()
    await session.refresh(dbmerchant)

    return models.Merchant.from_orm(dbmerchant)


@router.get("")
async def read_merchants(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    page: int = 1, 
    page_size: int = 10,
    ) -> models.MerchantList:
    result = await session.exec(select(models.DBMerchant).offset((page - 1) * page_size).limit(page_size))
    merchants = result.all()
    return models.MerchantList.from_orm(dict(merchants=merchants, page_size=0, page=0, size_per_page=0))


@router.get("/{merchant_id}")
async def read_merchant(
    merchant_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    ) -> models.Merchant:
    db_merchant = await session.get(models.DBMerchant, merchant_id)
    if db_merchant:
        return models.Merchant.from_orm(db_merchant)
    raise HTTPException(status_code=404, detail="Merchant not found")


@router.put("/{merchant_id}")
async def update_merchant(
    merchant_id: int, 
    merchant: models.UpdatedMerchant,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    ) -> models.Merchant:
    print("updated_merchant", merchant)
    data = merchant.dict()
    db_merchant = await session.get(models.DBMerchant, merchant_id)
    db_merchant.sqlmodel_update(data)
    session.add(db_merchant)
    await session.commit()
    await session.refresh(db_merchant)

    return models.Merchant.from_orm(db_merchant)


@router.delete("/{merchant_id}")
async def delete_merchant(
    merchant_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    ) -> dict:
    db_merchant = await session.get(models.DBMerchant, merchant_id)
    await session.delete(db_merchant)
    await session.commit()

    return dict(message=f"delete success")