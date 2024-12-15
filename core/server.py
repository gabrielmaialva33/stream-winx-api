from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

from api import router
from app.repositories import telegram_repository


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await telegram_repository.start_client()

    yield

    await telegram_repository.stop_client()


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

    app_.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Aqui você pode especificar as origens permitidas, como ["http://localhost:3000"]
        allow_credentials=True,  # Permitir envio de cookies e headers de autenticação
        allow_methods=["*"],  # Permitir todos os métodos HTTP, como GET, POST, PUT
        allow_headers=["*"],  # Permitir todos os headers
    )

    init_routers(app_)

    app_.mount("/static", StaticFiles(directory="static"), name="static")

    @app_.get("/", include_in_schema=False)
    async def redoc_html():
        with open("static/doc/doc.html", "r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content, status_code=200)

    return app_


app = create_app()
