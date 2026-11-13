#!/usr/bin/env python3
"""CLI Task Master - A lightweight SQLite-backed terminal task manager."""

import argparse
import os
import sqlite3
import sys
from datetime import datetime

DEFAULT_DB_PATH = os.path.expanduser("~/.tasks.db")


def get_db_path(custom_path=None):
    """Return database file path."""
    if custom_path:
        return os.path.abspath(os.path.expanduser(custom_path))
    return os.getenv("TASKS_DB_PATH", DEFAULT_DB_PATH)


def init_db(db_path):
    """Initialize SQLite database and tasks table if not existing."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                priority TEXT NOT NULL CHECK(priority IN ('high', 'med', 'low')) DEFAULT 'med',
                category TEXT NOT NULL DEFAULT 'General',
                status TEXT NOT NULL CHECK(status IN ('pending', 'completed')) DEFAULT 'pending',
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
            """
        )
        conn.commit()


def render_tasks_table(tasks):
    """Render a list of task records as a clean table."""
    if not tasks:
        print("No tasks found.")
        return

    headers = ["ID", "Title", "Priority", "Category", "Status", "Created At", "Completed At"]
    rows = []
    for t in tasks:
        t_id, title, priority, category, status, created_at, completed_at = t
        status_display = "[✔] Completed" if status == "completed" else "[ ] Pending"
        priority_display = priority.upper()
        completed_display = completed_at if completed_at else "-"
        rows.append([t_id, title, priority_display, category, status_display, created_at, completed_display])

    try:
        from tabulate import tabulate

        print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    except ImportError:
        # Fallback to pure standard library formatting
        col_widths = [len(h) for h in headers]
        for row in rows:
            for idx, val in enumerate(row):
                col_widths[idx] = max(col_widths[idx], len(str(val)))

        format_str = " | ".join(f"{{:<{w}}}" for w in col_widths)
        separator = "-+-".join("-" * w for w in col_widths)

        print(format_str.format(*headers))
        print(separator)
        for row in rows:
            print(format_str.format(*[str(val) for val in row]))


def cmd_add(args):
    """Add a new task."""
    db_path = get_db_path(args.db)
    init_db(db_path)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tasks (title, priority, category, status, created_at)
            VALUES (?, ?, ?, 'pending', ?)
            """,
            (args.title.strip(), args.priority.lower(), args.category.strip(), now),
        )
        task_id = cursor.lastrowid
        conn.commit()

    print(f"Task #{task_id} added successfully: '{args.title}' [{args.priority.upper()}] ({args.category})")


def cmd_list(args):
    """List tasks with optional filters."""
    db_path = get_db_path(args.db)
    init_db(db_path)

    query = "SELECT id, title, priority, category, status, created_at, completed_at FROM tasks WHERE 1=1"
    params = []

    if args.status and args.status != "all":
        query += " AND status = ?"
        params.append(args.status.lower())

    if args.category:
        query += " AND LOWER(category) = LOWER(?)"
        params.append(args.category.strip())

    if args.priority:
        query += " AND priority = ?"
        params.append(args.priority.lower())

    query += " ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'med' THEN 2 WHEN 'low' THEN 3 END, id ASC"

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        tasks = cursor.fetchall()

    render_tasks_table(tasks)


def cmd_done(args):
    """Mark a task as completed."""
    db_path = get_db_path(args.db)
    init_db(db_path)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, status FROM tasks WHERE id = ?", (args.id,))
        task = cursor.fetchone()

        if not task:
            print(f"Error: Task #{args.id} not found.", file=sys.stderr)
            sys.exit(1)

        if task[2] == "completed":
            print(f"Task #{args.id} ('{task[1]}') is already completed.")
            return

        cursor.execute(
            "UPDATE tasks SET status = 'completed', completed_at = ? WHERE id = ?",
            (now, args.id),
        )
        conn.commit()

    print(f"Task #{args.id} ('{task[1]}') marked as completed.")


def cmd_delete(args):
    """Delete a task."""
    db_path = get_db_path(args.db)
    init_db(db_path)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM tasks WHERE id = ?", (args.id,))
        task = cursor.fetchone()

        if not task:
            print(f"Error: Task #{args.id} not found.", file=sys.stderr)
            sys.exit(1)

        cursor.execute("DELETE FROM tasks WHERE id = ?", (args.id,))
        conn.commit()

    print(f"Task #{args.id} ('{task[1]}') deleted successfully.")


def cmd_search(args):
    """Search tasks by keyword in title or category."""
    db_path = get_db_path(args.db)
    init_db(db_path)

    keyword = f"%{args.keyword.strip()}%"
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, title, priority, category, status, created_at, completed_at
            FROM tasks
            WHERE title LIKE ? OR category LIKE ?
            ORDER BY id ASC
            """,
            (keyword, keyword),
        )
        tasks = cursor.fetchall()

    render_tasks_table(tasks)


def build_parser():
    """Construct CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="cli-task-master",
        description="CLI Task Master - Lightweight SQLite-backed terminal task manager.",
    )
    parser.add_argument(
        "--db",
        help="Custom SQLite database file path (defaults to ~/.tasks.db or $TASKS_DB_PATH).",
        default=None,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    parser_add = subparsers.add_parser("add", help="Add a new task")
    parser_add.add_argument("title", help="Task title or description")
    parser_add.add_argument(
        "-p",
        "--priority",
        choices=["high", "med", "low"],
        default="med",
        help="Priority level (default: med)",
    )
    parser_add.add_argument(
        "-c",
        "--category",
        default="General",
        help="Category or tag (default: General)",
    )
    parser_add.set_defaults(func=cmd_add)

    # List command
    parser_list = subparsers.add_parser("list", help="List tasks with optional filters")
    parser_list.add_argument(
        "-s",
        "--status",
        choices=["all", "pending", "completed"],
        default="all",
        help="Filter by status (default: all)",
    )
    parser_list.add_argument(
        "-c",
        "--category",
        help="Filter by category",
        default=None,
    )
    parser_list.add_argument(
        "-p",
        "--priority",
        choices=["high", "med", "low"],
        help="Filter by priority",
        default=None,
    )
    parser_list.set_defaults(func=cmd_list)

    # Done command
    parser_done = subparsers.add_parser("done", help="Mark a task as completed")
    parser_done.add_argument("id", type=int, help="Task ID to mark complete")
    parser_done.set_defaults(func=cmd_done)

    # Delete command
    parser_del = subparsers.add_parser("delete", help="Delete a task")
    parser_del.add_argument("id", type=int, help="Task ID to remove")
    parser_del.set_defaults(func=cmd_delete)

    # Search command
    parser_search = subparsers.add_parser("search", help="Search tasks by keyword")
    parser_search.add_argument("keyword", help="Search keyword for title or category")
    parser_search.set_defaults(func=cmd_search)

    return parser


def main():
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
