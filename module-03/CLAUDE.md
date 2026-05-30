# Stack
- Python 3.14 — standard interpreter for all modules
- FastAPI + sqlite3 (stdlib) for REST APIs; httpx + pytest for tests
- argparse for all CLIs — never hand-roll sys.argv parsing
- Node.js v22 present but unused in current modules

# Conventions
- Every executable script starts with `#!/usr/bin/env python3`
- Module-level docstring format: `"""Name — one-line description."""`
- Every function gets exactly one line of docstring — no multi-line blocks
- snake_case for all identifiers (files, functions, variables, modules)
- Single-file modules preferred; split only when the file exceeds ~200 lines
- Always use `datetime.now(timezone.utc).isoformat()` for timestamps — never `datetime.now()` without timezone
- Exit 0 on success, 1 on error in all CLI scripts

# Commands
- Run tests:  `pytest <module>/winner/ -v`
- Run API:    `cd <module>/winner && uvicorn notes_api:app --reload`
- Run CLI:    `python3 task.py`
- No Makefile or build step — run commands above directly

# Do-not
- Never add a package (pip install, npm install) without asking first
- Never use `datetime.now()` without `timezone.utc` — local timestamps break reproducibility
- Never write multi-line docstrings — one line only
- Never hand-roll `sys.argv` parsing — always use argparse
- Never create files outside the current module directory without asking

# Glossary
- Module: numbered learning unit (module-01 through module-10), each self-contained
- Winner: the selected implementation after Best-of-N evaluation lives in `<module>/winner/`
- Candidate: a competing implementation generated for Best-of-N selection
- Best-of-N: generate N candidates, evaluate against rubric, promote one to `winner/`
