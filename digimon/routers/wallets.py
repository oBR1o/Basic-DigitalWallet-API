from fastapi import APIRouter,  HTTPException, Depends

from typing import Optional, Annotated

from sqlmodel import Field, SQLModel, create_engine, Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from .. import models

router = APIRouter(prefix="/wallets", tags=["wallet"])

@router.post("/{merchant_id}")
async def create_wallet(
    wallet: models.CreatedWallet, 
    merchant_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    ) -> models.Wallet:
    print("created_wallet", wallet)
    data = wallet.dict()
    dbwallet = models.DBWallet(**data)
    dbwallet.merchant_id = merchant_id
    dbmerchant = await session.get(models.DBMerchant, merchant_id)
    dbwallet.merchant_name = dbmerchant.name
    session.add(dbwallet)
    await session.commit()
    await session.refresh(dbwallet)

    return models.Wallet.from_orm(dbwallet)

@router.get("/{wallet_id}")
async def read_wallet(
    wallet_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    ) -> models.Wallet:
    db_wallet = await session.get(models.DBWallet, wallet_id)
    if db_wallet:
        return models.Wallet.from_orm(db_wallet)
    raise HTTPException(status_code=404, detail="Wallet not found")


@router.put("/{wallet_id}")
async def update_wallet(
    wallet_id: int, 
    wallet: models.UpdatedWallet,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    ) -> models.Wallet:
    print("updated_wallet", wallet)
    db_wallet = await session.get(models.DBWallet, wallet_id)
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in wallet.dict().items():
        setattr(db_wallet, key, value)


    session.add(db_wallet)
    await session.commit()
    await session.refresh(db_wallet)

    return models.Wallet.from_orm(db_wallet)


@router.delete("/{wallet_id}")
async def delete_merchant(
    merchant_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    ) -> dict:
    db_wallet = await session.get(models.DBWallet, merchant_id)
    await session.delete(db_wallet)
    await session.commit()
    return dict(message=f"delete success")