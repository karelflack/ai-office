from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.joke_service import get_random_joke, get_joke_by_id, get_all_jokes


class JokeResponse(BaseModel):
    id: int
    setup: str
    punchline: str
    category: str


router = APIRouter(tags=["jokes"])


@router.get("/joke", response_model=JokeResponse)
def random_joke() -> JokeResponse:
    """Return a random joke from the dataset."""
    joke = get_random_joke()
    if joke is None:
        raise HTTPException(status_code=500, detail="Joke source unavailable.")
    return joke


@router.get("/joke/{id}", response_model=JokeResponse)
def joke_by_id(id: int) -> JokeResponse:
    """Return the joke with the given ID."""
    joke = get_joke_by_id(id)
    if joke is None:
        raise HTTPException(status_code=404, detail="Joke not found.")
    return joke


@router.get("/jokes", response_model=list[JokeResponse])
def jokes_list(category: str = Query(default=None)) -> list[JokeResponse]:
    """Return all jokes. Optional ?category= filter."""
    return get_all_jokes(category=category)
