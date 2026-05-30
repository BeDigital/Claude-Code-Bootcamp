# Notes API

SQLite-backed REST API built with FastAPI + Pydantic v2.

## Run

```bash
pip install fastapi uvicorn
uvicorn notes_api:app --reload
```

## Endpoints

| Method | Path | Body | Status |
|--------|------|------|--------|
| POST | `/notes` | `{"title":"…","body":"…"}` | 201 |
| GET | `/notes?q=` | — | 200 |
| GET | `/notes/{id}` | — | 200 / 404 |
| PATCH | `/notes/{id}` | `{"title":"…","body":"…"}` (partial) | 200 / 404 / 422 |
| DELETE | `/notes/{id}` | — | 204 / 404 |
