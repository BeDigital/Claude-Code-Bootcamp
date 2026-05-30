#!/usr/bin/env python3
"""Notes REST API — FastAPI + sqlite3, single-file."""

import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, field_validator

DB_PATH = Path(__file__).parent / "notes.db"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT    NOT NULL,
                body       TEXT    NOT NULL DEFAULT '',
                created_at TEXT    NOT NULL,
                updated_at TEXT    NOT NULL
            )
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


# ---------- schemas ----------

class NoteIn(BaseModel):
    title: str
    body: str = ""

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be blank")
        return v


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("title must not be blank")
        return v


class NoteOut(BaseModel):
    id: int
    title: str
    body: str
    created_at: str
    updated_at: str


# ---------- helpers ----------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_note(row: sqlite3.Row) -> NoteOut:
    return NoteOut(**dict(row))


def _fetch_one(conn: sqlite3.Connection, note_id: int) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail={"error": "not found"})
    return row


# ---------- routes ----------

@app.post("/notes", status_code=201, response_model=NoteOut)
def create_note(payload: NoteIn):
    now = _now()
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO notes (title, body, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (payload.title, payload.body, now, now),
        )
        return _row_to_note(conn.execute("SELECT * FROM notes WHERE id = ?", (cur.lastrowid,)).fetchone())


@app.get("/notes", response_model=list[NoteOut])
def list_notes(q: Optional[str] = Query(default=None)):
    with get_db() as conn:
        if q:
            rows = conn.execute(
                "SELECT * FROM notes WHERE title LIKE ? OR body LIKE ? ORDER BY id",
                (f"%{q}%", f"%{q}%"),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM notes ORDER BY id").fetchall()
    return [_row_to_note(r) for r in rows]


@app.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: int):
    with get_db() as conn:
        return _row_to_note(_fetch_one(conn, note_id))


@app.patch("/notes/{note_id}", response_model=NoteOut)
def update_note(note_id: int, payload: NoteUpdate):
    with get_db() as conn:
        row = _fetch_one(conn, note_id)
        title = payload.title if payload.title is not None else row["title"]
        body = payload.body if payload.body is not None else row["body"]
        now = _now()
        conn.execute(
            "UPDATE notes SET title = ?, body = ?, updated_at = ? WHERE id = ?",
            (title, body, now, note_id),
        )
        return _row_to_note(conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone())


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    with get_db() as conn:
        _fetch_one(conn, note_id)
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
