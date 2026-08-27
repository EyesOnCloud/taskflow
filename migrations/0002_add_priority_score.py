"""Add a priority_score column to tasks.

FIXED (Defect #4): downgrade() now actually removes the column. SQLite
cannot drop a column with plain `ALTER TABLE ... DROP COLUMN` on the
SQLite versions this project targets, so downgrade() rebuilds the
table without the column instead: create a new table with the
pre-migration shape, copy the data across, drop the old table, and
rename the new one into place. This is the standard SQLite pattern for
"remove a column."
"""

VERSION = "0002_add_priority_score"


def upgrade(conn):
    conn.execute("ALTER TABLE tasks ADD COLUMN priority_score TEXT")
    conn.commit()


def downgrade(conn):
    conn.execute("PRAGMA foreign_keys=off")
    conn.execute(
        """
        CREATE TABLE tasks_pre_0002 (
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
    conn.execute(
        """
        INSERT INTO tasks_pre_0002
            (id, title, description, assignee_email, status, idempotency_key,
             days_overdue, created_at)
        SELECT id, title, description, assignee_email, status, idempotency_key,
               days_overdue, created_at
        FROM tasks
        """
    )
    conn.execute("DROP TABLE tasks")
    conn.execute("ALTER TABLE tasks_pre_0002 RENAME TO tasks")
    conn.execute("PRAGMA foreign_keys=on")
    conn.commit()
