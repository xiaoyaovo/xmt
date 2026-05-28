from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class WeddingRsvpCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    attendance: Literal["yes", "no"] = "yes"
    guests: int = Field(default=1, ge=1, le=20)
    message: str | None = Field(default=None, max_length=2000)


class WeddingRsvpResponse(BaseModel):
    id: int
    name: str
    attendance: str
    guests: int
    message: str | None = None
    created_at: datetime
