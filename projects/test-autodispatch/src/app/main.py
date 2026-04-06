from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import quote
from app.services.quote_service import load_quotes


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_quotes()
    yield


app = FastAPI(
    title="Daily Motivational Quote API",
    description="Returns one motivational quote per calendar day.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(quote.router)


@app.get("/health", tags=["ops"])
def health() -> dict:
    return {"status": "ok"}
