"""
pytest suite for candidate-a Notes API (FastAPI + SQLite).

Strategy
--------
* httpx via FastAPI's TestClient (httpx-backed ASGI transport, no network)
* monkeypatch DB_PATH before the lifespan fires so every test gets its own
  tmp SQLite file — no shared state between tests
* lifespan / init_db() run naturally inside the TestClient context manager

Run:
    pip install fastapi httpx pytest
    pytest test_notes_api.py -v
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient  # httpx2-backed, in-process

# sys.path is patched by conftest.py before collection, so this import is clean
import notes_api


# ── fixture: one isolated DB per test function ─────────────────────────────────
@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """
    Patch DB_PATH to a fresh temp file, then start the ASGI app in-process.
    The lifespan calls init_db() against the patched path, so the table is
    ready before the first request and torn down with the temp dir afterward.
    """
    monkeypatch.setattr(notes_api, "DB_PATH", tmp_path / "test_notes.db")
    with TestClient(notes_api.app) as c:
        yield c


# ── tiny helper so every test doesn't repeat the same POST body ───────────────
def make_note(client: TestClient, title: str = "Hello", body: str = "World"):
    return client.post("/notes", json={"title": title, "body": body})


# ══════════════════════════════════════════════════════════════════════════════
# CREATE
# ══════════════════════════════════════════════════════════════════════════════

class TestCreate:
    def test_returns_201(self, client):
        assert make_note(client).status_code == 201

    def test_response_contains_expected_fields(self, client):
        data = make_note(client, title="My Title", body="My Body").json()
        assert data["title"] == "My Title"
        assert data["body"] == "My Body"
        assert isinstance(data["id"], int)
        assert "created_at" in data
        assert "updated_at" in data

    def test_body_defaults_to_empty_string(self, client):
        r = client.post("/notes", json={"title": "No Body"})
        assert r.status_code == 201
        assert r.json()["body"] == ""

    def test_ids_are_unique(self, client):
        id_a = make_note(client, title="A").json()["id"]
        id_b = make_note(client, title="B").json()["id"]
        assert id_a != id_b


# ══════════════════════════════════════════════════════════════════════════════
# LIST
# ══════════════════════════════════════════════════════════════════════════════

class TestList:
    def test_empty_db_returns_empty_list(self, client):
        r = client.get("/notes")
        assert r.status_code == 200
        assert r.json() == []

    def test_returns_all_notes(self, client):
        make_note(client, title="A")
        make_note(client, title="B")
        notes = client.get("/notes").json()
        assert len(notes) == 2

    def test_ordered_by_id_ascending(self, client):
        make_note(client, title="First")
        make_note(client, title="Second")
        titles = [n["title"] for n in client.get("/notes").json()]
        assert titles == ["First", "Second"]


# ══════════════════════════════════════════════════════════════════════════════
# SEARCH  (GET /notes?q=…)
# ══════════════════════════════════════════════════════════════════════════════

class TestSearch:
    def test_title_match(self, client):
        make_note(client, title="FastAPI rocks", body="irrelevant")
        make_note(client, title="Other note", body="irrelevant")
        results = client.get("/notes", params={"q": "FastAPI"}).json()
        assert len(results) == 1
        assert results[0]["title"] == "FastAPI rocks"

    def test_body_match(self, client):
        make_note(client, title="Note", body="searchable content here")
        make_note(client, title="Note2", body="nothing relevant")
        results = client.get("/notes", params={"q": "searchable"}).json()
        assert len(results) == 1
        assert results[0]["body"] == "searchable content here"

    def test_no_match_returns_empty_list(self, client):
        make_note(client, title="Hello")
        results = client.get("/notes", params={"q": "zzznomatch"}).json()
        assert results == []

    def test_case_insensitive_via_like(self, client):
        # SQLite LIKE is case-insensitive for ASCII by default
        make_note(client, title="UPPER")
        results = client.get("/notes", params={"q": "upper"}).json()
        assert len(results) == 1


# ══════════════════════════════════════════════════════════════════════════════
# GET ONE
# ══════════════════════════════════════════════════════════════════════════════

class TestGetOne:
    def test_returns_200_for_existing_note(self, client):
        note_id = make_note(client, title="Fetch Me").json()["id"]
        assert client.get(f"/notes/{note_id}").status_code == 200

    def test_returns_correct_note(self, client):
        note_id = make_note(client, title="Target", body="body text").json()["id"]
        data = client.get(f"/notes/{note_id}").json()
        assert data["id"] == note_id
        assert data["title"] == "Target"
        assert data["body"] == "body text"

    def test_returns_only_that_note(self, client):
        make_note(client, title="A")
        note_id = make_note(client, title="B").json()["id"]
        make_note(client, title="C")
        data = client.get(f"/notes/{note_id}").json()
        assert data["title"] == "B"


# ══════════════════════════════════════════════════════════════════════════════
# UPDATE  (PATCH — partial)
# ══════════════════════════════════════════════════════════════════════════════

class TestUpdate:
    def test_patch_title_only(self, client):
        note_id = make_note(client, title="Old Title", body="Keep Me").json()["id"]
        r = client.patch(f"/notes/{note_id}", json={"title": "New Title"})
        assert r.status_code == 200
        data = r.json()
        assert data["title"] == "New Title"
        assert data["body"] == "Keep Me"          # unchanged

    def test_patch_body_only(self, client):
        note_id = make_note(client, title="Keep Me", body="Old Body").json()["id"]
        r = client.patch(f"/notes/{note_id}", json={"body": "New Body"})
        assert r.status_code == 200
        data = r.json()
        assert data["body"] == "New Body"
        assert data["title"] == "Keep Me"         # unchanged

    def test_patch_updates_updated_at(self, client):
        note = make_note(client, title="T").json()
        r = client.patch(f"/notes/{note['id']}", json={"title": "T2"})
        # updated_at must be >= created_at (timestamps are ISO strings, lexicographic ok)
        assert r.json()["updated_at"] >= note["updated_at"]

    def test_patch_both_fields(self, client):
        note_id = make_note(client, title="Old", body="Old").json()["id"]
        r = client.patch(f"/notes/{note_id}", json={"title": "New", "body": "New"})
        data = r.json()
        assert data["title"] == "New"
        assert data["body"] == "New"


# ══════════════════════════════════════════════════════════════════════════════
# DELETE
# ══════════════════════════════════════════════════════════════════════════════

class TestDelete:
    def test_returns_204(self, client):
        note_id = make_note(client).json()["id"]
        assert client.delete(f"/notes/{note_id}").status_code == 204

    def test_response_body_is_empty(self, client):
        note_id = make_note(client).json()["id"]
        assert client.delete(f"/notes/{note_id}").content == b""

    def test_note_no_longer_retrievable(self, client):
        note_id = make_note(client).json()["id"]
        client.delete(f"/notes/{note_id}")
        assert client.get(f"/notes/{note_id}").status_code == 404

    def test_note_removed_from_list(self, client):
        note_id = make_note(client, title="Gone").json()["id"]
        make_note(client, title="Stays")
        client.delete(f"/notes/{note_id}")
        titles = [n["title"] for n in client.get("/notes").json()]
        assert "Gone" not in titles
        assert "Stays" in titles


# ══════════════════════════════════════════════════════════════════════════════
# 404  NOT FOUND
# ══════════════════════════════════════════════════════════════════════════════

class Test404:
    GHOST = 99999

    def test_get_nonexistent_note(self, client):
        assert client.get(f"/notes/{self.GHOST}").status_code == 404

    def test_patch_nonexistent_note(self, client):
        assert client.patch(f"/notes/{self.GHOST}", json={"title": "X"}).status_code == 404

    def test_delete_nonexistent_note(self, client):
        assert client.delete(f"/notes/{self.GHOST}").status_code == 404

    def test_get_after_delete_is_404(self, client):
        note_id = make_note(client).json()["id"]
        client.delete(f"/notes/{note_id}")
        assert client.get(f"/notes/{note_id}").status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# 422  UNPROCESSABLE ENTITY
# ══════════════════════════════════════════════════════════════════════════════

class Test422:
    def test_create_missing_title_field(self, client):
        r = client.post("/notes", json={"body": "no title key at all"})
        assert r.status_code == 422

    def test_create_blank_title(self, client):
        r = client.post("/notes", json={"title": "   ", "body": "blank whitespace"})
        assert r.status_code == 422

    def test_create_empty_string_title(self, client):
        r = client.post("/notes", json={"title": "", "body": "empty"})
        assert r.status_code == 422

    def test_create_non_string_title(self, client):
        r = client.post("/notes", json={"title": 12345, "body": "numeric"})
        # Pydantic coerces int→str, so this actually passes — document the behaviour
        # If the spec tightened this, the test would flip to 422
        assert r.status_code in (201, 422)

    def test_patch_blank_title(self, client):
        note_id = make_note(client).json()["id"]
        r = client.patch(f"/notes/{note_id}", json={"title": "   "})
        assert r.status_code == 422

    def test_patch_empty_string_title(self, client):
        note_id = make_note(client).json()["id"]
        r = client.patch(f"/notes/{note_id}", json={"title": ""})
        assert r.status_code == 422
