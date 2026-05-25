from datetime import datetime

from pydantic import BaseModel


class CsvFileResponse(BaseModel):
    id: int
    original_filename: str
    size: int
    content_type: str | None = None
    columns: list[str]
    row_count: int
    delimiter: str
    status: str
    error_message: str | None = None
    expires_at: datetime
    created_at: datetime
    updated_at: datetime
    title: str | None = None
    remark: str | None = None


class CsvFileListResponse(BaseModel):
    items: list[CsvFileResponse]
    total: int


class CsvRowsResponse(BaseModel):
    file: CsvFileResponse
    columns: list[str]
    rows: list[list[str]]
    offset: int
    limit: int
    total: int
    has_more: bool

