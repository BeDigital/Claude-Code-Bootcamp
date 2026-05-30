"""pytest suite for Bookmarks API (FastAPI + SQLite).

Strategy
--------
* httpx via FastAPI TestClient — in-process, no network
* monkeypatch DB_PATH before lifespan fires — each test gets its own tmp SQLite file
* imports the real app module — no mocking of the SUT

Run:
    pytest assessments/practical/tests/ -v
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app


# ── fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Isolated DB per test via monkeypatched DB_PATH."""
    monkeypatch.setattr(app, "DB_PATH", tmp_path / "test_bookmarks.db")
    with TestClient(app.app) as c:
        yield c


def make_bookmark(client, url="https://example.com", title="Example", tag="misc"):
    """POST a bookmark and return the response."""
    return client.post("/bookmarks", json={"url": url, "title": title, "tag": tag})


# ══════════════════════════════════════════════════════════════════════════════
# HAPPY PATH
# ══════════════════════════════════════════════════════════════════════════════

class TestCreate:
    def test_returns_201(self, client):
        assert make_bookmark(client).status_code == 201

    def test_response_contains_all_fields(self, client):
        data = make_bookmark(client, url="https://a.com", title="Alpha", tag="t1").json()
        assert data["url"] == "https://a.com"
        assert data["title"] == "Alpha"
        assert data["tag"] == "t1"
        assert isinstance(data["id"], int)
        assert "created_at" in data

    def test_tag_defaults_to_empty_string(self, client):
        r = client.post("/bookmarks", json={"url": "https://b.com", "title": "Beta"})
        assert r.status_code == 201
        assert r.json()["tag"] == ""


class TestList:
    def test_empty_db_returns_empty_list(self, client):
        r = client.get("/bookmarks")
        assert r.status_code == 200
        assert r.json() == []

    def test_returns_all_bookmarks(self, client):
        make_bookmark(client, title="A")
        make_bookmark(client, title="B")
        assert len(client.get("/bookmarks").json()) == 2

    def test_ordered_by_id_ascending(self, client):
        make_bookmark(client, title="First")
        make_bookmark(client, title="Second")
        titles = [b["title"] for b in client.get("/bookmarks").json()]
        assert titles == ["First", "Second"]


class TestGetOne:
    def test_returns_200_for_existing(self, client):
        bm_id = make_bookmark(client).json()["id"]
        assert client.get(f"/bookmarks/{bm_id}").status_code == 200

    def test_returns_correct_bookmark(self, client):
        bm_id = make_bookmark(client, url="https://c.com", title="Gamma", tag="g").json()["id"]
        data = client.get(f"/bookmarks/{bm_id}").json()
        assert data["url"] == "https://c.com"
        assert data["title"] == "Gamma"
        assert data["tag"] == "g"


class TestDelete:
    def test_returns_204(self, client):
        bm_id = make_bookmark(client).json()["id"]
        assert client.delete(f"/bookmarks/{bm_id}").status_code == 204

    def test_response_body_is_empty(self, client):
        bm_id = make_bookmark(client).json()["id"]
        assert client.delete(f"/bookmarks/{bm_id}").content == b""

    def test_removed_from_list_after_delete(self, client):
        gone_id = make_bookmark(client, title="Gone").json()["id"]
        make_bookmark(client, title="Stays")
        client.delete(f"/bookmarks/{gone_id}")
        titles = [b["title"] for b in client.get("/bookmarks").json()]
        assert "Gone" not in titles
        assert "Stays" in titles


# ══════════════════════════════════════════════════════════════════════════════
# ERROR PATHS
# ══════════════════════════════════════════════════════════════════════════════

class Test404:
    GHOST = 99999

    def test_get_nonexistent_returns_404(self, client):
        r = client.get(f"/bookmarks/{self.GHOST}")
        assert r.status_code == 404
        assert r.json()["detail"] == {"error": "not found"}

    def test_delete_nonexistent_returns_404(self, client):
        r = client.delete(f"/bookmarks/{self.GHOST}")
        assert r.status_code == 404
        assert r.json()["detail"] == {"error": "not found"}

    def test_get_after_delete_is_404(self, client):
        bm_id = make_bookmark(client).json()["id"]
        client.delete(f"/bookmarks/{bm_id}")
        assert client.get(f"/bookmarks/{bm_id}").status_code == 404


class Test422:
    def test_missing_url_field(self, client):
        r = client.post("/bookmarks", json={"title": "No URL"})
        assert r.status_code == 422

    def test_blank_url_rejected(self, client):
        r = client.post("/bookmarks", json={"url": "   ", "title": "Blank URL"})
        assert r.status_code == 422

    def test_blank_title_rejected(self, client):
        r = client.post("/bookmarks", json={"url": "https://x.com", "title": "  "})
        assert r.status_code == 422

    def test_missing_title_field(self, client):
        r = client.post("/bookmarks", json={"url": "https://x.com"})
        assert r.status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
# BOUNDARY — tag filter
# ══════════════════════════════════════════════════════════════════════════════

class TestTagFilter:
    def test_filter_returns_only_matching_tag(self, client):
        make_bookmark(client, title="Py", tag="python")
        make_bookmark(client, title="JS", tag="javascript")
        results = client.get("/bookmarks", params={"tag": "python"}).json()
        assert len(results) == 1
        assert results[0]["title"] == "Py"

    def test_filter_no_match_returns_empty_list(self, client):
        make_bookmark(client, tag="python")
        results = client.get("/bookmarks", params={"tag": "rust"}).json()
        assert results == []

    def test_filter_is_exact_not_substring(self, client):
        make_bookmark(client, tag="python")
        # "py" must NOT match "python" — filter is = not LIKE
        results = client.get("/bookmarks", params={"tag": "py"}).json()
        assert results == []

    def test_no_tag_param_returns_all(self, client):
        make_bookmark(client, tag="python")
        make_bookmark(client, tag="js")
        results = client.get("/bookmarks").json()
        assert len(results) == 2

    def test_multiple_bookmarks_same_tag(self, client):
        make_bookmark(client, title="A", tag="python")
        make_bookmark(client, title="B", tag="python")
        make_bookmark(client, title="C", tag="js")
        results = client.get("/bookmarks", params={"tag": "python"}).json()
        assert len(results) == 2
        assert all(b["tag"] == "python" for b in results)
