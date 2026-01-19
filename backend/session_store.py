# Path: backend/session_store.py
# Purpose:
# - Session memory
# - Loan intent tracking
# - Auto-expiry
# - SQLite schema migration safe

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "storage" / "chat_sessions.db"


def _column_exists(cur, table, column):
    cur.execute(f"PRAGMA table_info({table})")
    return column in [row[1] for row in cur.fetchall()]


# -------------------------------------------------
# DB init + migration
# -------------------------------------------------
def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create base tables
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

    # 🔄 MIGRATIONS
    if not _column_exists(cur, "sessions", "last_active"):
        cur.execute("ALTER TABLE sessions ADD COLUMN last_active TEXT")

    if not _column_exists(cur, "sessions", "last_loan_type"):
        cur.execute("ALTER TABLE sessions ADD COLUMN last_loan_type TEXT")

    conn.commit()
    conn.close()


# -------------------------------------------------
# Session helpers
# -------------------------------------------------
def create_session_if_not_exists(session_id: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()

    cur.execute("""
        INSERT OR IGNORE INTO sessions (session_id, created_at, last_active)
        VALUES (?, ?, ?)
    """, (session_id, now, now))

    cur.execute("""
        UPDATE sessions SET last_active=?
        WHERE session_id=?
    """, (now, session_id))

    conn.commit()
    conn.close()


def delete_expired_sessions(older_than_minutes: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cutoff = (datetime.utcnow() - timedelta(minutes=older_than_minutes)).isoformat()

    cur.execute("""
        DELETE FROM messages
        WHERE session_id IN (
            SELECT session_id FROM sessions
            WHERE last_active < ?
        )
    """, (cutoff,))

    cur.execute("""
        DELETE FROM sessions WHERE last_active < ?
    """, (cutoff,))

    conn.commit()
    conn.close()


# -------------------------------------------------
# Messages
# -------------------------------------------------
def save_message(session_id: str, role: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()

    cur.execute("""
        INSERT INTO messages (session_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
    """, (session_id, role, content, now))

    cur.execute("""
        UPDATE sessions SET last_active=?
        WHERE session_id=?
    """, (now, session_id))

    conn.commit()
    conn.close()


def get_recent_messages(session_id: str, limit: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT role, content FROM messages
        WHERE session_id=?
        ORDER BY id DESC
        LIMIT ?
    """, (session_id, limit))

    rows = cur.fetchall()
    conn.close()
    return list(reversed(rows))


# -------------------------------------------------
# Loan intent
# -------------------------------------------------
def set_last_loan_type(session_id: str, loan_type: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        UPDATE sessions SET last_loan_type=?
        WHERE session_id=?
    """, (loan_type, session_id))

    conn.commit()
    conn.close()


def get_last_loan_type(session_id: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT last_loan_type FROM sessions
        WHERE session_id=?
    """, (session_id,))

    row = cur.fetchone()
    conn.close()
    return row[0] if row and row[0] else None
