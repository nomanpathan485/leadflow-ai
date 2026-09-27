import sqlite3
from contextlib import closing
from pathlib import Path

# Keep the database beside this Python file.
DB_PATH = Path(__file__).resolve().parent / "leads.db"


def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                course TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'New',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def save_lead(name, email, course, message):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.execute(
            """
            INSERT INTO leads (name, email, course, message)
            VALUES (?, ?, ?, ?)
            """,
            (name, email, course, message),
        )
        conn.commit()
        return cursor.lastrowid


def get_leads():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row

        rows = conn.execute(
            "SELECT * FROM leads ORDER BY id DESC"
        ).fetchall()

        return [dict(row) for row in rows]

def update_lead_status(lead_id: int, status: str):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.execute(
            "UPDATE leads SET status = ? WHERE id = ?",
            (status, lead_id),
        )
        conn.commit()

        return cursor.rowcount > 0