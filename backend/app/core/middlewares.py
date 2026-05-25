from fastapi.middleware.cors import CORSMiddleware

from app.settings.config import settings


def apply_middlewares(app):
    return CORSMiddleware(
        app,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
