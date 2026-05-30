# Notes API

A simple Notes API with SQLite persistence, built with FastAPI and Pydantic v2.

## Setup and Run

```bash
pip install fastapi pydantic uvicorn
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000` with OpenAPI docs at `/docs`.
