from fastapi import HTTPException, status

from app.models.tool_sync_item import ToolSyncItem
from app.models.user import User


async def list_tool_sync_items(user: User, tool_key: str) -> list[ToolSyncItem]:
    return await ToolSyncItem.filter(user=user, tool_key=tool_key).order_by("-updated_at")


async def get_tool_sync_item(user: User, tool_key: str, item_key: str) -> ToolSyncItem:
    item = await ToolSyncItem.get_or_none(user=user, tool_key=tool_key, item_key=item_key)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="同步内容不存在。")

    return item


async def upsert_tool_sync_item(
    user: User,
    tool_key: str,
    item_key: str,
    *,
    title: str | None,
    payload: dict,
) -> ToolSyncItem:
    item, _ = await ToolSyncItem.update_or_create(
        defaults={
            "title": title,
            "payload": payload,
        },
        user=user,
        tool_key=tool_key,
        item_key=item_key,
    )
    return item


async def delete_tool_sync_item(user: User, tool_key: str, item_key: str) -> None:
    item = await get_tool_sync_item(user, tool_key, item_key)
    await item.delete()
