from contextlib import asynccontextmanager

from fastapi import FastAPI

from routers import joke
from services.joke_service import load_jokes


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_jokes()
    yield


app = FastAPI(
    title="Random Joke API",
    description="Returns jokes on demand. Three endpoints: random joke, joke by ID, full list.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(joke.router)


@app.get("/health", tags=["ops"])
def health() -> dict:
    return {"status": "ok"}
