from tortoise import fields

from app.models.base import BaseModel


class Comment(BaseModel):
    """通用评论 — 通过 (target_type, target_id) 关联到任意业务对象。"""

    target_type = fields.CharField(max_length=32, index=True)
    target_id = fields.CharField(max_length=128, index=True)
    parent = fields.ForeignKeyField(
        "models.Comment",
        related_name="children",
        null=True,
        on_delete=fields.CASCADE,
    )
    reply_to = fields.ForeignKeyField(
        "models.Comment",
        related_name="incoming_replies",
        null=True,
        on_delete=fields.SET_NULL,
    )
    author_name = fields.CharField(max_length=64)
    author_relation = fields.CharField(max_length=64, null=True)
    author_avatar = fields.CharField(max_length=512, null=True)
    author_anon_id = fields.CharField(max_length=64, index=True)
    content = fields.TextField()
    like_count = fields.IntField(default=0)
    reply_count = fields.IntField(default=0)

    class Meta:
        table = "comments"


class CommentLike(BaseModel):
    """一个 anon_id 对一个 comment 只能点赞一次。"""

    comment = fields.ForeignKeyField(
        "models.Comment",
        related_name="likes",
        on_delete=fields.CASCADE,
    )
    anon_id = fields.CharField(max_length=64)

    class Meta:
        table = "comment_likes"
        unique_together = (("comment", "anon_id"),)
