from fastapi import FastAPI,  HTTPException

from .routers import init_router
from .models import init_db

from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select



def create_app():
        app = FastAPI()

        init_db()

        init_router(app)

        return app


