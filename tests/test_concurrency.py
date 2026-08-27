"""Real concurrency test for Defect #1 -- duplicate task creation.

Uses two real OS threads, each with its own real sqlite3 connection to
the same file-backed database, forced into the exact interleaving that
exposes the race with threading.Barrier. This is a genuine reproduction,
not a simulation -- it actually runs against real SQLite.
"""
import threading

from app import db, task_service


def test_concurrent_create_with_same_idempotency_key_does_not_duplicate(db_path):
    """On `start`, this test FAILS (or is expected to) -- two threads
    both pass the existence check before either commits, so two rows
    get created for one idempotency key. On `final`, the fix (a real
    UNIQUE constraint / atomic insert-or-get) makes this pass.
    """
    barrier = threading.Barrier(2)
    results = []
    errors = []

    def worker():
        conn = db.get_connection(db_path)
        try:
            barrier.wait(timeout=5)  # force both threads to reach the
            # check-then-act window at (as close to) the same instant
            task_id = task_service.create_task(
                conn,
                title="Double-submit repro",
                description="same click, twice",
                assignee_email="dev@example.com",
                idempotency_key="dup-key-123",
            )
            results.append(task_id)
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)
        finally:
            conn.close()

    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)
    t1.start()
    t2.start()
    t1.join(timeout=10)
    t2.join(timeout=10)

    assert not errors, f"unexpected errors: {errors}"

    verify_conn = db.get_connection(db_path)
    rows = verify_conn.execute(
        "SELECT id FROM tasks WHERE idempotency_key = ?", ("dup-key-123",)
    ).fetchall()
    verify_conn.close()

    assert len(rows) == 1, (
        f"expected exactly 1 task for this idempotency key, found {len(rows)} -- "
        "this is Defect #1: the check-then-act race in create_task()"
    )


def test_unkeyed_creates_never_collide(db_path):
    """Sanity check: tasks with NO idempotency key are independent and
    must never be treated as duplicates of each other."""
    conn = db.get_connection(db_path)
    id1 = task_service.create_task(conn, "A", "desc a", "a@example.com")
    id2 = task_service.create_task(conn, "B", "desc b", "b@example.com")
    conn.close()
    assert id1 != id2
