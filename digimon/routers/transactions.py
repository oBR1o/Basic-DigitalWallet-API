from fastapi import APIRouter,  HTTPException

from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select

from ..models import (
    Transaction,
    CreatedTransaction,
    UpdatedTransaction,
    TransactionList,
    DBTransaction,
    DBItem,
    DBWallet,
    engine,
)

router = APIRouter(prefix="/transactions", tags=["transaction"])

@router.post("/{wallet_id}/{item_id}")
async def create_transaction(transaction: CreatedTransaction, wallet_id: int, item_id: int) -> Transaction:
    print("created_merchant", transaction)
    data = transaction.dict()
    db_transaction = DBTransaction(**data)
    db_transaction.wallet_id = wallet_id
    db_transaction.item_id = item_id

    with Session(engine) as session:
        db_wallet = session.get(DBWallet, wallet_id)
        db_item = session.get(DBItem, item_id)
        if db_wallet is None or db_item is None:
            raise HTTPException(status_code=404, detail="Wallet or Item not found")
        
        total_price = db_item.price * db_transaction.quantity
        if db_wallet.balance < total_price:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        db_wallet.balance -= total_price
        db_wallet.sqlmodel_update(db_wallet.dict())

        db_transaction.total_price = total_price

        session.add(db_transaction)
        session.commit()
        session.refresh(db_transaction)

    return Transaction.from_orm(db_transaction)


@router.get("/{wallet_id}")
async def read_transactions(wallet_id: int) -> TransactionList:
    with Session(engine) as session:
        transactions = session.exec(select(DBTransaction).where(DBTransaction.wallet_id == wallet_id)).all()
    return TransactionList(
        transactions=transactions,
        page=1,
        page_size=len(transactions),
        size_per_page=len(transactions),
    )


@router.get("/{transaction_id}")
async def read_transaction(transaction_id: int) -> Transaction:
    with Session(engine) as session:
        db_transaction = session.get(DBTransaction, transaction_id)
        if db_transaction:
            return Transaction.from_orm(db_transaction)
    raise HTTPException(status_code=404, detail="Transaction not found")


@router.put("/{transaction_id}")
async def update_transaction(transaction_id: int, transaction: UpdatedTransaction) -> Transaction:
    print("updated_transaction", transaction)
    data = transaction.dict()
    with Session(engine) as session:
        db_transaction = session.get(DBTransaction, transaction_id)
        db_transaction.sqlmodel_update(data)
        session.add(db_transaction)
        session.commit()
        session.refresh(db_transaction)

    return Transaction.from_orm(db_transaction)


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int) -> dict:
    with Session(engine) as session:
        db_transaction = session.get(DBTransaction, transaction_id)
        session.delete(db_transaction)
        session.commit()
    return dict(message=f"delete success")