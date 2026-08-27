"""Core task operations: create, read, update, bulk-notify.

Defect #1 (race condition) and Defect #6 (PII in logs) are fixed here.
See docs/ANSWER_KEY.md for what changed and why.
"""
import logging
import sqlite3

logger = logging.getLogger("taskflow.tasks")


def create_task(conn, title, description, assignee_email, idempotency_key=None):
    """Create a task.

    FIXED (Defect #1): the existence check below is kept as a fast
    path (avoids a round trip to the database for the common case of
    "not a retry"), but it is no longer trusted alone. The real
    protection is the UNIQUE index on idempotency_key added by
    migrations/0003 -- if two threads both pass the fast-path check,
    only one INSERT can succeed; the other raises sqlite3.IntegrityError,
    which is caught here and resolved onto the winner's row instead of
    propagating or silently creating a duplicate.

    FIXED (Defect #6): the log line only records the task id and
    title -- never assignee_email or description, which are personal
    data and do not belong in a log stream.
    """
    if idempotency_key:
        existing = conn.execute(
            "SELECT id FROM tasks WHERE idempotency_key = ?", (idempotency_key,)
        ).fetchone()
        if existing:
            return existing["id"]

    try:
        cur = conn.execute(
            """
            INSERT INTO tasks (title, description, assignee_email, status, idempotency_key)
            VALUES (?, ?, ?, 'open', ?)
            """,
            (title, description, assignee_email, idempotency_key),
        )
        conn.commit()
        task_id = cur.lastrowid
    except sqlite3.IntegrityError:
        # Another thread won the race on this idempotency_key between
        # our fast-path check and our INSERT. Resolve onto its row
        # instead of raising or creating a duplicate.
        conn.rollback()
        winner = conn.execute(
            "SELECT id FROM tasks WHERE idempotency_key = ?", (idempotency_key,)
        ).fetchone()
        if winner is None:
            raise  # genuinely unexpected -- not the race we planned for
        return winner["id"]

    logger.info("task created id=%s title=%r", task_id, title)
    return task_id


def get_task(conn, task_id):
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return dict(row) if row else None


def list_tasks(conn, status=None):
    if status:
        rows = conn.execute("SELECT * FROM tasks WHERE status = ?", (status,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM tasks").fetchall()
    return [dict(r) for r in rows]


def update_task(conn, task_id, status=None, priority=None):
    if status is not None:
        conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    if priority is not None:
        conn.execute("UPDATE tasks SET priority_score = ? WHERE id = ?", (priority, task_id))
    conn.commit()
    return get_task(conn, task_id)


def done_tasks(conn):
    rows = conn.execute("SELECT * FROM tasks WHERE status = 'done'").fetchall()
    return [dict(r) for r in rows]
