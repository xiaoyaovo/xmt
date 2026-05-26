from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `tool_sync_items` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `tool_key` VARCHAR(64) NOT NULL,
    `item_key` VARCHAR(128) NOT NULL,
    `title` VARCHAR(255),
    `payload` JSON NOT NULL,
    `user_id` BIGINT NOT NULL,
    CONSTRAINT `fk_tool_sync_items_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uid_tool_sync_user_tool_item` (`user_id`, `tool_key`, `item_key`)
) CHARACTER SET utf8mb4;
CREATE INDEX `idx_tool_sync_user_tool_updated` ON `tool_sync_items` (`user_id`, `tool_key`, `updated_at`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `tool_sync_items`;"""


MODELS_STATE = (
    "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"
    "Y="
)
