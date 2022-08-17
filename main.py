from fastapi import FastAPI

from model.db import database, metadata, engine
from routers.notifications_router import notifications_router
from routers.tasks_router import tasks_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ORM

app.state.database = database
app.include_router(tasks_router)
app.include_router(notifications_router)

# metadata.create_all(engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()


@app.on_event("startup")
async def startup():
    database_ = app.state.database
    if not database_.is_connected:
        await database_.disconnect()
