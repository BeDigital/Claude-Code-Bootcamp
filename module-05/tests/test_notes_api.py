#!/usr/bin/env python3
"""pytest suite for module-04 winner Notes API — imports the real module."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import notes_api


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Patch DB_PATH to a fresh temp file; start the ASGI app in-process."""
    monkeypatch.setattr(notes_api, "DB_PATH", tmp_path / "test.db")
    with TestClient(notes_api.app) as c:
        yield c


def make_note(client: TestClient, title: str = "Hello", body: str = "World") -> dict:
    """POST a note and return the response JSON."""
    r = client.post("/notes", json={"title": title, "body": body})
    assert r.status_code == 201
    return r.json()


# ── create ─────────────────────────────────────────────────────────────────────

def test_create_returns_201(client):
    """POST /notes returns 201 with full note body."""
    r = client.post("/notes", json={"title": "t", "body": "b"})
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "t"
    assert data["body"] == "b"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_body_defaults_empty(client):
    """body field is optional; defaults to empty string."""
    r = client.post("/notes", json={"title": "no body"})
    assert r.status_code == 201
    assert r.json()["body"] == ""


def test_create_blank_title_returns_422(client):
    """Blank title is rejected with 422."""
    r = client.post("/notes", json={"title": "   ", "body": "x"})
    assert r.status_code == 422


def test_create_missing_title_returns_422(client):
    """Missing title field is rejected with 422."""
    r = client.post("/notes", json={"body": "x"})
    assert r.status_code == 422


# ── list ───────────────────────────────────────────────────────────────────────

def test_list_empty(client):
    """GET /notes on empty DB returns empty list."""
    r = client.get("/notes")
    assert r.status_code == 200
    assert r.json() == []


def test_list_returns_all(client):
    """GET /notes returns all created notes."""
    make_note(client, "first", "a")
    make_note(client, "second", "b")
    r = client.get("/notes")
    assert r.status_code == 200
    assert len(r.json()) == 2


# ── search ─────────────────────────────────────────────────────────────────────

def test_search_by_title(client):
    """q= matches notes where title contains the substring."""
    make_note(client, "FastAPI guide", "some body")
    make_note(client, "unrelated", "other")
    r = client.get("/notes?q=FastAPI")
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 1
    assert results[0]["title"] == "FastAPI guide"


def test_search_by_body(client):
    """q= matches notes where body contains the substring — not title."""
    make_note(client, "plain title", "secret keyword here")
    make_note(client, "other", "nothing special")
    r = client.get("/notes?q=secret")
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 1
    assert results[0]["body"] == "secret keyword here"


def test_search_empty_q_returns_all(client):
    """q= with empty string returns all notes (falsy, no filter applied)."""
    make_note(client, "a")
    make_note(client, "b")
    r = client.get("/notes?q=")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_search_no_match_returns_empty(client):
    """q= that matches nothing returns empty list."""
    make_note(client, "alpha", "beta")
    r = client.get("/notes?q=zzz")
    assert r.status_code == 200
    assert r.json() == []


# ── get one ────────────────────────────────────────────────────────────────────

def test_get_one(client):
    """GET /notes/{id} returns the correct note."""
    note = make_note(client, "specific", "detail")
    r = client.get(f"/notes/{note['id']}")
    assert r.status_code == 200
    assert r.json()["title"] == "specific"


def test_get_missing_returns_404(client):
    """GET /notes/999 returns 404 with correct body shape."""
    r = client.get("/notes/999")
    assert r.status_code == 404
    assert r.json() == {"detail": {"error": "not found"}}


# ── update ─────────────────────────────────────────────────────────────────────

def test_patch_title(client):
    """PATCH /notes/{id} with title updates only title."""
    note = make_note(client, "old title", "body stays")
    r = client.patch(f"/notes/{note['id']}", json={"title": "new title"})
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "new title"
    assert data["body"] == "body stays"


def test_patch_body(client):
    """PATCH /notes/{id} with body updates only body."""
    note = make_note(client, "title stays", "old body")
    r = client.patch(f"/notes/{note['id']}", json={"body": "new body"})
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "title stays"
    assert data["body"] == "new body"


def test_patch_updates_updated_at(client):
    """PATCH updates updated_at but preserves created_at."""
    note = make_note(client, "t", "b")
    r = client.patch(f"/notes/{note['id']}", json={"title": "updated"})
    assert r.status_code == 200
    data = r.json()
    assert data["created_at"] == note["created_at"]
    assert data["updated_at"] >= note["updated_at"]


def test_patch_missing_returns_404(client):
    """PATCH /notes/999 returns 404 with correct body shape."""
    r = client.patch("/notes/999", json={"title": "ghost"})
    assert r.status_code == 404
    assert r.json() == {"detail": {"error": "not found"}}


def test_patch_blank_title_returns_422(client):
    """PATCH with blank title is rejected with 422."""
    note = make_note(client)
    r = client.patch(f"/notes/{note['id']}", json={"title": "  "})
    assert r.status_code == 422


# ── delete ─────────────────────────────────────────────────────────────────────

def test_delete_returns_204(client):
    """DELETE /notes/{id} returns 204 and removes the note."""
    note = make_note(client)
    r = client.delete(f"/notes/{note['id']}")
    assert r.status_code == 204
    assert client.get(f"/notes/{note['id']}").status_code == 404


def test_delete_missing_returns_404(client):
    """DELETE /notes/999 returns 404 with correct body shape."""
    r = client.delete("/notes/999")
    assert r.status_code == 404
    assert r.json() == {"detail": {"error": "not found"}}
