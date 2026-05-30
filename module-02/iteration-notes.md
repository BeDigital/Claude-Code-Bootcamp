# Iteration Notes — Module 02

## Original prompt (v1)

```
GOAL
Build a single-binary CLI Task Manager so a developer can manage TODOs from the terminal.

CONSTRAINTS
- Language: Python 3.11 (stdlib only)
- Persistence: a single JSON file `tasks.json` in CWD.
- No background processes. No network calls.
- Exit code 0 on success, 1 on user error, 2 on internal error.
- All user-facing strings in English.

OUTPUT FORMAT
- One source file (task.py)
- A short README explaining install + the four commands.

EXAMPLES
- `task add "Write the spec"` → "Added task #1: Write the spec"
- `task list` → tabular: id, status, created_at, text
- `task done 1` → "Marked #1 as done"
- `task delete 99` → exit 1, "No task with id 99"
```

v1 produced a working tool with the four core commands and correct exit codes.

---

## Prompt edit (v2 — stretch challenge)

Added one sentence to the OUTPUT FORMAT section:

```diff
- `task list` → tabular: id, status, created_at, text
+ `task list` → tabular: id, status, created_at, text
+ `task list --status open` → only open tasks
+ `task list --status done` → only completed tasks
```

Full addition to EXAMPLES:

```
- `task list --status open` → only tasks with status "open"
- `task list --status done` → only tasks with status "done"
- Invalid --status value → argparse rejects with exit 2
```

---

## What changed in the code

**Diff summary:**

```diff
# p_list subparser — added --status argument
+ p_list.add_argument(
+     "--status",
+     choices=["open", "done"],
+     default=None,
+     help="Filter by status (open or done)",
+ )

# cmd_list — added filter logic before printing
+ if hasattr(args, "status") and args.status:
+     tasks = [t for t in tasks if t["status"] == args.status]
```

**Lines changed:** ~7 lines added, 0 removed.

**Behavior change:**
- `task list` with no flag still shows all tasks (unchanged).
- `task list --status open` filters to only open tasks.
- `task list --status done` filters to only done tasks.
- Passing any other value (e.g., `--status pending`) is rejected by argparse at parse time with a usage error, which exits non-zero — consistent with the exit code contract.

---

## Takeaways

The original prompt was tight enough that the stretch feature required only a minimal, additive change — no refactoring. Adding explicit filter examples to the EXAMPLES section was sufficient to drive the right implementation without any ambiguity about desired behavior (show header even when empty, use `choices=` for validation).
