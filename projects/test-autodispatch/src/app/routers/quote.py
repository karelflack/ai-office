from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.quote_service import get_daily_quote


class QuoteResponse(BaseModel):
    quote: str
    author: str
    date: str


router = APIRouter(prefix="/quote", tags=["quotes"])


@router.get("/daily", response_model=QuoteResponse)
def daily_quote() -> QuoteResponse:
    """Return the motivational quote for today (UTC date)."""
    result = get_daily_quote()
    if result is None:
        raise HTTPException(status_code=500, detail="Quote source unavailable.")
    return result
