from fastapi import APIRouter,  HTTPException, Depends

from typing import Optional, Annotated

from sqlmodel import Field, SQLModel, create_engine, Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from .. import models

router = APIRouter(prefix="/items", tags=["item"])

@router.post("")
async def create_item(
    item: models.CreatedItem,
    session: Annotated[AsyncSession, Depends(models.get_session)]   
) -> models.Item | None:
    data = item.dict()
    dbitem = models.DBItem(**data)
    session.add(dbitem)
    await session.commit()
    await session.refresh(dbitem)

    return models.Item.from_orm(dbitem)


@router.get("")
async def read_items(
    session: Annotated[AsyncSession, Depends(models.async_session)],
) -> models.ItemList:
    result = await session.exec(select(models.DBItem))
    items = result.all()

    return models.ItemList.from_orm(
        dict(items=items, page_size=0, page=0, size_per_page=0)
    )


@router.get("/{item_id}")
async def read_item(
    item_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)]
 ) -> models.Item:
        db_item = await session.get(models.DBItem, item_id)
        if db_item:
            return models.Item.from_orm(db_item)
        
        raise HTTPException(status_code=404, detail="Item not found")


@router.put("/{item_id}")
async def update_item(
    item_id: int, item: models.UpdatedItem,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    ) -> models.Item:
    print("updated_item", item)
    data = item.dict()
    db_item = await session.get(models.DBItem, item_id)
    db_item.sqlmodel_update(data)
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)

    return models.Item.from_orm(db_item)


@router.delete("/{item_id}")
async def delete_item(
     item_id: int, 
     session: Annotated[AsyncSession, Depends(models.get_session)]
     ) -> dict:
    db_item = await session.get(models.DBItem, item_id)
    await session.delete(db_item)
    await session.commit()
    
    return dict(message=f"delete success")