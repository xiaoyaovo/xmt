from fastapi import APIRouter, Query

from app.schemas.lol import LolSearchResponse
from app.services.lol_service import PLATFORM_REGIONS, PLATFORM_ROUTES, REGIONAL_ROUTES, search_lol_profile

router = APIRouter(prefix="/lol")


@router.get("/search", response_model=LolSearchResponse, summary="Search League of Legends match history")
async def search_match_history(
    game_name: str = Query(..., min_length=1, max_length=64),
    tag_line: str = Query(..., min_length=1, max_length=16),
    platform: str = Query(default="kr", pattern=r"^[a-z0-9]{2,4}$"),
    region: str = Query(default="", pattern=r"^[a-z]*$"),
    count: int = Query(default=10, ge=1, le=20),
) -> LolSearchResponse:
    normalized_platform = platform.lower()
    normalized_region = region.lower() or PLATFORM_REGIONS.get(normalized_platform, "asia")
    if normalized_platform not in PLATFORM_ROUTES:
        normalized_platform = "kr"
    if normalized_region not in REGIONAL_ROUTES:
        normalized_region = PLATFORM_REGIONS.get(normalized_platform, "asia")

    result = await search_lol_profile(
        game_name=game_name,
        tag_line=tag_line,
        platform=normalized_platform,
        region=normalized_region,
        count=count,
    )
    return LolSearchResponse(**result)
