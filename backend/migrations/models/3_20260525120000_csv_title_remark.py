from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `csv_files`
            ADD COLUMN `title` VARCHAR(255) NULL,
            ADD COLUMN `remark` LONGTEXT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `csv_files`
            DROP COLUMN `remark`,
            DROP COLUMN `title`;"""
