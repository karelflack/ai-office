from pydantic import BaseModel


class Joke(BaseModel):
    id: int
    setup: str
    punchline: str
    category: str
