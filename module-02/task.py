#!/usr/bin/env python3
"""CLI Task Manager — stdlib only, JSON persistence."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

TASKS_FILE = os.path.join(os.getcwd(), "tasks.json")


def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return {"next_id": 1, "tasks": []}
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading {TASKS_FILE}: {e}", file=sys.stderr)
        sys.exit(2)


def save_tasks(data):
    try:
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        print(f"Error writing {TASKS_FILE}: {e}", file=sys.stderr)
        sys.exit(2)


def cmd_add(args):
    data = load_tasks()
    task_id = data["next_id"]
    data["next_id"] += 1
    data["tasks"].append({
        "id": task_id,
        "status": "open",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "text": args.text,
    })
    save_tasks(data)
    print(f"Added task #{task_id}: {args.text}")


def cmd_list(args):
    data = load_tasks()
    tasks = data["tasks"]

    if hasattr(args, "status") and args.status:
        tasks = [t for t in tasks if t["status"] == args.status]

    if not tasks:
        print(f"{'ID':<6} {'STATUS':<8} {'CREATED':<22} TEXT")
        print("-" * 60)
        return

    print(f"{'ID':<6} {'STATUS':<8} {'CREATED':<22} TEXT")
    print("-" * 60)
    for t in tasks:
        print(f"{t['id']:<6} {t['status']:<8} {t['created_at']:<22} {t['text']}")


def cmd_done(args):
    data = load_tasks()
    for t in data["tasks"]:
        if t["id"] == args.id:
            t["status"] = "done"
            save_tasks(data)
            print(f"Marked #{args.id} as done")
            return
    print(f"No task with id {args.id}", file=sys.stderr)
    sys.exit(1)


def cmd_delete(args):
    data = load_tasks()
    original_len = len(data["tasks"])
    data["tasks"] = [t for t in data["tasks"] if t["id"] != args.id]
    if len(data["tasks"]) == original_len:
        print(f"No task with id {args.id}", file=sys.stderr)
        sys.exit(1)
    save_tasks(data)
    print(f"Deleted task #{args.id}")


def main():
    parser = argparse.ArgumentParser(
        prog="task",
        description="Simple CLI task manager",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.required = True

    # add
    p_add = subparsers.add_parser("add", help="Add a new task")
    p_add.add_argument("text", help="Task description")
    p_add.set_defaults(func=cmd_add)

    # list
    p_list = subparsers.add_parser("list", help="List tasks")
    p_list.add_argument(
        "--status",
        choices=["open", "done"],
        default=None,
        help="Filter by status (open or done)",
    )
    p_list.set_defaults(func=cmd_list)

    # done
    p_done = subparsers.add_parser("done", help="Mark a task as done")
    p_done.add_argument("id", type=int, help="Task ID")
    p_done.set_defaults(func=cmd_done)

    # delete
    p_delete = subparsers.add_parser("delete", help="Delete a task")
    p_delete.add_argument("id", type=int, help="Task ID")
    p_delete.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
