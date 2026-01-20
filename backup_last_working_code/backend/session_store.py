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

    # Create sessions table with is_active column
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        created_at TEXT,
        is_active INTEGER DEFAULT 1
    )
    """)

    # Create messages table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        role TEXT,
        content TEXT,
        created_at TEXT
    )
    """)

    # Check if is_active column exists, if not add it (for existing databases)
    cur.execute("PRAGMA table_info(sessions)")
    columns = [column[1] for column in cur.fetchall()]
    
    if 'is_active' not in columns:
        print("⚠️ Migrating database: Adding is_active column...")
        cur.execute("ALTER TABLE sessions ADD COLUMN is_active INTEGER DEFAULT 1")
        print("✅ Database migration complete")

    conn.commit()
    conn.close()


def create_session_if_not_exists(session_id: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT OR IGNORE INTO sessions (session_id, created_at, is_active)
    VALUES (?, ?, 1)
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
    """Get recent messages for active session only"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check if session exists and is active
    cur.execute("""
    SELECT is_active FROM sessions WHERE session_id = ?
    """, (session_id,))
    
    result = cur.fetchone()
    if not result or result[0] == 0:
        # Session doesn't exist or is inactive - return empty history
        conn.close()
        return []

    # Get recent messages
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


def clear_session(session_id: str):
    """Clear all messages for a session and mark as inactive"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Delete all messages
    cur.execute("""
    DELETE FROM messages WHERE session_id = ?
    """, (session_id,))

    # Mark session as inactive
    cur.execute("""
    UPDATE sessions SET is_active = 0 WHERE session_id = ?
    """, (session_id,))

    conn.commit()
    conn.close()


def activate_session(session_id: str):
    """Reactivate a session (used when starting fresh)"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    UPDATE sessions SET is_active = 1 WHERE session_id = ?
    """, (session_id,))

    conn.commit()
    conn.close()