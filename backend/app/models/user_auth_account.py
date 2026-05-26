from tortoise import fields

from app.models.base import BaseModel


class UserAuthAccount(BaseModel):
    user = fields.ForeignKeyField("models.User", related_name="auth_accounts", on_delete=fields.CASCADE)
    provider = fields.CharField(max_length=32)
    provider_user_id = fields.CharField(max_length=128)
    provider_username = fields.CharField(max_length=255, null=True)
    provider_email = fields.CharField(max_length=320, null=True)
    avatar_url = fields.CharField(max_length=1024, null=True)
    password_hash = fields.CharField(max_length=255, null=True)
    linked_at = fields.DatetimeField(null=True)
    last_used_at = fields.DatetimeField(null=True)

    class Meta:
        table = "user_auth_accounts"
        unique_together = (
            ("provider", "provider_user_id"),
            ("user", "provider"),
        )
