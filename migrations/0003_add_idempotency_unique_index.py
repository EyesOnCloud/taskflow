"""Fix for Defect #1: back the idempotency_key check with a real
database-level constraint, not just application logic.

SQLite doesn't support adding a UNIQUE constraint via ALTER TABLE, but
it does support creating a unique index after the fact -- and standard
SQL treats every NULL as distinct, so tasks created without an
idempotency_key are never treated as colliding with each other.
"""

VERSION = "0003_add_idempotency_unique_index"


def upgrade(conn):
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_tasks_idempotency_key "
        "ON tasks (idempotency_key)"
    )
    conn.commit()


def downgrade(conn):
    conn.execute("DROP INDEX IF EXISTS ux_tasks_idempotency_key")
    conn.commit()
