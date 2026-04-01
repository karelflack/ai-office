import os
from fastapi import APIRouter, FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import crud, schemas
from .auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_current_user,
    get_optional_user,
)
from . import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener", version="2.0.0")

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# ---------------------------------------------------------------------------
# Auth router  (/auth/register, /auth/login, /auth/refresh, /auth/me)
# ---------------------------------------------------------------------------

auth_router = APIRouter(prefix="/auth", tags=["auth"])


def _issue_tokens(email: str) -> schemas.Token:
    """Create a matched access+refresh token pair for the given email."""
    return schemas.Token(
        access_token=create_access_token({"sub": email}),
        refresh_token=create_refresh_token({"sub": email}),
    )


@auth_router.post("/register", response_model=schemas.Token, status_code=201)
def auth_register(body: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, body.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    hashed = hash_password(body.password)
    user = crud.create_user(db, email=body.email, hashed_password=hashed)
    return _issue_tokens(user.email)


@auth_router.post("/login", response_model=schemas.Token)
def auth_login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _issue_tokens(user.email)


@auth_router.post("/refresh", response_model=schemas.Token)
def auth_refresh(body: schemas.RefreshRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new access+refresh token pair."""
    email = decode_refresh_token(body.refresh_token)
    user = crud.get_user_by_email(db, email)
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return _issue_tokens(user.email)


@auth_router.get("/me", response_model=schemas.UserResponse)
def auth_me(current_user: models.User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return current_user


app.include_router(auth_router)


# ---------------------------------------------------------------------------
# Legacy flat auth endpoints (kept for backward compatibility)
# ---------------------------------------------------------------------------

@app.post("/register", response_model=schemas.Token, status_code=201)
def register(body: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, body.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    hashed = hash_password(body.password)
    user = crud.create_user(db, email=body.email, hashed_password=hashed)
    return _issue_tokens(user.email)


@app.post("/login", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm provides `username` and `password` fields
    user = crud.get_user_by_email(db, form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _issue_tokens(user.email)


# ---------------------------------------------------------------------------
# Link endpoints
# ---------------------------------------------------------------------------

@app.post("/shorten", response_model=schemas.ShortenResponse, status_code=201)
def shorten_url(
    body: schemas.ShortenRequest,
    db: Session = Depends(get_db),
    current_user: models.User | None = Depends(get_optional_user),
):
    original_url = str(body.url)

    if body.custom_code:
        existing = crud.get_link_by_code(db, body.custom_code)
        if existing:
            raise HTTPException(status_code=409, detail="Custom code already in use")

    owner_id = current_user.id if current_user else None
    link = crud.create_link(db, original_url=original_url, custom_code=body.custom_code, owner_id=owner_id)
    return schemas.ShortenResponse(
        code=link.code,
        original_url=link.original_url,
        short_url=f"{BASE_URL}/{link.code}",
        created_at=link.created_at,
        owner_id=link.owner_id,
    )


@app.get("/me/links", response_model=list[schemas.LinkResponse])
def my_links(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    links = crud.get_links_by_owner(db, current_user.id)
    return [
        schemas.LinkResponse(
            code=link.code,
            original_url=link.original_url,
            short_url=f"{BASE_URL}/{link.code}",
            created_at=link.created_at,
            owner_id=link.owner_id,
        )
        for link in links
    ]


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
def delete_url(
    code: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    link = crud.get_link_by_code(db, code)
    if not link:
        raise HTTPException(status_code=404, detail="Short code not found")

    # Owners can always delete their own links.
    # Any authenticated user can delete anonymous links (no owner).
    # Authenticated users cannot delete links owned by someone else.
    if link.owner_id is not None and link.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorised to delete this link")

    crud.delete_link(db, link)
