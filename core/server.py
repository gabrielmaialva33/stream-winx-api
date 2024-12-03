from contextlib import asynccontextmanager

from fastapi import FastAPI

from api import router
from core.integrations import telegram


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await telegram.start()

    yield

    await telegram.stop()


def init_routers(app_: FastAPI) -> None:
    app_.include_router(router)


def create_app() -> FastAPI:
    app_ = FastAPI(
        title="CineWinx API",
        description="API to index and stream content from telegram channels",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    init_routers(app_)

    return app_


app = create_app()
