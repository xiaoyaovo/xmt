import csv
import os
import shutil
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from tortoise.expressions import Q

from app.models.csv_file import CsvFile
from app.models.user import User
from app.settings.config import settings


def storage_root() -> Path:
    root = Path(settings.csv_storage_dir)
    if not root.is_absolute():
        root = Path(settings.csv_storage_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


async def cleanup_expired_csv_files(user: User | None = None) -> None:
    query = CsvFile.filter(expires_at__lt=datetime.now())
    if user:
        query = query.filter(user=user)

    expired_files = await query
    for item in expired_files:
        delete_storage_file(item)
        await item.delete()


def delete_storage_file(item: CsvFile) -> None:
    path = Path(item.storage_path)
    try:
        if path.is_file():
            path.unlink()
    except OSError:
        pass


async def ensure_user_quota(user: User, incoming_size: int) -> None:
    await cleanup_expired_csv_files(user)
    current_files = await CsvFile.filter(user=user).count()
    if current_files >= settings.csv_user_max_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"最多保留 {settings.csv_user_max_files} 个 CSV 文件，请先删除历史记录。",
        )

    existing_items = await CsvFile.filter(user=user)
    current_size = sum(item.size for item in existing_items)
    if current_size + incoming_size > settings.csv_user_max_storage_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV 历史总容量不能超过 {settings.csv_user_max_storage_mb} MB。",
        )


def sniff_dialect(path: Path) -> csv.Dialect:
    with path.open("r", newline="", encoding="utf-8-sig", errors="replace") as file:
        sample = file.read(8192)

    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        return csv.excel


def inspect_csv_file(path: Path) -> tuple[list[str], int, str]:
    dialect = sniff_dialect(path)
    row_count = 0
    columns: list[str] = []

    with path.open("r", newline="", encoding="utf-8-sig", errors="replace") as file:
        reader = csv.reader(file, dialect)
        for index, row in enumerate(reader):
            if index == 0:
                columns = [value.strip() or f"Column {column_index + 1}" for column_index, value in enumerate(row)]
                continue
            row_count += 1

    if not columns:
        columns = []

    return columns, row_count, getattr(dialect, "delimiter", ",")


async def save_upload_file(
    user: User,
    upload: UploadFile,
    title: str | None = None,
    remark: str | None = None,
) -> CsvFile:
    filename = upload.filename or "data.csv"
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只支持上传 .csv 文件。")

    stored_filename = f"{uuid.uuid4().hex}.csv"
    user_dir = storage_root() / str(user.id)
    user_dir.mkdir(parents=True, exist_ok=True)
    target_path = user_dir / stored_filename

    size = 0
    try:
        with target_path.open("wb") as output:
            while chunk := await upload.read(1024 * 1024):
                size += len(chunk)
                if size > settings.csv_max_upload_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"CSV 文件不能超过 {settings.csv_max_upload_mb} MB。",
                    )
                output.write(chunk)

        await ensure_user_quota(user, size)
        columns, row_count, delimiter = inspect_csv_file(target_path)

        cleaned_title = (title or "").strip() or None
        cleaned_remark = (remark or "").strip() or None

        return await CsvFile.create(
            user=user,
            original_filename=os.path.basename(filename),
            stored_filename=stored_filename,
            storage_path=str(target_path),
            size=size,
            content_type=upload.content_type,
            columns=columns,
            row_count=row_count,
            delimiter=delimiter,
            status="ready",
            expires_at=datetime.now() + timedelta(days=settings.csv_retention_days),
            title=cleaned_title,
            remark=cleaned_remark,
        )
    except Exception:
        if target_path.exists():
            target_path.unlink()
        raise
    finally:
        await upload.close()


async def get_user_csv_file(user: User, file_id: int) -> CsvFile:
    await cleanup_expired_csv_files(user)
    item = await CsvFile.get_or_none(id=file_id, user=user)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CSV 文件不存在或已过期。")
    return item


def read_csv_rows(item: CsvFile, offset: int, limit: int) -> list[list[str]]:
    path = Path(item.storage_path)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CSV 原文件不存在。")

    dialect = sniff_dialect(path)
    rows: list[list[str]] = []
    start_index = offset + 1
    end_index = start_index + limit

    with path.open("r", newline="", encoding="utf-8-sig", errors="replace") as file:
        reader = csv.reader(file, dialect)
        for index, row in enumerate(reader):
            if index == 0:
                continue
            if index < start_index:
                continue
            if index >= end_index:
                break
            rows.append(row)

    return rows


async def delete_csv_file(item: CsvFile) -> None:
    delete_storage_file(item)
    await item.delete()


def purge_user_storage_dir(user: User) -> None:
    user_dir = storage_root() / str(user.id)
    if user_dir.is_dir():
        shutil.rmtree(user_dir, ignore_errors=True)
