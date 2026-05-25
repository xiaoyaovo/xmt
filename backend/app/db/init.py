from tortoise import Tortoise

from app.db.config import TORTOISE_ORM


async def init_db() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
