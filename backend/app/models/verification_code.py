from tortoise import fields

from app.models.base import BaseModel


class VerificationCode(BaseModel):
    email = fields.CharField(max_length=255, index=True)
    code_hash = fields.CharField(max_length=255)
    purpose = fields.CharField(max_length=32)
    attempts = fields.IntField(default=0)
    expires_at = fields.DatetimeField()
    consumed_at = fields.DatetimeField(null=True)

    class Meta:
        table = "verification_codes"
