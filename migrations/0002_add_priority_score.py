"""Add a priority_score column to tasks.

DEFECT #4 (seeded, unfixed on `start`): downgrade() below is a no-op.
SQLite cannot drop a column with plain `ALTER TABLE ... DROP COLUMN`
in older versions, and whoever wrote this migration took the shortcut
of leaving downgrade() empty rather than doing the rebuild-the-table
dance SQLite actually requires. The result: you can migrate this
database forward, but you can never safely migrate it back -- exactly
the trap docs/CLAUDE.md's (or AGENTS.md's) migration rule exists to
catch.
"""

VERSION = "0002_add_priority_score"


def upgrade(conn):
    conn.execute("ALTER TABLE tasks ADD COLUMN priority_score TEXT")
    conn.commit()


def downgrade(conn):
    # BROKEN ON PURPOSE (Defect #4): this does nothing. A correct
    # downgrade needs to rebuild the tasks table without the column,
    # since SQLite's ALTER TABLE cannot drop a column directly.
    pass
