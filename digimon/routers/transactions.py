from fastapi import APIRouter,  HTTPException, Depends

from typing import Optional, Annotated

from sqlmodel import Field, SQLModel, create_engine, Session, select
from sqlmodel.ext.asyncio.session import AsyncSession   

from .. import security
from .. import deps
from .. import models


router = APIRouter(prefix="/transactions", tags=["transaction"])

@router.post("/{wallet_id}/{item_id}")
async def create_transaction(
    transaction: models.CreatedTransaction, 
    wallet_id: int, 
    item_id: int,
    quantity_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[AsyncSession, Depends(deps.get_current_activate_user)],
    ) -> models.Transaction:
    print("created_merchant", transaction)
    data = transaction.dict()
    db_transaction = models.DBTransaction(**data)
    db_transaction.wallet_id = wallet_id
    db_transaction.item_id = item_id
    db_transaction.quantity = quantity_id

    db_wallet = await session.get(models.DBWallet, wallet_id)
    db_item = await session.get(models.DBItem, item_id)
    if db_wallet is None or db_item is None:
        raise HTTPException(status_code=404, detail="Wallet or Item not found")
        
    total_price = db_item.price * quantity_id
    if db_wallet.balance < total_price:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    db_item.quantity -= quantity_id
    db_item.sqlmodel_update(db_item.dict())
        
    db_wallet.balance -= total_price
    db_wallet.sqlmodel_update(db_wallet.dict())

    db_transaction.total_price = total_price

    session.add(db_transaction)
    await session.commit()
    await session.refresh(db_transaction)

    return models.Transaction.from_orm(db_transaction)


@router.get("/{wallet_id}")
async def read_transactions(
    wallet_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[AsyncSession, Depends(deps.get_current_activate_user)],
    ) -> models.TransactionList:
    transactions = await session.exec(
        select(models.DBTransaction).where(models.DBTransaction.wallet_id == wallet_id)
    ).all()

    return models.TransactionList(
        transactions=transactions,
        page=1,
        page_size=len(transactions),
        size_per_page=len(transactions),
    )


@router.get("/{transaction_id}")
async def read_transaction(
    transaction_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[AsyncSession, Depends(deps.get_current_activate_user)],
    ) -> models.Transaction:
    db_transaction = await session.get(models.DBTransaction, transaction_id)
    if db_transaction:
        return models.Transaction.from_orm(db_transaction)
    raise HTTPException(status_code=404, detail="Transaction not found")


@router.put("/{transaction_id}")
async def update_transaction(
    transaction_id: int, 
    transaction: models.UpdatedTransaction,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[AsyncSession, Depends(deps.get_current_activate_user)],
    ) -> models.Transaction:
    print("updated_transaction", transaction)
    data = transaction.dict()
    db_transaction = await session.get(models.DBTransaction, transaction_id)
    db_transaction.sqlmodel_update(data)
    session.add(db_transaction)
    await session.commit()
    await session.refresh(db_transaction)

    return models.Transaction.from_orm(db_transaction)


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[AsyncSession, Depends(deps.get_current_activate_user)],
    ) -> dict:
    db_transaction = await session.get(models.DBTransaction, transaction_id)
    await session.delete(db_transaction)
    await session.commit()
    return dict(message=f"delete success")