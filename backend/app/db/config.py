from app.settings.config import settings

TORTOISE_ORM = {
    "connections": {
        "default": settings.mysql_url,
    },
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai",
}
