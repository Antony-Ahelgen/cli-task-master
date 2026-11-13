# 📋 CLI Task Master

A fast, lightweight, and robust SQLite-backed terminal task manager built with Python. Manage your daily to-dos, prioritize assignments, categorize workflows, and search tasks directly from your command line.

---

## ✨ Features

- **⚡ Fast & Lightweight**: Zero required heavy external dependencies; powered by standard library `sqlite3` and `argparse`.
- **💾 Local SQLite Storage**: Keeps your tasks safely stored locally in `~/.tasks.db` (customizable via `--db` or `TASKS_DB_PATH`).
- **🎯 Task Prioritization**: Assign `high`, `med`, or `low` priority levels to keep your focus sharp.
- **🏷️ Categories & Tags**: Organize tasks by category (`Work`, `Personal`, `Dev`, `Bugs`, etc.).
- **🔍 Quick Search**: Instantly filter and search tasks by keyword across task titles and categories.
- **📊 Clean Table Output**: Automatically renders formatted ASCII/Unicode tables using `tabulate` (with graceful fallback to built-in formatting).

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Antony-Ahelgen/cli-task-master.git
cd cli-task-master
```

### 2. (Optional) Set Up a Virtual Environment

```bash
python -m venv venv
# On Linux/macOS:
source venv/bin/activate
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

*(Note: If `tabulate` is not installed, the tool gracefully falls back to built-in table formatting.)*

---

## 🛠️ Usage & Commands

```bash
python main.py [COMMAND] [OPTIONS]
```

### 1. Adding Tasks (`add`)

Add tasks with optional priority (`-p` / `--priority`: `high`, `med`, `low`) and category (`-c` / `--category`):

```bash
# Basic task (defaults to 'med' priority and 'General' category)
python main.py add "Draft monthly project report"

# High priority task with category
python main.py add "Fix database connection timeout bug" -p high -c Backend

# Low priority personal task
python main.py add "Buy groceries" -p low -c Personal
```

### 2. Listing Tasks (`list`)

List all tasks or filter by status (`pending`, `completed`, `all`), priority, or category:

```bash
# List all tasks
python main.py list

# List pending tasks only
python main.py list -s pending

# List completed tasks
python main.py list -s completed

# Filter by category
python main.py list -c Backend

# Filter by priority
python main.py list -p high
```

### 3. Marking Tasks Complete (`done`)

Mark a task as done using its ID:

```bash
python main.py done 1
```

### 4. Searching Tasks (`search`)

Perform a keyword search matching task titles and categories:

```bash
python main.py search "database"
```

### 5. Deleting Tasks (`delete`)

Remove a task permanently:

```bash
python main.py delete 1
```

---

## ⚙️ Configuration & Options

| Option / Flag | Description |
| :--- | :--- |
| `--db <path>` | Specify a custom SQLite database file path. |
| `TASKS_DB_PATH` | Environment variable to override default storage location (`~/.tasks.db`). |
| `-h`, `--help` | Display command help and usage syntax. |

---

## 🏗️ Architecture & Database Schema

CLI Task Master utilizes SQLite with the following schema:

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    priority TEXT NOT NULL CHECK(priority IN ('high', 'med', 'low')) DEFAULT 'med',
    category TEXT NOT NULL DEFAULT 'General',
    status TEXT NOT NULL CHECK(status IN ('pending', 'completed')) DEFAULT 'pending',
    created_at TEXT NOT NULL,
    completed_at TEXT
);
```

---

## 🧪 Testing

Run standard execution checks:

```bash
python -m py_compile main.py
python main.py --help
```

---

## 📄 License

MIT License. Feel free to use and modify for personal and commercial projects.
