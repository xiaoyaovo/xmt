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
