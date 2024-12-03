from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import router
from app.telegram_client import start_client, stop_client


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await start_client()

    yield

    await stop_client()


app = FastAPI(title="Stream Winx API", version="1.0.0", lifespan=lifespan)

app.include_router(router)
