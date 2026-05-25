from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ToolSyncItemUpsertRequest(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    payload: dict[str, Any] = Field(default_factory=dict)


class ToolSyncItemResponse(BaseModel):
    id: int
    tool_key: str
    item_key: str
    title: str | None = None
    payload: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ToolSyncItemListResponse(BaseModel):
    items: list[ToolSyncItemResponse]
    total: int
