from tortoise import Tortoise

from app.db.config import TORTOISE_ORM
from app.settings.config import settings


async def init_db() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    try:
        conn = Tortoise.get_connection("default")
        await conn.execute_query("SELECT 1")
    except Exception as exc:
        await Tortoise.close_connections()
        raise RuntimeError(
            f"无法连接到 MySQL ({settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}),"
            "请确认数据库已启动且配置正确"
        ) from exc
