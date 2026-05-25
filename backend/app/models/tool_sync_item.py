from tortoise import fields

from app.models.base import BaseModel


class ToolSyncItem(BaseModel):
    user = fields.ForeignKeyField("models.User", related_name="tool_sync_items", on_delete=fields.CASCADE)
    tool_key = fields.CharField(max_length=64)
    item_key = fields.CharField(max_length=128)
    title = fields.CharField(max_length=255, null=True)
    payload = fields.JSONField(default=dict)

    class Meta:
        table = "tool_sync_items"
        unique_together = (("user", "tool_key", "item_key"),)
