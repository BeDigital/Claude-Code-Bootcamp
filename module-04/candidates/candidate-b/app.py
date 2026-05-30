#!/usr/bin/env python3
"""Notes API with SQLite persistence."""

import sqlite3
from datetime import datetime, timezone
from contextlib import contextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI()
DB_PATH = Path("notes.db")


class Note(BaseModel):
    id: int
    title: str
    body: str
    created_at: str
    updated_at: str


class NoteCreate(BaseModel):
    title: str
    body: str


class ErrorResponse(BaseModel):
    error: str


def init_db():
    """Initialize database schema on startup."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.commit()


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def now_iso() -> str:
    """Return current time in ISO 8601 UTC format."""
    return datetime.now(timezone.utc).isoformat()


@app.on_event("startup")
def startup():
    init_db()


@app.post("/notes", status_code=201, response_model=Note)
def create_note(note: NoteCreate):
    """Create a new note."""
    now = now_iso()
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO notes (title, body, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (note.title, note.body, now, now),
        )
        conn.commit()
        note_id = cursor.lastrowid

    with get_db() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        return Note(
            id=row["id"],
            title=row["title"],
            body=row["body"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@app.get("/notes", response_model=list[Note])
def list_notes(q: str | None = Query(None)):
    """List all notes, optionally filtered by query."""
    with get_db() as conn:
        if q:
            rows = conn.execute(
                "SELECT * FROM notes WHERE title LIKE ? OR body LIKE ? ORDER BY created_at DESC",
                (f"%{q}%", f"%{q}%"),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM notes ORDER BY created_at DESC"
            ).fetchall()

        return [
            Note(
                id=row["id"],
                title=row["title"],
                body=row["body"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]


@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int):
    """Get a single note by ID."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail={"error": "not found"})

    return Note(
        id=row["id"],
        title=row["title"],
        body=row["body"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: int, note: NoteCreate):
    """Update a note."""
    now = now_iso()
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM notes WHERE id = ?", (note_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail={"error": "not found"})

        conn.execute(
            "UPDATE notes SET title = ?, body = ?, updated_at = ? WHERE id = ?",
            (note.title, note.body, now, note_id),
        )
        conn.commit()

    with get_db() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        return Note(
            id=row["id"],
            title=row["title"],
            body=row["body"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    """Delete a note."""
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM notes WHERE id = ?", (note_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail={"error": "not found"})

        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()

    return None
