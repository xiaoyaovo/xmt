from fastapi.middleware.cors import CORSMiddleware

from app.settings.config import settings


def build_middlewares() -> list[dict]:
    return [
        {
            "cls": CORSMiddleware,
            "kwargs": {
                "allow_origins": settings.cors_origin_list,
                "allow_credentials": True,
                "allow_methods": ["*"],
                "allow_headers": ["*"],
            },
        }
    ]
