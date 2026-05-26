from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users`
            MODIFY COLUMN `github_id` VARCHAR(64) NULL,
            ADD COLUMN `auth_provider` VARCHAR(32) NOT NULL DEFAULT 'github',
            ADD COLUMN `provider_user_id` VARCHAR(128) NULL,
            ADD COLUMN `password_hash` VARCHAR(255) NULL;
        UPDATE `users`
            SET `auth_provider` = 'github',
                `provider_user_id` = `github_id`
            WHERE `provider_user_id` IS NULL AND `github_id` IS NOT NULL;
        CREATE UNIQUE INDEX `uid_users_provider_user` ON `users` (`auth_provider`, `provider_user_id`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX `uid_users_provider_user` ON `users`;
        ALTER TABLE `users`
            DROP COLUMN `password_hash`,
            DROP COLUMN `provider_user_id`,
            DROP COLUMN `auth_provider`,
            MODIFY COLUMN `github_id` VARCHAR(64) NOT NULL UNIQUE;"""


MODELS_STATE = (
    "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"
    "TP/wLHfc9d"
)
