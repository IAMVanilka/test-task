import uvicorn

from fastapi import FastAPI
from contextlib import asynccontextmanager

from modules.db.database import engine, metadata_obj
from modules.routers.main_routers import main_router, auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(metadata_obj.create_all)

    yield

    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(main_router)
app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")