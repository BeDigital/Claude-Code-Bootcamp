#!/usr/bin/env python3
"""Bookmarks REST API — FastAPI + sqlite3, single-file."""

import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, field_validator

DB_PATH = Path(__file__).parent / "bookmarks.db"


def get_db() -> sqlite3.Connection:
    """Open and return a WAL-mode SQLite connection with Row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    """Create the bookmarks table if it does not exist."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                url        TEXT    NOT NULL,
                title      TEXT    NOT NULL,
                tag        TEXT    NOT NULL DEFAULT '',
                created_at TEXT    NOT NULL
            )
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run init_db on startup."""
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


# ---------- schemas ----------

class BookmarkIn(BaseModel):
    url: str
    title: str
    tag: str = ""

    @field_validator("url")
    @classmethod
    def url_not_empty(cls, v: str) -> str:
        """Reject blank or whitespace-only URLs."""
        if not v.strip():
            raise ValueError("url must not be blank")
        return v

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Reject blank or whitespace-only titles."""
        if not v.strip():
            raise ValueError("title must not be blank")
        return v


class BookmarkOut(BaseModel):
    id: int
    url: str
    title: str
    tag: str
    created_at: str


# ---------- helpers ----------

def _now() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _row_to_bookmark(row: sqlite3.Row) -> BookmarkOut:
    """Convert a sqlite3.Row to a BookmarkOut model."""
    return BookmarkOut(**dict(row))


def _fetch_one(conn: sqlite3.Connection, bookmark_id: int) -> sqlite3.Row:
    """Return the row for bookmark_id or raise 404."""
    row = conn.execute(
        "SELECT * FROM bookmarks WHERE id = ?", (bookmark_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail={"error": "not found"})
    return row


# ---------- routes ----------

@app.get("/health")
def health_check():
    """Return 200 with a live DB ping if the service is operational."""
    with get_db() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok", "db": "connected"}


@app.post("/bookmarks", status_code=201, response_model=BookmarkOut)
def create_bookmark(payload: BookmarkIn):
    """Create a new bookmark and return it."""
    now = _now()
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO bookmarks (url, title, tag, created_at) VALUES (?, ?, ?, ?)",
            (payload.url, payload.title, payload.tag, now),
        )
        return _row_to_bookmark(
            conn.execute(
                "SELECT * FROM bookmarks WHERE id = ?", (cur.lastrowid,)
            ).fetchone()
        )


@app.get("/bookmarks", response_model=list[BookmarkOut])
def list_bookmarks(tag: Optional[str] = Query(default=None)):
    """List all bookmarks, or filter by exact tag match when tag is provided."""
    with get_db() as conn:
        if tag is not None:
            rows = conn.execute(
                "SELECT * FROM bookmarks WHERE tag = ? ORDER BY id", (tag,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM bookmarks ORDER BY id").fetchall()
    return [_row_to_bookmark(r) for r in rows]


@app.get("/bookmarks/{bookmark_id}", response_model=BookmarkOut)
def get_bookmark(bookmark_id: int):
    """Fetch a single bookmark by id or return 404."""
    with get_db() as conn:
        return _row_to_bookmark(_fetch_one(conn, bookmark_id))


@app.delete("/bookmarks/{bookmark_id}", status_code=204)
def delete_bookmark(bookmark_id: int):
    """Delete a bookmark by id or return 404."""
    with get_db() as conn:
        _fetch_one(conn, bookmark_id)
        conn.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
