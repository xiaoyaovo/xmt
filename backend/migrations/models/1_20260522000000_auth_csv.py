from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `users` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `github_id` VARCHAR(64) NOT NULL UNIQUE,
    `username` VARCHAR(255) NOT NULL,
    `avatar_url` VARCHAR(1024),
    `email` VARCHAR(320),
    `last_login_at` DATETIME(6)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `csv_files` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `original_filename` VARCHAR(255) NOT NULL,
    `stored_filename` VARCHAR(255) NOT NULL,
    `storage_path` VARCHAR(1024) NOT NULL,
    `size` BIGINT NOT NULL,
    `content_type` VARCHAR(255),
    `columns` JSON NOT NULL,
    `row_count` INT NOT NULL DEFAULT 0,
    `delimiter` VARCHAR(8) NOT NULL DEFAULT ',',
    `status` VARCHAR(32) NOT NULL DEFAULT 'ready',
    `error_message` LONGTEXT,
    `expires_at` DATETIME(6) NOT NULL,
    `user_id` BIGINT NOT NULL,
    CONSTRAINT `fk_csv_file_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE INDEX `idx_csv_files_user_created` ON `csv_files` (`user_id`, `created_at`);
CREATE INDEX `idx_csv_files_expires` ON `csv_files` (`expires_at`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `csv_files`;
        DROP TABLE IF EXISTS `users`;"""


MODELS_STATE = (
    "eJztWu1v2jgY/1dQPnUSV7FAgZ1OJ1FGV24rnFp2N22aIpOYYDVxmOO05Sb+97OdhCTOyx"
    "EKFHr5Bs9LbP8e+3mzfyq2Y0DLPe+7D1fIgsqvtZ8KBjb/IbPqNQUsFhGDEyiYCiVFdx+0"
    "GZMSVDB1KQE6ZYwZsFzISAZ0dYIWFDmYUbFnWZzo6EwQYTMieRj98KBGHRPSOSSM8e07Iy"
    "NswCf28eDv4p4NBi0jMV1k8LEFXaPLhaBdInOI6ZWQ5QNONd2xPBtH8oslnTt4rYAw5VQT"
    "YkgAhXwESjy+Aj7BYLXhovzJRiL+LGM6BpwBz6KxFW8Ig+5gDiGbjSvWaPJRfnmnqs1mR2"
    "00292LVqdz0W10mayYUprVWfkLjgDxPyVgGX4YjiZ8oQ6zk29BTlgJHUCBryXwjgDWCeSQ"
    "aICmgX7POBTZMBvqpKYEuRGonoc/ZAOEcBdZICREJoh23o5swNZgjLG1DMxbAO9keDO4m/"
    "Ru/uQrsV33hyUg6k0GnKMK6lKinrXfJO2x/kjt7+Hkusb/1r6ORwOBoONSk4gRI7nJV4XP"
    "CXjU0bDzqAEjthNDaggMk4wM6y2MLQ2b1KwM+6KGDSYf2dUhyEQYWMIzC2LKvP05INmmzV"
    "SWLMxgPFKb2uBJY9M26Zz9VS8uCoz6V++2f927PWNSkqVGAUv1easEuC51CNv520CboVoB"
    "mwAWmFBbADZGSVTjeqcJ6duG2toAUy6WC6rPlFBF/2Ts0aL8KNT47wzpSHA8YJIUS4ocTC"
    "GmPjwldqust9VuDWLA6zr/PkZuGsw/7sajPDDXKhKOnzFb4DcD6bRes5BLv+9r7yq/zTys"
    "czhrUw9ZFGH3nA/4u7I92AXYciwSSUgI6dlN74uMdv/T+FLOLvgHLiXkCUsudMfDGWlgrp"
    "dI6BzOVTSe7SfUt61Oq9tst9buYU0p8gppD8BqYWQjCkmZ459QOlykUurP2I7Js9/d4OR3"
    "c899Nx31AfUyDn1RvA81DogfrxWWO8OwqW4AYlPNRZGzkjBCQhyi2dB1WSqURnMCn3LOcU"
    "rxRAJSUbU2+DIp9pHrYu3TePQhFJcdpwTw0wIxF7pFrZzUPM1a+URq43DZxV0PFxKtbNMw"
    "plTlxXJezFuzs/vM3iHHLY30FauDkYk/wqVAe8jmDbCe5X6CXvTn4DPHh/Iq3CkhNfKGBD"
    "yu29XxDcSWxxYFqR/nenf93vuBIkCcAv3+ERBDS6DJOY7qSJS1bJplq7ZMAZi5dyNYBZ9z"
    "AOw1BBad9+dQv7+FukOSrfVcoXrRncBciGs6l9eIUKiuB6rrgep64IgiZXU98L8xbOp6oG"
    "zbere96r07Ramt2tioq9ooaKo23mTlOC8Tr0UilBGiwwQpPyrzBKQKw1UYrsLwUXvrKgy/"
    "UsOmwrCJ6NybZnYi8mNxQukUA3J7k1vOdv4dZzt1w8kDW9mUJq5zmvfFe7mCAw8suhDNI1"
    "YZMJNaJ9I/PsztO7QBKoXlWuEkYWyqm2TbTKrgZqMhY2gBl2qWYyK8RQhMKe8gCh7XZccR"
    "Bb3c9nuJ4imW0MafFkuFQ6B69fEWWkCgmTZt+hnz8fn0vO7xap81ZA8SpM+VjCoy4NSL6k"
    "gQyRxNIfmKqshnPk/Irw8fWPkfHJRNg1FMpUqSoiSJHY0y2ZEvfpoA7qx9lvF0Lg1i0UOv"
    "tcpLPfTaWwTf2ZOuF21Rrv4F+Eyu9A=="
)
