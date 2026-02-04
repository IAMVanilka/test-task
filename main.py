from fastapi import FastAPI

import uvicorn

from modules.db.database import create_tables
from modules.routers.main_routers import main_router, auth_router

app = FastAPI()
app.include_router(main_router)
app.include_router(auth_router)

if __name__ == "__main__":
    create_tables()
    uvicorn.run(app, host="0.0.0.0")