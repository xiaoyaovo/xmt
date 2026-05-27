from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users`
            ADD COLUMN `email_verified` BOOL NOT NULL DEFAULT 0;
        UPDATE `users`
            SET `email_verified` = 1
            WHERE `auth_provider` IN ('github', 'linuxdo') AND `email` IS NOT NULL;
        CREATE TABLE IF NOT EXISTS `verification_codes` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `email` VARCHAR(255) NOT NULL,
    `code_hash` VARCHAR(255) NOT NULL,
    `purpose` VARCHAR(32) NOT NULL,
    `attempts` INT NOT NULL DEFAULT 0,
    `expires_at` DATETIME(6) NOT NULL,
    `consumed_at` DATETIME(6),
    KEY `idx_verification_codes_email` (`email`)
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `verification_codes`;
        ALTER TABLE `users`
            DROP COLUMN `email_verified`;"""
