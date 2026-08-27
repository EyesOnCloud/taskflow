"""A tiny migration runner (stands in for Alembic, which isn't needed
here -- this project has no external dependencies at all).

Migrations are plain Python modules in this directory, each exposing
VERSION, upgrade(conn), and downgrade(conn). Applied versions are
tracked in the schema_migrations table (see app/db.py).
"""
import importlib
import os
import sys

MIGRATIONS_DIR = os.path.dirname(__file__)

# Ordered by filename. Add new migration files here in order.
MIGRATION_MODULES = [
    "0001_initial",
    "0002_add_priority_score",
]


def _load(module_name):
    if MIGRATIONS_DIR not in sys.path:
        sys.path.insert(0, MIGRATIONS_DIR)
    return importlib.import_module(module_name)


def applied_versions(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()
    rows = conn.execute("SELECT version FROM schema_migrations").fetchall()
    return {r["version"] if isinstance(r, dict) else r[0] for r in rows}


def migrate_up(conn):
    """Apply every migration that hasn't been applied yet, in order."""
    done = applied_versions(conn)
    for name in MIGRATION_MODULES:
        mod = _load(name)
        if mod.VERSION in done:
            continue
        mod.upgrade(conn)
        conn.execute("INSERT INTO schema_migrations (version) VALUES (?)", (mod.VERSION,))
        conn.commit()


def migrate_down(conn, target_version=None):
    """Undo migrations back to (but not including) target_version.

    With target_version=None, undoes everything.
    """
    done = applied_versions(conn)
    for name in reversed(MIGRATION_MODULES):
        mod = _load(name)
        if mod.VERSION not in done:
            continue
        if mod.VERSION == target_version:
            break
        mod.downgrade(conn)
        conn.execute("DELETE FROM schema_migrations WHERE version = ?", (mod.VERSION,))
        conn.commit()
