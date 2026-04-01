from datetime import datetime
from pydantic import BaseModel, HttpUrl, field_serializer


class ShortenRequest(BaseModel):
    url: HttpUrl
    custom_code: str | None = None


class ShortenResponse(BaseModel):
    code: str
    original_url: str
    short_url: str
    created_at: datetime


class StatsResponse(BaseModel):
    code: str
    original_url: str
    created_at: datetime
    total_clicks: int
    recent_clicks: list[datetime]
