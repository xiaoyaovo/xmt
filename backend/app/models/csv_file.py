from tortoise import fields

from app.models.base import BaseModel


class CsvFile(BaseModel):
    user = fields.ForeignKeyField("models.User", related_name="csv_files", on_delete=fields.CASCADE)
    original_filename = fields.CharField(max_length=255)
    stored_filename = fields.CharField(max_length=255)
    storage_path = fields.CharField(max_length=1024)
    size = fields.BigIntField()
    content_type = fields.CharField(max_length=255, null=True)
    columns = fields.JSONField(default=list)
    row_count = fields.IntField(default=0)
    delimiter = fields.CharField(max_length=8, default=",")
    status = fields.CharField(max_length=32, default="ready")
    error_message = fields.TextField(null=True)
    expires_at = fields.DatetimeField()
    title = fields.CharField(max_length=255, null=True)
    remark = fields.TextField(null=True)

    class Meta:
        table = "csv_files"

