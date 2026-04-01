# URL Shortener API

A Python REST API built with FastAPI and SQLite.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API is available at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/shorten` | Create a short URL |
| `GET` | `/{code}` | Redirect to original URL |
| `DELETE` | `/{code}` | Delete a short URL |
| `GET` | `/{code}/stats` | Click statistics |

### POST /shorten

```json
{ "url": "https://example.com/some/long/path", "custom_code": "optional" }
```

Returns `201` with `{ code, original_url, short_url, created_at }`.

Returns `409` if `custom_code` is already taken.

### GET /{code}

Redirects `302` to the original URL and records the click.

### GET /{code}/stats

Returns click count and timestamps of the 10 most recent clicks.

### DELETE /{code}

Returns `204` on success.

## Configuration

| Env Var | Default | Description |
|---------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./shortener.db` | SQLAlchemy connection string |
| `BASE_URL` | `http://localhost:8000` | Used in `short_url` response field |

## Running Tests

```bash
pytest tests/ -v
```
