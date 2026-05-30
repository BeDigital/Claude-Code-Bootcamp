# CLI Task Manager

A minimal task manager for the terminal. Python 3.11, stdlib only, single file.

## Install

No install needed. Run directly with Python 3.11+.

```bash
python3 task.py <command> [args]
```

`tasks.json` is created in the current working directory on first use.

## Commands

### Add a task

```bash
python3 task.py add "Task description"
```

Output: `Added task #1: Task description`  
Exit: `0`

### List tasks

```bash
python3 task.py list
```

Output: tabular view with `id`, `status`, `created_at`, and `text`.

Optional filter by status:

```bash
python3 task.py list --status open
python3 task.py list --status done
```

### Mark a task done

```bash
python3 task.py done 1
```

Output: `Marked #1 as done`  
Exit: `0` on success, `1` if the ID does not exist.

### Delete a task

```bash
python3 task.py delete 1
```

Output: `Deleted task #1`  
Exit: `0` on success, `1` if the ID does not exist.

## Exit codes

| Code | Meaning |
|------|---------|
| `0`  | Success |
| `1`  | User error (bad ID, bad args) |
| `2`  | Internal error (I/O failure) |
