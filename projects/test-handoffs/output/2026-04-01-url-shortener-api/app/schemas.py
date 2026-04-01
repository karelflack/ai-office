from datetime import datetime
from pydantic import BaseModel, HttpUrl, EmailStr


class ShortenRequest(BaseModel):
    url: HttpUrl
    custom_code: str | None = None


class ShortenResponse(BaseModel):
    code: str
    original_url: str
    short_url: str
    created_at: datetime
    owner_id: int | None = None


class StatsResponse(BaseModel):
    code: str
    original_url: str
    created_at: datetime
    total_clicks: int
    recent_clicks: list[datetime]


# --- Auth schemas ---

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    # Subject field holds the user's email
    sub: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LinkResponse(BaseModel):
    code: str
    original_url: str
    short_url: str
    created_at: datetime
    owner_id: int | None = None
