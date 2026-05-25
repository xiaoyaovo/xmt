from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `health_check_records` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(100) NOT NULL UNIQUE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztVmtv2jAU/SuIT0zqKhqe2zdgbDCtMFH2UKsqMolJLBw7dZy1qOK/z9dJMAmPtRVbu2"
    "mfkpx7bnzvObFv7ssBdzGNTgcYUen3fOwsJtjhwi2/Ld2XGQqwutlPOimVURgaCgASzajO"
    "8jXddoBvC52gCWgWSYEcqThzRCOsIBdHjiChJJwplMWUAsgdRSTMM1DMyE2Mbck9LH0sVO"
    "DqWsGEufgOR9ljuLDnBNN8D0RXq3FbLkONdYk3ZPK95sKCM9vhNA6Y4YdL6XO2TiBMAuph"
    "hgWSGFaQIoYOoMC08ayppFhDSarcyHHxHMVUbnT8QBkczkBCVU2ke/RglddvLKtWa1nVWr"
    "PdqLdajXa1rbi6pO1Qa5U0bARJXqVlGX4YjqbQKFc+JWYCsNI5SKIkS+ttBHYEBklsJLeF"
    "fqcikgR4t9T5zILkbpp6mt0UDcjkPuRABhgLzJd3JA9UD+6Y0WVq7wF5p8Pz/sW0c/4ZOg"
    "mi6IZqiTrTPkQsjS4LaKX5Ku/H+iWlb8PpoASPpcvxqK8V5JH0hF7R8KaXZagJxZLbjN/a"
    "yN34EjM0E0YxjbFx6D7R2Hzmf2Of1di0eOOrvm452vOR2O1mxi/4qMR6inO//VAM0J1NMf"
    "Okrx7PqtUDxn3tTHqDzqSiWAU3RmnISmKrFcyX+WLjAARghpzFLRKuvRXhFt/H3Q4FVlBE"
    "EEOeVgeahA7SUdzBgjj+riGdRg5OZmQ4L2YW/0OD2Dqrt+rtWrO+nr9r5NDY/fWI/YFFBC"
    "U9YtNupBxn3/6BEze3c61G4wE7V7H27lwdW+WOPtgajxAxpf+dAh7t6NsUUK0oMdvxQ/Dx"
    "Yjza85dnUgpCfmGqwSuXOPKkREkkr1+mrAdUhK5zQz8Tr3Le+V7Utfdp3C1Oc3hB97nHy+"
    "onJqx6aQ=="
)
