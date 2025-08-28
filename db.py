import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

DB_PATH = "family_bot.db"


def init_db():
    """Initialize the database with tables and indexes."""
    logger.info("Initializing database")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        
        # Users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Asks table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS asks (
                id INTEGER PRIMARY KEY,
                chat_id INTEGER NOT NULL,
                requester_id INTEGER NOT NULL,
                requester_name TEXT NOT NULL,
                text TEXT NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('open','closed')),
                created_at TEXT NOT NULL,
                closed_at TEXT
            )
        """)
        
        # Ask assignees table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ask_assignees (
                id INTEGER PRIMARY KEY,
                ask_id INTEGER NOT NULL,
                assignee_id INTEGER NOT NULL,
                assignee_name TEXT NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('open','done')),
                done_at TEXT,
                FOREIGN KEY(ask_id) REFERENCES asks(id) ON DELETE CASCADE
            )
        """)
        
        # Indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_asks_chat_status ON asks(chat_id, status);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_assign_assignee_status ON ask_assignees(assignee_id, status);")
        
        conn.commit()


def register_user(user_id: int, display_name: str) -> None:
    """Register or update a user in the database."""
    now = datetime.utcnow().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT OR REPLACE INTO users (user_id, display_name, created_at)
            VALUES (?, ?, COALESCE((SELECT created_at FROM users WHERE user_id = ?), ?))
        """, (user_id, display_name, user_id, now))
        conn.commit()


def get_roster() -> List[Tuple[int, str]]:
    """Get all registered users ordered by display name."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT user_id, display_name 
            FROM users 
            ORDER BY display_name
        """)
        return cursor.fetchall()


def create_ask(chat_id: int, requester_id: int, requester_name: str, text: str, 
               assignees: List[Tuple[int, str]]) -> int:
    """Create a new ask with assignees. Returns ask_id."""
    now = datetime.utcnow().isoformat()
    
    with sqlite3.connect(DB_PATH) as conn:
        # Create the ask
        cursor = conn.execute("""
            INSERT INTO asks (chat_id, requester_id, requester_name, text, status, created_at)
            VALUES (?, ?, ?, ?, 'open', ?)
        """, (chat_id, requester_id, requester_name, text, now))
        
        ask_id = cursor.lastrowid
        
        # Create assignees
        for user_id, display_name in assignees:
            conn.execute("""
                INSERT INTO ask_assignees (ask_id, assignee_id, assignee_name, status)
                VALUES (?, ?, ?, 'open')
            """, (ask_id, user_id, display_name))
        
        conn.commit()
        logger.info(f"Created ask {ask_id} with {len(assignees)} assignees")
        return ask_id


def list_my_open_assignments(user_id: int) -> List[Dict]:
    """List all open assignments for a user."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT aa.id as assignment_id, a.id as ask_id, a.text, a.requester_name
            FROM ask_assignees aa 
            JOIN asks a ON a.id = aa.ask_id
            WHERE aa.assignee_id = ? AND aa.status = 'open' AND a.status = 'open'
            ORDER BY a.created_at DESC
        """, (user_id,))
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def mark_assignment_done(assignment_id: int, assignee_id: int, when_utc: str) -> Tuple[int, int, str, str]:
    """Mark an assignment as done. Returns (ask_id, requester_id, requester_name, text) for notification."""
    with sqlite3.connect(DB_PATH) as conn:
        # Mark assignment done
        conn.execute("""
            UPDATE ask_assignees 
            SET status = 'done', done_at = ?
            WHERE id = ? AND assignee_id = ?
        """, (when_utc, assignment_id, assignee_id))
        
        # Get ask info for notification
        cursor = conn.execute("""
            SELECT a.id, a.requester_id, a.requester_name, a.text
            FROM asks a 
            JOIN ask_assignees aa ON a.id = aa.ask_id
            WHERE aa.id = ?
        """, (assignment_id,))
        
        result = cursor.fetchone()
        if not result:
            raise ValueError(f"Assignment {assignment_id} not found")
        
        conn.commit()
        logger.info(f"Marked assignment {assignment_id} as done")
        return result


def maybe_close_ask(ask_id: int, when_utc: str) -> bool:
    """Close ask if all assignments are done. Returns True if closed."""
    with sqlite3.connect(DB_PATH) as conn:
        # Check if any assignments are still open
        cursor = conn.execute("""
            SELECT COUNT(*) FROM ask_assignees 
            WHERE ask_id = ? AND status = 'open'
        """, (ask_id,))
        
        open_count = cursor.fetchone()[0]
        
        if open_count == 0:
            # All done, close the ask
            conn.execute("""
                UPDATE asks 
                SET status = 'closed', closed_at = ?
                WHERE id = ?
            """, (when_utc, ask_id))
            conn.commit()
            logger.info(f"Closed ask {ask_id} - all assignments complete")
            return True
        
        return False


def get_all_open_asks(chat_id: int) -> List[Dict]:
    """Get all open asks with assignee statuses for a chat."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT a.id as ask_id, a.text, a.requester_name,
                   aa.assignee_name, aa.status
            FROM asks a
            JOIN ask_assignees aa ON a.id = aa.ask_id
            WHERE a.chat_id = ? AND a.status = 'open'
            ORDER BY a.created_at DESC, a.id, aa.id
        """, (chat_id,))
        
        # Group by ask_id in Python
        by_id = {}
        for ask_id, text, requester_name, assignee_name, status in cursor.fetchall():
            if ask_id not in by_id:
                by_id[ask_id] = {
                    "ask_id": ask_id,
                    "text": text,
                    "requester_name": requester_name,
                    "assignees": []
                }
            by_id[ask_id]["assignees"].append((assignee_name, status))
        
        return list(by_id.values())