import os

from sqlalchemy import create_engine, MetaData

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///database.db")

metadata_obj = MetaData()

engine = create_engine(
    url=SQLALCHEMY_DATABASE_URL
)

def create_tables():
    metadata_obj.create_all(engine)