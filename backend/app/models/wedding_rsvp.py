from tortoise import fields

from app.models.base import BaseModel


class WeddingRsvp(BaseModel):
    name = fields.CharField(max_length=64)
    attendance = fields.CharField(max_length=8)
    guests = fields.IntField(default=1)
    message = fields.TextField(null=True)

    class Meta:
        table = "wedding_rsvps"
