"""Migration up/down tests -- Defect #4."""
from app import db
from migrations import runner


def test_migrate_up_creates_priority_score_column(tmp_path):
    path = str(tmp_path / "mig_test.db")
    conn = db.get_connection(path)
    runner.migrate_up(conn)
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
    conn.close()
    assert "priority_score" in cols


def test_downgrade_actually_removes_priority_score_column(tmp_path):
    """On `start`, this FAILS: migration 0002's downgrade() is a no-op,
    so the column is still present after downgrading. On `final`, the
    downgrade correctly rebuilds the table without the column.
    """
    path = str(tmp_path / "mig_down_test.db")
    conn = db.get_connection(path)
    runner.migrate_up(conn)
    runner.migrate_down(conn, target_version="0001_initial")
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
    conn.close()
    assert "priority_score" not in cols, (
        "Defect #4: downgrade() for 0002_add_priority_score did not remove "
        "the column it added"
    )
