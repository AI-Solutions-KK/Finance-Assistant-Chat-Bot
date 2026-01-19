# Path: backend/session_store.py
# Purpose:
# - Store FULL current-session chat only
# - Used ONLY for LLM context understanding
# - NEVER used as knowledge
# - Auto-cleared on TTL / refresh / close

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from config import STORAGE_DIR, SESSION_TTL_MINUTES

DB_PATH = STORAGE_DIR / "chat_sessions.db"


# -------------------------------------------------
# DB init
# -------------------------------------------------
def init_db():
    STORAGE_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            last_active TEXT
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


# -------------------------------------------------
# Session helpers
# -------------------------------------------------
def create_session_if_not_exists(session_id: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    now = datetime.utcnow().isoformat()

    cur.execute("""
        INSERT OR IGNORE INTO sessions (session_id, last_active)
        VALUES (?, ?)
    """, (session_id, now))

    cur.execute("""
        UPDATE sessions SET last_active = ?
        WHERE session_id = ?
    """, (now, session_id))

    conn.commit()
    conn.close()


def delete_expired_sessions(older_than_minutes: int = SESSION_TTL_MINUTES):
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
        DELETE FROM sessions
        WHERE last_active < ?
    """, (cutoff,))

    conn.commit()
    conn.close()


# -------------------------------------------------
# Message storage (TEMP ONLY)
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
        UPDATE sessions SET last_active = ?
        WHERE session_id = ?
    """, (now, session_id))

    conn.commit()
    conn.close()


def get_recent_messages(session_id: str, limit: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT role, content
        FROM messages
        WHERE session_id = ?
        ORDER BY id ASC
        LIMIT ?
    """, (session_id, limit))

    rows = cur.fetchall()
    conn.close()
    return rows
