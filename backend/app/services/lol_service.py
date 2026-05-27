from urllib.parse import quote

import httpx
from fastapi import HTTPException, status

from app.settings.config import settings

REGIONAL_ROUTES = {
    "americas": "americas",
    "asia": "asia",
    "europe": "europe",
    "sea": "sea",
}

PLATFORM_ROUTES = {
    "br1": "br1",
    "eun1": "eun1",
    "euw1": "euw1",
    "jp1": "jp1",
    "kr": "kr",
    "la1": "la1",
    "la2": "la2",
    "na1": "na1",
    "oc1": "oc1",
    "ph2": "ph2",
    "ru": "ru",
    "sg2": "sg2",
    "th2": "th2",
    "tr1": "tr1",
    "tw2": "tw2",
    "vn2": "vn2",
}

PLATFORM_REGIONS = {
    "br1": "americas",
    "la1": "americas",
    "la2": "americas",
    "na1": "americas",
    "oc1": "sea",
    "ph2": "sea",
    "sg2": "sea",
    "th2": "sea",
    "tw2": "sea",
    "vn2": "sea",
    "eun1": "europe",
    "euw1": "europe",
    "ru": "europe",
    "tr1": "europe",
    "jp1": "asia",
    "kr": "asia",
}

QUEUE_LABELS = {
    400: "匹配模式",
    420: "单双排位",
    430: "普通匹配",
    440: "灵活排位",
    450: "极地大乱斗",
    700: "冠军杯赛",
    1700: "斗魂竞技场",
}

RANKED_QUEUE_LABELS = {
    "RANKED_SOLO_5x5": "单双排位",
    "RANKED_FLEX_SR": "灵活排位",
}


def normalize_route(value: str, allowed: dict[str, str], fallback: str) -> str:
    key = (value or fallback).strip().lower()
    return allowed.get(key, fallback)


def normalize_count(value: int) -> int:
    return max(1, min(value, 20))


def riot_headers() -> dict[str, str]:
    return {"X-Riot-Token": settings.riot_api_key}


def riot_error_message(status_code: int) -> str:
    if status_code == status.HTTP_404_NOT_FOUND:
        return "没有找到这个 Riot ID。"
    if status_code == status.HTTP_403_FORBIDDEN:
        return "Riot API Key 无效或已过期。"
    if status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        return "Riot API 请求过于频繁，请稍后再试。"
    return "Riot API 暂时不可用。"


def build_riot_url(route: str, path: str) -> str:
    return f"https://{route}.api.riotgames.com{path}"


async def get_json(client: httpx.AsyncClient, route: str, path: str) -> dict | list:
    response = await client.get(build_riot_url(route, path), headers=riot_headers())
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=riot_error_message(response.status_code))
    return response.json()


async def get_optional_json(
    client: httpx.AsyncClient,
    route: str,
    path: str,
    fallback,
    *,
    required_statuses: set[int] | None = None,
):
    try:
        return await get_json(client, route, path)
    except HTTPException as exc:
        if required_statuses and exc.status_code in required_statuses:
            raise
        return fallback


async def get_data_dragon_json(client: httpx.AsyncClient, version: str, file_name: str) -> dict:
    response = await client.get(f"https://ddragon.leagueoflegends.com/cdn/{version}/data/zh_CN/{file_name}")
    if response.status_code >= 400:
        return {}
    return response.json()


async def get_data_dragon_version(client: httpx.AsyncClient) -> str:
    response = await client.get("https://ddragon.leagueoflegends.com/api/versions.json")
    if response.status_code >= 400:
        return "latest"
    versions = response.json()
    return versions[0] if versions else "latest"


def champion_asset(champions_by_key: dict[str, dict], champion_id: int) -> dict:
    champion = champions_by_key.get(str(champion_id), {})
    image = champion.get("image", {})
    full = image.get("full", "")
    return {
        "id": champion.get("id", str(champion_id)),
        "name": champion.get("name") or champion.get("id") or str(champion_id),
        "image": full,
    }


def spell_asset(spells_by_key: dict[str, dict], spell_id: int) -> dict:
    spell = spells_by_key.get(str(spell_id), {})
    image = spell.get("image", {})
    return {
        "id": spell.get("id", str(spell_id)),
        "name": spell.get("name") or spell.get("id") or str(spell_id),
        "image": image.get("full", ""),
    }


def item_asset(items: dict[str, dict], item_id: int) -> dict | None:
    if not item_id:
        return None
    item = items.get(str(item_id), {})
    return {
        "id": item_id,
        "name": item.get("name", str(item_id)),
        "image": f"{item_id}.png",
    }


def summarize_ranked(entries: list[dict]) -> list[dict]:
    summaries = []
    for entry in entries:
        wins = int(entry.get("wins") or 0)
        losses = int(entry.get("losses") or 0)
        total = wins + losses
        summaries.append(
            {
                "queue_type": entry.get("queueType", ""),
                "queue_label": RANKED_QUEUE_LABELS.get(entry.get("queueType", ""), entry.get("queueType", "")),
                "tier": entry.get("tier", "UNRANKED"),
                "rank": entry.get("rank", ""),
                "league_points": entry.get("leaguePoints", 0),
                "wins": wins,
                "losses": losses,
                "win_rate": round((wins / total) * 100) if total else 0,
            }
        )
    return summaries


def summarize_match(match: dict, puuid: str, assets: dict, data_dragon_version: str) -> dict | None:
    info = match.get("info") or {}
    metadata = match.get("metadata") or {}
    participants = info.get("participants") or []
    participant = next((item for item in participants if item.get("puuid") == puuid), None)
    if not participant:
        return None

    champion = champion_asset(assets["champions_by_key"], participant.get("championId", 0))
    spells = [
        spell_asset(assets["spells_by_key"], participant.get("summoner1Id", 0)),
        spell_asset(assets["spells_by_key"], participant.get("summoner2Id", 0)),
    ]
    items = [
        item_asset(assets["items"], participant.get(f"item{index}", 0))
        for index in range(7)
    ]

    kills = int(participant.get("kills") or 0)
    deaths = int(participant.get("deaths") or 0)
    assists = int(participant.get("assists") or 0)
    duration_seconds = int(info.get("gameDuration") or 0)
    total_cs = int(participant.get("totalMinionsKilled") or 0) + int(participant.get("neutralMinionsKilled") or 0)

    return {
        "match_id": metadata.get("matchId", ""),
        "queue_id": info.get("queueId", 0),
        "queue_label": QUEUE_LABELS.get(info.get("queueId", 0), f"队列 {info.get('queueId', 0)}"),
        "game_creation": info.get("gameCreation", 0),
        "game_duration": duration_seconds,
        "game_mode": info.get("gameMode", ""),
        "win": bool(participant.get("win")),
        "champion": champion,
        "champion_icon_url": (
            f"https://ddragon.leagueoflegends.com/cdn/{data_dragon_version}/img/champion/{champion['image']}"
            if champion.get("image")
            else ""
        ),
        "summoner_spells": spells,
        "items": [item for item in items if item],
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "kda": round((kills + assists) / max(1, deaths), 2),
        "cs": total_cs,
        "cs_per_minute": round(total_cs / max(1, duration_seconds / 60), 1),
        "gold_earned": participant.get("goldEarned", 0),
        "damage_to_champions": participant.get("totalDamageDealtToChampions", 0),
        "vision_score": participant.get("visionScore", 0),
    }


async def search_lol_profile(
    *,
    game_name: str,
    tag_line: str,
    platform: str = "kr",
    region: str = "",
    count: int = 10,
) -> dict:
    if not settings.riot_api_key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Riot API Key 未配置。")

    normalized_platform = normalize_route(platform, PLATFORM_ROUTES, "kr")
    normalized_region = normalize_route(region, REGIONAL_ROUTES, PLATFORM_REGIONS.get(normalized_platform, "asia"))
    normalized_count = normalize_count(count)

    encoded_game_name = quote(game_name.strip(), safe="")
    encoded_tag_line = quote(tag_line.strip(), safe="")

    timeout = httpx.Timeout(settings.riot_request_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            account = await get_json(
                client,
                normalized_region,
                f"/riot/account/v1/accounts/by-riot-id/{encoded_game_name}/{encoded_tag_line}",
            )
            puuid = account.get("puuid")
            if not puuid:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="没有找到这个 Riot ID。")

            summoner = await get_optional_json(
                client,
                normalized_platform,
                f"/lol/summoner/v4/summoners/by-puuid/{quote(puuid, safe='')}",
                {},
                required_statuses={status.HTTP_403_FORBIDDEN},
            )
            ranked = await get_optional_json(
                client,
                normalized_platform,
                f"/lol/league/v4/entries/by-summoner/{quote(summoner.get('id', ''), safe='')}",
                [],
                required_statuses={status.HTTP_403_FORBIDDEN},
            ) if summoner.get("id") else []
            match_ids = await get_optional_json(
                client,
                normalized_region,
                f"/lol/match/v5/matches/by-puuid/{quote(puuid, safe='')}/ids?start=0&count={normalized_count}",
                [],
                required_statuses={status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND},
            )

            version = await get_data_dragon_version(client)
            champion_json = await get_data_dragon_json(client, version, "champion.json")
            spell_json = await get_data_dragon_json(client, version, "summoner.json")
            item_json = await get_data_dragon_json(client, version, "item.json")

            assets = {
                "champions_by_key": {
                    value.get("key"): value
                    for value in (champion_json.get("data") or {}).values()
                    if value.get("key")
                },
                "spells_by_key": {
                    value.get("key"): value
                    for value in (spell_json.get("data") or {}).values()
                    if value.get("key")
                },
                "items": item_json.get("data") or {},
            }

            matches = []
            for match_id in match_ids:
                match = await get_optional_json(
                    client,
                    normalized_region,
                    f"/lol/match/v5/matches/{quote(match_id, safe='')}",
                    {},
                )
                summary = summarize_match(match, puuid, assets, version)
                if summary:
                    matches.append(summary)

            return {
                "account": {
                    "puuid": puuid,
                    "game_name": account.get("gameName", game_name),
                    "tag_line": account.get("tagLine", tag_line),
                },
                "summoner": {
                    "id": summoner.get("id", ""),
                    "account_id": summoner.get("accountId", ""),
                    "profile_icon_id": summoner.get("profileIconId", 0),
                    "summoner_level": summoner.get("summonerLevel", 0),
                    "profile_icon_url": (
                        f"https://ddragon.leagueoflegends.com/cdn/{version}/img/profileicon/"
                        f"{summoner.get('profileIconId', 0)}.png"
                    ),
                },
                "ranked": summarize_ranked(ranked),
                "matches": matches,
                "assets": {
                    "data_dragon_version": version,
                    "champion_base_url": f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion",
                    "spell_base_url": f"https://ddragon.leagueoflegends.com/cdn/{version}/img/spell",
                    "item_base_url": f"https://ddragon.leagueoflegends.com/cdn/{version}/img/item",
                },
                "meta": {
                    "platform": normalized_platform,
                    "region": normalized_region,
                    "count": normalized_count,
                },
            }
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="连接 Riot API 失败，请稍后重试。",
            ) from exc
