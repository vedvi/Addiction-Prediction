import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'screentime.db')


def _get_connection():
    """Return a connection to the SQLite database (creates tables on first call)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    _init_tables(conn)
    return conn


def _init_tables(conn):
    """Create tables if they don't already exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS analyses (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            daily_hours     REAL    NOT NULL,
            apps_json       TEXT    NOT NULL,
            summary         TEXT,
            insights        TEXT,
            is_addicted     TEXT,
            analyzed_at     TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    conn.commit()


# ── User helpers ──────────────────────────────────────────────────────────────

def get_or_create_user(name: str) -> int:
    """Return the user id for *name*, creating a new row if necessary."""
    conn = _get_connection()
    row = conn.execute(
        "SELECT id FROM users WHERE LOWER(name) = LOWER(?)", (name.strip(),)
    ).fetchone()
    if row:
        user_id = row["id"]
    else:
        cur = conn.execute(
            "INSERT INTO users (name) VALUES (?)", (name.strip(),)
        )
        conn.commit()
        user_id = cur.lastrowid
    conn.close()
    return user_id


def get_all_users():
    """Return a list of all user names (for suggestions / autocomplete)."""
    conn = _get_connection()
    rows = conn.execute("SELECT DISTINCT name FROM users ORDER BY name").fetchall()
    conn.close()
    return [r["name"] for r in rows]


# ── Analysis helpers ──────────────────────────────────────────────────────────

def save_analysis(user_id: int, daily_hours: float, apps: list,
                  summary: str, insights: str, is_addicted: str):
    """Persist one analysis run."""
    conn = _get_connection()
    conn.execute(
        """INSERT INTO analyses
           (user_id, daily_hours, apps_json, summary, insights, is_addicted)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, daily_hours, json.dumps(apps), summary, insights, is_addicted),
    )
    conn.commit()
    conn.close()


def get_user_history(user_id: int, limit: int = 10):
    """Return the last *limit* analyses for a user, newest first."""
    conn = _get_connection()
    rows = conn.execute(
        """SELECT daily_hours, apps_json, summary, insights,
                  is_addicted, analyzed_at
           FROM analyses
           WHERE user_id = ?
           ORDER BY analyzed_at DESC
           LIMIT ?""",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
