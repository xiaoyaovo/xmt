from tortoise import fields

from app.models.base import BaseModel


class HealthCheckRecord(BaseModel):
    name = fields.CharField(max_length=100, unique=True)

    class Meta:
        table = "health_check_records"
