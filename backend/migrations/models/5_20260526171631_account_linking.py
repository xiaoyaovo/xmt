from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `user_auth_accounts` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `provider` VARCHAR(32) NOT NULL,
    `provider_user_id` VARCHAR(128) NOT NULL,
    `provider_username` VARCHAR(255),
    `provider_email` VARCHAR(320),
    `avatar_url` VARCHAR(1024),
    `password_hash` VARCHAR(255),
    `linked_at` DATETIME(6),
    `last_used_at` DATETIME(6),
    `user_id` BIGINT NOT NULL,
    UNIQUE KEY `uid_user_auth_a_provide_86ac3d` (`provider`, `provider_user_id`),
    UNIQUE KEY `uid_user_auth_a_user_id_9eec9c` (`user_id`, `provider`),
    CONSTRAINT `fk_user_aut_users_f5ea857c` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;

        INSERT IGNORE INTO `user_auth_accounts` (
            `created_at`,
            `updated_at`,
            `provider`,
            `provider_user_id`,
            `provider_username`,
            `provider_email`,
            `avatar_url`,
            `password_hash`,
            `linked_at`,
            `last_used_at`,
            `user_id`
        )
        SELECT
            `created_at`,
            `updated_at`,
            `auth_provider`,
            `provider_user_id`,
            `username`,
            `email`,
            `avatar_url`,
            `password_hash`,
            COALESCE(`last_login_at`, `created_at`),
            `last_login_at`,
            `id`
        FROM `users`
        WHERE `provider_user_id` IS NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `user_auth_accounts`;"""


MODELS_STATE = (
    "eJztXG1v2zYQ/iuGP7WAV7hyXrxhGOCmSeutTYbE3YoWhcBIjE1YJl2KSuIV+e8jqXdR0i"
    "xHsi2P32zyTiSf48vdc5R+dBfEho776sy9v0AO7P7S+dHFYCF+ZKt6nS5YLuMKUcDArVTq"
    "Wu69ecelZCm4dRkFFuMVd8BxIS+yoWtRtGSIYF6KPccRhcTigghP4yIPo+8eNBmZQjaDlF"
    "d8/caLEbbhI3948Hc5541Bx051F9mibVlustVSlr1B0zFmF1JWNHhrWsTxFjiWX67YjOBI"
    "AWEmSqcQQwoYFC0w6okRiA4Gow0H5Xc2FvF7mdCx4R3wHJYY8ZowWAQLCHlvXDnGqWjlp5"
    "8NYzA4NfqDk+Hx0enp8bA/5LKyS2rV6ZM/4BgQ/1ESlvG78eVEDJRwO/kWFAVPUgcw4GtJ"
    "vGOALQoFJCZgKtBveQ1DC5gPdVozA7kdqL4Kf2QNEMJdZoGwIDZBPPNqsgEfg32FnVVg3h"
    "J4J+OP5zeT0cc/xUgWrvvdkRCNJueixpClq0zpi5OXaXtED+n8PZ6874i/nS9Xl+cSQeKy"
    "KZUtxnKTL13RJ+AxYmLyYAI7MRPD0hAYLhkb1lvaGxo2rakNu1PDBp2P7UoomiIMHLkzy0"
    "LFvGczQPNNm6ucsTCHcU9tugCPJu/2lM34X+P4uMSof42uz96Prl9wqYylLoMqw697SoHr"
    "MkL5zN8E2hxVDWwKWDCF5hLwNiqimtRrJ6Sv+8bRGpgKsUJQ/coMquifnDla5h+FGv/tIe"
    "0Jjlt0khJOEcEMYubDU2G2ZvU2mq3BGXBY69/HyFXB/P3m6rIIzEglg+MnzAf41UYW63Uc"
    "5LJvTc3d7q93HrYEnJ1bDzkMYfeVaPC37uZgl2ArsEg5ISGkLz6OPmfRPvtw9SbrXYgHvM"
    "kgT7lzYREP57iBhbtESmd7W0X/2fuE8fro9Gg4ODmKtoeopGxXUHcAHgujBWKQVln+KaXt"
    "nVTd3jOmY3rtD9dY+cPCdT9UT33AvJxFX3behxpbxE/ECqvaMBwYa4A4MApRFFVpGCGlhJ"
    "oL6LrcFVLRnMDHgnWsKLbkQCqL1s4/T8r3yChY+3B1+S4Uz26cGYAfl4hvoRvEymnNdsbK"
    "LYmNw2GXsh4MMaeSyxYptGRpbMFXo3AB6LzKPhNrtATFbW8wngupWZXLTijpcC0bromMwd"
    "08l9IWuKlIXxAK0RT/AVcS7THvN8BW3tIPUiSfgsfsH8pP4UwJS+M1RMFDlEVJTiA+PD4o"
    "yPzdcHRzNnp73pUg3gJr/gCobabQFDXEIJmSSFatWhiLbAnA3Ouwg1GIPgfAvofAYbOzGb"
    "Tm19AiNJ3xKRTqlaWqZlLctIS8SaWCzlrprJXOWu2RA6ezVv8bwypZq6rZlHpTKI1vihm2"
    "v78W2d8v4fr7L/N8nN2c1xNCnJsVtsYMLvKO6lR96SnNuKTpclETcdkGDuivkfMnm5pDSe"
    "uIxuTvb/oA1we43uf1Aa4NW/UAT+6na3NrCZ12Ju5P1knbnxQn7U+UlH10FlXAManTThxf"
    "G+tklrhUsUtkKNklzfU+n+tdgpVDQI63U5yXT6jsU15eNNumvLymhOv2NzUl3FpKWAKbE1"
    "qGgBeHlGJAjQSS3BmamUtK7pEdXOgIfpshhjqa1NHkPqz9gwk6dDR5oIZVoskpYjPvNtf9"
    "KXbfU0q1uPDb5YXrDyaVM2pdKNXDbXu37XwzPsNTb/q6nXLQVwA2T7eV0WYjEbsApWomKK"
    "nTTvKjocDddR8I97tnwK30Ro2i2Mrp2Qim4J47mHzpUqfSXprSaiWaTb2fBBcAVcIyUmgl"
    "jANjncQvlyo5jPpZDB3gMtMhU4Q38IIV5Roc4f26rblHfm/hBeUKefxETJv8+EKGOwhUL/"
    "64hg6QaKqmVT/0sH/nZBFrpWae0pcGNocje1ehpZhI/x1Y8h2tZyIiKLYRf9zIit74ahEo"
    "TZOSSWQK+MkMeOVUpalYrm7espyy7HXiKzKRpCYyNZG5D6v8YPguTWQeqGGVg3gT8m03vF"
    "u9gc5Bcm47x7UR0i0FT1X2LVe5lcF5MyxcCE9lpkPVbCWqjVAemoermYfTZHH9S99BeL6R"
    "Q5dS1Hzcjj8YIBlSfrhtZMmMrjbmjo2p71T29J1KfafSB3YEKbJm3RzWMqjplZGVIJbZm1"
    "foD4hnfOaHyooZxHtI3YDvX9fJS6i0M2xu5jIAXxoVQAzE2wlgbW8s53xEUwWx7JOPkcqu"
    "Xi1pzJmq7SWSnb4V/vQvOdHT5Q=="
)
