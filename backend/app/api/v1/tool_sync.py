from fastapi import APIRouter, Depends, Path

from app.api.dependencies import require_current_user
from app.models.tool_sync_item import ToolSyncItem
from app.models.user import User
from app.schemas.tool_sync import ToolSyncItemListResponse, ToolSyncItemResponse, ToolSyncItemUpsertRequest
from app.services.tool_sync_service import (
    delete_tool_sync_item,
    get_tool_sync_item,
    list_tool_sync_items,
    upsert_tool_sync_item,
)

router = APIRouter(prefix="/sync/items")

TOOL_KEY_PATTERN = r"^[a-z0-9][a-z0-9_-]{0,63}$"
ITEM_KEY_PATTERN = r"^[a-z0-9][a-z0-9_.:-]{0,127}$"


def serialize_tool_sync_item(item: ToolSyncItem) -> ToolSyncItemResponse:
    return ToolSyncItemResponse(
        id=item.id,
        tool_key=item.tool_key,
        item_key=item.item_key,
        title=item.title,
        payload=item.payload or {},
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("/{tool_key}", response_model=ToolSyncItemListResponse, summary="List synced tool items")
async def list_items(
    tool_key: str = Path(..., pattern=TOOL_KEY_PATTERN),
    user: User = Depends(require_current_user),
) -> ToolSyncItemListResponse:
    items = await list_tool_sync_items(user, tool_key)
    return ToolSyncItemListResponse(items=[serialize_tool_sync_item(item) for item in items], total=len(items))


@router.get("/{tool_key}/{item_key}", response_model=ToolSyncItemResponse, summary="Get synced tool item")
async def get_item(
    tool_key: str = Path(..., pattern=TOOL_KEY_PATTERN),
    item_key: str = Path(..., pattern=ITEM_KEY_PATTERN),
    user: User = Depends(require_current_user),
) -> ToolSyncItemResponse:
    item = await get_tool_sync_item(user, tool_key, item_key)
    return serialize_tool_sync_item(item)


@router.put("/{tool_key}/{item_key}", response_model=ToolSyncItemResponse, summary="Create or update synced tool item")
async def upsert_item(
    body: ToolSyncItemUpsertRequest,
    tool_key: str = Path(..., pattern=TOOL_KEY_PATTERN),
    item_key: str = Path(..., pattern=ITEM_KEY_PATTERN),
    user: User = Depends(require_current_user),
) -> ToolSyncItemResponse:
    item = await upsert_tool_sync_item(user, tool_key, item_key, title=body.title, payload=body.payload)
    return serialize_tool_sync_item(item)


@router.delete("/{tool_key}/{item_key}", summary="Delete synced tool item")
async def delete_item(
    tool_key: str = Path(..., pattern=TOOL_KEY_PATTERN),
    item_key: str = Path(..., pattern=ITEM_KEY_PATTERN),
    user: User = Depends(require_current_user),
) -> dict[str, bool]:
    await delete_tool_sync_item(user, tool_key, item_key)
    return {"ok": True}
