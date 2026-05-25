from contextlib import asynccontextmanager

from fastapi import FastAPI
from tortoise import Tortoise

from app.api import api_router
from app.core.middlewares import apply_middlewares
from app.db.init import init_db
from app.settings.config import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield
    await Tortoise.close_connections()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.app_debug,
        lifespan=lifespan,
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.include_router(api_router, prefix="/api")
    return apply_middlewares(app)


app = create_app()
