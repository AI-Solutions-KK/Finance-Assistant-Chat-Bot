# Path: backend/session_store.py
# Purpose: SQLite-based session & chat history storage

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "storage" / "chat_sessions.db"


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        role TEXT,
        content TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def create_session_if_not_exists(session_id: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT OR IGNORE INTO sessions (session_id, created_at)
    VALUES (?, ?)
    """, (session_id, datetime.utcnow().isoformat()))

    conn.commit()
    conn.close()


def save_message(session_id: str, role: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO messages (session_id, role, content, created_at)
    VALUES (?, ?, ?, ?)
    """, (session_id, role, content, datetime.utcnow().isoformat()))

    conn.commit()
    conn.close()


def get_recent_messages(session_id: str, limit: int = 6):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    SELECT role, content
    FROM messages
    WHERE session_id = ?
    ORDER BY id DESC
    LIMIT ?
    """, (session_id, limit))

    rows = cur.fetchall()
    conn.close()

    return list(reversed(rows))
