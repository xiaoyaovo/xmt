from tortoise import fields

from app.models.base import BaseModel


class User(BaseModel):
    github_id = fields.CharField(max_length=64, unique=True, null=True)
    auth_provider = fields.CharField(max_length=32, default="github")
    provider_user_id = fields.CharField(max_length=128, null=True)
    username = fields.CharField(max_length=255)
    password_hash = fields.CharField(max_length=255, null=True)
    avatar_url = fields.CharField(max_length=1024, null=True)
    email = fields.CharField(max_length=320, null=True)
    last_login_at = fields.DatetimeField(null=True)

    class Meta:
        table = "users"
        unique_together = (("auth_provider", "provider_user_id"),)
