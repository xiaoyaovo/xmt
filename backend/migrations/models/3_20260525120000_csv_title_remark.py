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


MODELS_STATE = (
    "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"
    "SHjVN4OefwFcrnaG"
)
