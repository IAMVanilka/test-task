import os

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite+aiosqlite:///database.db")

metadata_obj = MetaData()

engine = create_async_engine(
    url=SQLALCHEMY_DATABASE_URL,
    echo=True
)

def create_tables():
    metadata_obj.create_all(engine)