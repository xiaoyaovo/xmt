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


MODELS_STATE = (
    "eJztXW2P2jgQ/iuIT63EVTTsCz2dTmLpbsu1u5x2aa9qVUUm8YJFXqjjsMtV+9/PNnl3kkvYBAj1N7BnkvgZ2zPz"
    "jAk/26atQ8N5NXRWV8iA7d9bP9sWMNmHZFen1QbLZdjBGgiYcqW25qzUeyrFW8HUIRhohHbcA8OBtEmHjobRkiDb"
    "oq2Waxis0daoILJmYZNroR8uVIk9g2QOMe349p02I0uHj/Ti3tflgt4MGnrscZHO7s3bVbJe8rYLNBtZ5IrLshtO"
    "Vc02XNMK5ZdrMretQAFZhLXOoAUxIJDdgWCXjYA9oDdaf1Cbhw1FNk8Z0dHhPXANEhlxQRg022IQ0qdx+Bhn7C6/"
    "vVGUXu9c6fbO+qcn5+en/W6fyvJHErvOnzYDDgHZXIrDMno3upmwgdrUThsLsoYnrgMI2GhxvEOANQwZJCogItBv"
    "aQ9BJkyHOq6ZgFz3VF/5H5IG8OHOs4DfEJognHkV2YCOQR9bxtozbw68k9H15d1kcP03G4npOD8MDtFgcsl6FN66"
    "TrS+OHsZt0dwkdY/o8n7Fvva+jq+ueQI2g6ZYX7HUG7ytc2eCbjEVi37QQV6ZCb6rT4wVDI0rLvUtzRsXFMadq+G"
    "9R4+tKuN0QxZwOA7M28UzDucA5xu2lTlhIUpjAdqUxM8qvSxZ2ROvyqnpzlG/Ty4Hb4f3L6gUglL3XhdyqbvKQau"
    "Q2xMZ/420KaoSmBjwIIZVJeA3qMkqlG9ZkL6uqucFMCUiWWCuulMoIr+TZmjefGRr/H/EdKB4LjDICkSFNkWgRbZ"
    "wFNitib1tpqtng84rvW/wcgRwfzrbnyTBWagksDxk0UH+E1HGum0DOSQ73XN3fYf966lMThbUxcZBFnOK3bDP9vb"
    "g52DLcMiFoT4kL64HnxJoj38OL5IRhfsAhcJ5DENLjTbtVLCwMxdIqazu62i++x9Qnl9cn7S752dBNtD0JK3K4g7"
    "AM2FkYkIxGWWf0xpd56q3XnGdIyv/X6Bld/PXPd90esD4qYs+jx/72vsED+WK6wrw7CnFACxp2SiyLriMEKMbaya"
    "0HFoKCSiOYGPGetYUGyIQ8rL1i6/TPL3yCBZ+zi+eeeLJzfOBMCPS0S30C1y5bhmM3PlhuTG/rBzWQ+CiFEqZAsU"
    "GrI0dhCrYWgCvCizz4QaDUFx1xuM60CsluWyI0oyXUuma6xicL9IpbQZbiLSVzaGaGZ9gGuO9og+N7C0tKXvlUg+"
    "eZc5PJSf/Jnit4ZrCIOHoIoSnUB0eHRQkGx2w8HdcPD2ss1BnAJt8QCwrsbQZD22YidaAlmxy1TMZAuwaNShe6Ng"
    "z+wB+x4Cg8yHc6gtbqFm43jFJ1Ook1eqmnNxVWPyKuYKsmolq1ayanVAAZysWv0yhhWqVmWrKdWWUGrfFBNsf7cQ"
    "2d/N4fq7L9NinP3464ltG3drSxsRaKa56lh/rpcmVFJ1qKiKqGwNDvpbEPzxWy0gp3XYzfjn79KBSwcu93npwKVh"
    "yzrw6H5amFuL6DSzcH9WpGx/ll20PxNK9oEvKoFjVKeZOL5WilSWqFR2SKQI1SXJ9T6f612CtWGDlGgnuy4fUTmk"
    "ujy7bZPq8pISrjrelJRwYylhDmxKaukDnp1SsgHVkkjSYGiuLrG9Qrp3oMP7rPoYymxSZpOHsPaPJumQ2eSRGlbI"
    "JmeIzN1paviTHb7HlCoJ4XfLC1efTAo+qiiUonPb3Wm7jRmfEanXfdxOcPQlgE3TbWS2WUvGzkApWwmK6jST/Kgp"
    "cXecB5vG3XPglPpFjaDYyOlZC6ZgRQNMunSxUWovjWk1Es26fp8ETYBKYRkoNBLGnlKk8EulcpxRNxVDdQUxohdN"
    "SyRt24DAysEzppwAdkq169pDy6bhxQm5i/H4YyzQvRglD2F+ur64pDOWI02FEImlkiG8BnCIatgzZG2RZAjKFeQZ"
    "h3UY9oDSiszz3yWOSUQog+i7LRIrylO9+nALDcDRFE0rvkfj8MKQLFJQLOzFz2RsD0fyKEhDMeHpEdD4T+CeiQhj"
    "MAf0cgMt+EFdg0Cpm/ONIpNB/ybAy2eCVcFyVdPC+YxwpxWeQAokJU8seeJDWOVHQydKnvhIDSs44m24zf3QmtXm"
    "kUdJae4d11o4zRg8ZcnNVOVGch/1kJw+PKWJJFGzkajWwihJmrNimlNy8dUvfQNZi60Cupii5OP2/D4GzpBS57aV"
    "JRO60ph7NqY8stqRR1blkdUNsJ95UU3j9O+QNrVT+EtBppNHYK4i0hQWXb53W1KRkoo8JC8pqchfxrACFbnjsywF"
    "bFfrYdWa3gKrw9JJckypmcRjPeSYi+kML0c3hirNBLJ6ZhwQAs1lWpU/M9aJqvySL8eVr8tsgEsrlNGzobnmdmFo"
    "XFWSM4d98q3OVHhAE1dt3k5JgL2eTl7aC0KZg0l1jyjPfeaun53BriB2vKNvReOPiEoz4496fnZAl0YJED3xZgJY"
    "2bvRUv6uQwQx788lApV9vcSiNtdV2esq9upenv4Djv8QCw=="
)
