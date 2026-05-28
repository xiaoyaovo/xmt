from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    target_type: str = Field(min_length=1, max_length=32, pattern=r"^[a-z0-9][a-z0-9_:.-]*$")
    target_id: str = Field(min_length=1, max_length=128, pattern=r"^[a-z0-9][a-z0-9_:.-]*$")
    parent_id: int | None = None
    reply_to_id: int | None = None
    author_name: str = Field(min_length=1, max_length=64)
    author_relation: str | None = Field(default=None, max_length=64)
    author_avatar: str | None = Field(default=None, max_length=512)
    content: str = Field(min_length=1, max_length=2000)


class CommentAuthor(BaseModel):
    name: str
    relation: str | None = None
    avatar: str | None = None


class CommentResponse(BaseModel):
    id: int
    parent_id: int | None = None
    reply_to_id: int | None = None
    reply_to_name: str | None = None
    author: CommentAuthor
    content: str
    like_count: int
    reply_count: int
    liked: bool = False
    created_at: datetime


class CommentListItem(CommentResponse):
    recent_replies: list[CommentResponse] = Field(default_factory=list)


class CommentListResponse(BaseModel):
    items: list[CommentListItem]
    total: int
    page: int
    page_size: int


class CommentLikeResponse(BaseModel):
    id: int
    like_count: int
    liked: bool


CommentSort = Literal["new", "hot"]
