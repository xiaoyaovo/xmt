from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse

from app.api.dependencies import require_current_user
from app.models.csv_file import CsvFile
from app.models.user import User
from app.schemas.csv_file import CsvFileListResponse, CsvFileResponse, CsvRowsResponse
from app.services.csv_service import (
    cleanup_expired_csv_files,
    delete_csv_file,
    get_user_csv_file,
    read_csv_rows,
    save_upload_file,
)

router = APIRouter(prefix="/csv")


def serialize_csv_file(item: CsvFile) -> CsvFileResponse:
    return CsvFileResponse(
        id=item.id,
        original_filename=item.original_filename,
        size=item.size,
        content_type=item.content_type,
        columns=item.columns or [],
        row_count=item.row_count,
        delimiter=item.delimiter,
        status=item.status,
        error_message=item.error_message,
        expires_at=item.expires_at,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.post("/files", response_model=CsvFileResponse, summary="Upload CSV file")
async def upload_csv_file(
    file: UploadFile = File(...),
    user: User = Depends(require_current_user),
) -> CsvFileResponse:
    item = await save_upload_file(user, file)
    return serialize_csv_file(item)


@router.get("/files", response_model=CsvFileListResponse, summary="List CSV history")
async def list_csv_files(user: User = Depends(require_current_user)) -> CsvFileListResponse:
    await cleanup_expired_csv_files(user)
    items = await CsvFile.filter(user=user).order_by("-created_at")
    return CsvFileListResponse(items=[serialize_csv_file(item) for item in items], total=len(items))


@router.get("/files/{file_id}", response_model=CsvFileResponse, summary="Get CSV file detail")
async def get_csv_file(file_id: int, user: User = Depends(require_current_user)) -> CsvFileResponse:
    item = await get_user_csv_file(user, file_id)
    return serialize_csv_file(item)


@router.get("/files/{file_id}/rows", response_model=CsvRowsResponse, summary="Read CSV rows")
async def get_csv_rows(
    file_id: int,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=1000),
    user: User = Depends(require_current_user),
) -> CsvRowsResponse:
    item = await get_user_csv_file(user, file_id)
    rows = read_csv_rows(item, offset, limit)
    return CsvRowsResponse(
        file=serialize_csv_file(item),
        columns=item.columns or [],
        rows=rows,
        offset=offset,
        limit=limit,
        total=item.row_count,
        has_more=offset + len(rows) < item.row_count,
    )


@router.get("/files/{file_id}/download", summary="Download original CSV file")
async def download_csv_file(file_id: int, user: User = Depends(require_current_user)) -> FileResponse:
    item = await get_user_csv_file(user, file_id)
    path = Path(item.storage_path)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CSV 原文件不存在。")

    return FileResponse(path, filename=item.original_filename, media_type=item.content_type or "text/csv")


@router.delete("/files/{file_id}", summary="Delete CSV file")
async def delete_csv_history(file_id: int, user: User = Depends(require_current_user)) -> dict[str, bool]:
    item = await get_user_csv_file(user, file_id)
    await delete_csv_file(item)
    return {"ok": True}

