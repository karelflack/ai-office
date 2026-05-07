# API design (REST)

**What this does:** A checklist for designing HTTP APIs that other developers will actually want to use. Covers naming, idempotency, error shapes, versioning, and authentication boundaries.

**Why it matters:** Bad APIs are nearly impossible to fix once clients depend on them. A design pass that takes an hour saves a year of breaking-change negotiations later.

---

## Resource & URL design

- **Nouns, not verbs.** `/users/123/orders`, not `/getUserOrders`.
- **Plural collections.** `/users`, not `/user`.
- **Hierarchy reflects ownership.** `/users/123/orders/456` — the order belongs to that user.
- **Lowercase, hyphenated.** `/order-items`, not `/orderItems` or `/order_items`.
- **Don't put filtering or sorting in the path.** `/users?role=admin&sort=-created_at`, not `/users/admins/recent`.

## Methods (do the obvious thing)

| Method | Semantics | Idempotent? |
|--------|-----------|-------------|
| GET | Read; never modify | Yes |
| POST | Create (server assigns ID) or RPC | No |
| PUT | Replace entire resource | Yes |
| PATCH | Partial update | Sometimes |
| DELETE | Remove | Yes |

Never use GET for anything that has side effects. Crawlers, prefetchers, and caches assume GET is safe.

## Idempotency

- **GET, PUT, DELETE must be idempotent.** Running the same request twice should leave the system in the same state as running it once.
- **POST should support an idempotency key** for any operation with consequences (payments, sends, creates with side effects). Header: `Idempotency-Key: <uuid>`.

## Status codes — pick the right one

- **200 OK** — success with body
- **201 Created** — resource created; include `Location:` header
- **204 No Content** — success, no body (e.g., DELETE)
- **400 Bad Request** — malformed request, validation failure
- **401 Unauthorized** — no/invalid credentials
- **403 Forbidden** — authenticated but not allowed
- **404 Not Found** — resource doesn't exist (or auth says you can't see it)
- **409 Conflict** — state conflict (duplicate, optimistic-concurrency miss)
- **422 Unprocessable Entity** — well-formed but semantically invalid
- **429 Too Many Requests** — rate limited; include `Retry-After`
- **500 Internal Server Error** — your bug
- **503 Service Unavailable** — temporary; include `Retry-After`

Don't return 200 with `{"error": "..."}` in the body — clients can't tell success from failure.

## Error shape (standardise)

Use one error shape across the whole API:

```json
{
  "error": {
    "code": "validation_failed",
    "message": "Email is required.",
    "field": "email",
    "request_id": "req_abc123"
  }
}
```

Include a stable `code` (machine-readable) AND a `message` (human-readable). Always include a `request_id` for support correlation.

## Versioning

Version from day one. Pick one strategy and stick with it:

- **URL prefix:** `/v1/users` — most explicit, easiest to route
- **Header:** `Accept: application/vnd.acme.v1+json` — cleaner URLs but harder to test

Never break v1. When the contract changes, ship v2 and run both for a deprecation window (≥ 90 days).

## Authentication boundary

- One auth method per surface — don't mix Bearer tokens and cookies in the same API.
- Token in `Authorization: Bearer <token>` header, not query string.
- Session cookies must be `Secure; HttpOnly; SameSite=Lax` (or `Strict` for sensitive flows).
- Document exactly which endpoints are public, which require auth, and which require admin.

## Pagination

- **Cursor-based** for any collection that grows. Returns `{data: [...], next_cursor: "..."}`.
- **Page-based** (`?page=2&per_page=20`) only for small, bounded collections. Page-based breaks under concurrent writes.

## Output checklist

For any new endpoint, produce a one-pager:

```
## Endpoint: POST /v1/users/{id}/orders
- Auth: Bearer token, must own the user_id
- Idempotency: Idempotency-Key header required
- Request body: { items: [...], shipping_address_id: "..." }
- Success: 201 Created with the new order, Location header
- Errors: 400 (validation), 404 (user not found), 409 (out of stock)
- Rate limit: 60/min per user
```
