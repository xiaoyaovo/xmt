from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.comment import router as comment_router
from app.api.v1.csv_files import router as csv_router
from app.api.v1.health import router as health_router
from app.api.v1.lol import router as lol_router
from app.api.v1.tool_sync import router as tool_sync_router
from app.api.v1.wedding import router as wedding_router

v1_router = APIRouter()
v1_router.include_router(auth_router, tags=["auth"])
v1_router.include_router(comment_router, tags=["comment"])
v1_router.include_router(csv_router, tags=["csv"])
v1_router.include_router(health_router, tags=["health"])
v1_router.include_router(lol_router, tags=["lol"])
v1_router.include_router(tool_sync_router, tags=["sync"])
v1_router.include_router(wedding_router, tags=["wedding"])
