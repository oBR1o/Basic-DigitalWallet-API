from fastapi import APIRouter,  HTTPException

from sqlmodel import Field, SQLModel, create_engine, Session, select

from ..models import (
    Wallet,
    CreatedWallet,
    UpdatedWallet,
    DBWallet,
    engine,
)

router = APIRouter(prefix="/wallets", tags=["wallet"])

@router.post("/{merchant_id}")
async def create_wallet(wallet: CreatedWallet, merchant_id: int) -> Wallet:
    print("created_wallet", wallet)
    data = wallet.dict()
    dbwallet = DBWallet(**data)
    dbwallet.merchant_id = merchant_id
    with Session(engine) as session:
        session.add(dbwallet)
        session.commit()
        session.refresh(dbwallet)

    return Wallet.from_orm(dbwallet)

@router.get("/{wallet_id}")
async def read_wallet(wallet_id: int) -> Wallet:
    with Session(engine) as session:
        db_wallet = session.get(DBWallet, wallet_id)
        if db_wallet:
            return Wallet.from_orm(db_wallet)
    raise HTTPException(status_code=404, detail="Wallet not found")


@router.put("/{wallet_id}")
async def update_wallet(wallet_id: int, wallet: UpdatedWallet) -> Wallet:
    print("updated_wallet", wallet)
    with Session(engine) as session:
        db_wallet = session.get(DBWallet, wallet_id)
        if db_wallet is None:
            raise HTTPException(status_code=404, detail="Item not found")
        for key, value in wallet.dict().items():
            setattr(db_wallet, key, value)


        session.add(db_wallet)
        session.commit()
        session.refresh(db_wallet)

    return Wallet.from_orm(db_wallet)


@router.delete("/{wallet_id}")
async def delete_merchant(merchant_id: int) -> dict:
    with Session(engine) as session:
        db_wallet = session.get(DBWallet, merchant_id)
        session.delete(db_wallet)
        session.commit()
    return dict(message=f"delete success")