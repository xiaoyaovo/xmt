from pydantic import BaseModel, Field


class LolSearchResponse(BaseModel):
    account: dict = Field(default_factory=dict)
    summoner: dict = Field(default_factory=dict)
    ranked: list[dict] = Field(default_factory=list)
    matches: list[dict] = Field(default_factory=list)
    assets: dict = Field(default_factory=dict)
    meta: dict = Field(default_factory=dict)
