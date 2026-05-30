# Bookmarks API — Practical Assessment

## Run the service

```bash
cd assessments/practical/service
uv run --no-project --with fastapi --with uvicorn uvicorn app:app --reload
```

Server starts on `http://localhost:8000`.

## Run the tests

```bash
uv run --no-project --with fastapi --with httpx --with pytest \
  pytest assessments/practical/tests/ -v
```

Expected: **23 passed**.

## Smoke script

```bash
curl -X POST localhost:8000/bookmarks \
  -H 'content-type: application/json' \
  -d '{"url":"https://example.com","title":"ex","tag":"misc"}'   # 201

curl localhost:8000/bookmarks                                    # 200
curl 'localhost:8000/bookmarks?tag=misc'                         # 200
curl localhost:8000/bookmarks/1                                  # 200
curl -X DELETE localhost:8000/bookmarks/1                        # 204
curl localhost:8000/bookmarks/99                                 # 404
curl localhost:8000/health                                       # 200
```
