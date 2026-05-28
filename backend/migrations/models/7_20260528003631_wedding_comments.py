from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `comments` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `target_type` VARCHAR(32) NOT NULL,
    `target_id` VARCHAR(128) NOT NULL,
    `author_name` VARCHAR(64) NOT NULL,
    `author_relation` VARCHAR(64),
    `author_avatar` VARCHAR(512),
    `author_anon_id` VARCHAR(64) NOT NULL,
    `content` LONGTEXT NOT NULL,
    `like_count` INT NOT NULL DEFAULT 0,
    `reply_count` INT NOT NULL DEFAULT 0,
    `parent_id` BIGINT,
    `reply_to_id` BIGINT,
    CONSTRAINT `fk_comments_comments_ab2e55ce` FOREIGN KEY (`parent_id`) REFERENCES `comments` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_comments_comments_54a8aaa9` FOREIGN KEY (`reply_to_id`) REFERENCES `comments` (`id`) ON DELETE SET NULL,
    KEY `idx_comments_target__24adbc` (`target_type`),
    KEY `idx_comments_target__a210bd` (`target_id`),
    KEY `idx_comments_author__f307f7` (`author_anon_id`)
) CHARACTER SET utf8mb4 COMMENT='通用评论 — 通过 (target_type, target_id) 关联到任意业务对象。';
        CREATE TABLE IF NOT EXISTS `comment_likes` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `anon_id` VARCHAR(64) NOT NULL,
    `comment_id` BIGINT NOT NULL,
    UNIQUE KEY `uid_comment_lik_comment_d0ebf8` (`comment_id`, `anon_id`),
    CONSTRAINT `fk_comment__comments_11dc9371` FOREIGN KEY (`comment_id`) REFERENCES `comments` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='一个 anon_id 对一个 comment 只能点赞一次。';
        CREATE TABLE IF NOT EXISTS `wedding_rsvps` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(64) NOT NULL,
    `attendance` VARCHAR(8) NOT NULL,
    `guests` INT NOT NULL DEFAULT 1,
    `message` LONGTEXT
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `comments`;
        DROP TABLE IF EXISTS `comment_likes`;
        DROP TABLE IF EXISTS `wedding_rsvps`;"""


MODELS_STATE = (
    "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"
)
