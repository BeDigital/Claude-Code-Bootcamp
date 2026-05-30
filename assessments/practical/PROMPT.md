# PROMPT.md — Bookmarks API (GCOE)

## MCP Context

Context for this brief was gathered via the **GitHub MCP server** (`mcp__github__get_file_contents`)
before any code was written:

- Retrieved `module-04/winner/notes_api.py` — confirmed stack, DB helper patterns, and field names.
- Retrieved `module-04/winner/test_notes_api.py` — confirmed fixture strategy and assertion shape.

The Examples section below reflects what was observed, not assumed.

---

## Goal

Build a single-file Bookmarks REST API in Python 3.14 using FastAPI and stdlib sqlite3.
The API exposes five endpoints:

| Method | Path | Behaviour |
|--------|------|-----------|
| POST | /bookmarks | Create a bookmark with {url, title, tag}; return 201 + created record |
| GET | /bookmarks | List all bookmarks ordered by id ascending |
| GET | /bookmarks?tag=\<t\> | Filter by exact tag match (= not LIKE); return empty list when no match |
| GET | /bookmarks/:id | Fetch one or 404 |
| DELETE | /bookmarks/:id | Delete or 404; return 204 with empty body |

Persist to SQLite using WAL mode, `row_factory = sqlite3.Row`, and a `lifespan` startup hook
that calls `init_db()`.

## Constraints

- **Single file** — `bookmarks_api.py`. No new packages beyond fastapi, httpx, pytest.
- **stdlib sqlite3 only** — no ORM, no SQLAlchemy.
- **Timestamps** — always `datetime.now(timezone.utc).isoformat()`; never without timezone.
- **Pydantic validators** — reject blank/whitespace `url` and `title` at the boundary (422).
- **tag** — defaults to `""` if omitted; stored as-is; filter is exact match.
- **No PATCH** — bookmarks are immutable once created.
- **404 shape** — `{"error": "not found"}` via a `_fetch_one(conn, id)` helper that raises
  `HTTPException(status_code=404)`.
- **No bare except** — raise HTTPException or let FastAPI handle validation errors.
- **Shebang + docstring** — `#!/usr/bin/env python3` and
  `"""Bookmarks REST API — FastAPI + sqlite3, single-file."""`

## Output format

One Python file, sections in this order:

1. Shebang + docstring
2. Imports (stdlib before third-party)
3. `DB_PATH` constant
4. `get_db()`, `init_db()`, `lifespan`, `app = FastAPI(lifespan=lifespan)`
5. Schemas: `BookmarkIn`, `BookmarkOut`
6. Helpers: `_now()`, `_row_to_bookmark()`, `_fetch_one()`
7. Routes: POST, GET list, GET one, DELETE

snake_case throughout. One-line function docstrings only.

## Examples

Reference: `module-04/winner/notes_api.py`.
Key differences from Notes API:
- Table `bookmarks` with columns `(id, url, title, tag, created_at)` — no `body`, no `updated_at`
- Tag filter uses `WHERE tag = ?` (exact) not `LIKE`
- No PATCH route
- `BookmarkIn` validates both `url` and `title` for blank/whitespace
