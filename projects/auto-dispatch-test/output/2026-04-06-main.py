"""
FastAPI joke service — main entrypoint.
Upstream: projects/auto-dispatch-test/output/2026-04-06-system-architecture.md (bjorn)
"""
from fastapi import FastAPI, HTTPException

from app.jokes import get_random_joke
from app.models import Joke

app = FastAPI(title="Joke API", version="1.0.0")


@app.get("/jokes/random", response_model=Joke)
def random_joke() -> Joke:
    joke = get_random_joke()
    if joke is None:
        raise HTTPException(status_code=500, detail="No jokes available.")
    return joke


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
