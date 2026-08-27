"""Create the tasks table."""

VERSION = "0001_initial"


def upgrade(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            assignee_email TEXT,
            status TEXT NOT NULL DEFAULT 'open',
            idempotency_key TEXT,
            days_overdue INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()


def downgrade(conn):
    conn.execute("DROP TABLE IF EXISTS tasks")
    conn.commit()
