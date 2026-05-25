from tortoise import fields

from app.models.base import BaseModel


class User(BaseModel):
    github_id = fields.CharField(max_length=64, unique=True)
    username = fields.CharField(max_length=255)
    avatar_url = fields.CharField(max_length=1024, null=True)
    email = fields.CharField(max_length=320, null=True)
    last_login_at = fields.DatetimeField(null=True)

    class Meta:
        table = "users"

