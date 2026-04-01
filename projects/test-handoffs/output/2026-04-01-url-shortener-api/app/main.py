import os
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import crud, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener", version="1.0.0")

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


@app.post("/shorten", response_model=schemas.ShortenResponse, status_code=201)
def shorten_url(body: schemas.ShortenRequest, db: Session = Depends(get_db)):
    original_url = str(body.url)

    if body.custom_code:
        existing = crud.get_link_by_code(db, body.custom_code)
        if existing:
            raise HTTPException(status_code=409, detail="Custom code already in use")

    link = crud.create_link(db, original_url=original_url, custom_code=body.custom_code)
    return schemas.ShortenResponse(
        code=link.code,
        original_url=link.original_url,
        short_url=f"{BASE_URL}/{link.code}",
        created_at=link.created_at,
    )


@app.get("/{code}/stats", response_model=schemas.StatsResponse)
def get_stats(code: str, db: Session = Depends(get_db)):
    link = crud.get_link_by_code(db, code)
    if not link:
        raise HTTPException(status_code=404, detail="Short code not found")

    return schemas.StatsResponse(
        code=link.code,
        original_url=link.original_url,
        created_at=link.created_at,
        total_clicks=len(link.clicks),
        recent_clicks=[c.clicked_at for c in sorted(link.clicks, key=lambda c: c.clicked_at, reverse=True)[:10]],
    )


@app.get("/{code}")
def redirect(code: str, request: Request, db: Session = Depends(get_db)):
    link = crud.get_link_by_code(db, code)
    if not link:
        raise HTTPException(status_code=404, detail="Short code not found")

    referrer = request.headers.get("referer")
    user_agent = request.headers.get("user-agent")
    crud.record_click(db, link, referrer=referrer, user_agent=user_agent)

    return RedirectResponse(url=link.original_url, status_code=302)


@app.delete("/{code}", status_code=204)
def delete_url(code: str, db: Session = Depends(get_db)):
    link = crud.get_link_by_code(db, code)
    if not link:
        raise HTTPException(status_code=404, detail="Short code not found")

    crud.delete_link(db, link)
