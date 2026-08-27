"""SQLite connection helpers. No ORM, no external dependencies."""
import sqlite3
import os

DB_PATH = os.environ.get("TASKFLOW_DB", os.path.join(os.path.dirname(__file__), "..", "taskflow.db"))


def get_connection(db_path=None):
    """Return a new connection to the TaskFlow database.

    Each caller gets its own connection (this is what makes the
    concurrency test in tests/test_concurrency.py realistic: two
    threads, two real connections, one real file-backed database).
    """
    path = db_path or DB_PATH
    conn = sqlite3.connect(path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn):
    """Bootstrap the schema_migrations tracking table only.

    Actual table creation lives in migrations/ so the migration
    history is the single source of truth for schema shape.
    """
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()
