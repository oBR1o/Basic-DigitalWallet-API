from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.ext.asyncio.session import AsyncSession

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncIterator


from .items import *
from .merchants import *
from .transactions import *
from .wallets import *


connect_args = {}

engine = None

def init_db(settings):
    global engine
 
    engine = create_async_engine(
        settings.SQLDB_URL,
        #echo= True,
        future= True,
        connect_args=connect_args,
    )

async def create_all():
    async with engine.begin() as conn:
        #await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

async def recreate_table():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncIterator[AsyncSession]: # type: ignore
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session   

async def session_close():
    global engine
    if engine is None:
        raise Exception("DatabaseSessionManager is not initialized.")
    await engine.dispose()