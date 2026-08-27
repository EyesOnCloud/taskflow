"""Core task operations: create, read, update, bulk-notify.

Seeds DEFECT #1 (race condition) and DEFECT #6 (PII in logs).
"""
import logging

logger = logging.getLogger("taskflow.tasks")


def create_task(conn, title, description, assignee_email, idempotency_key=None):
    """Create a task.

    DEFECT #1 (seeded, unfixed on `start`): if an idempotency_key is
    given, we check whether a task with that key already exists, and
    only insert if not. That check-then-act sequence is NOT atomic --
    two concurrent requests carrying the same idempotency_key can both
    pass the "does it exist?" check before either has committed an
    insert, and both go on to create a row. There is no UNIQUE
    constraint on idempotency_key backing this up at the database
    level, so nothing stops it.

    DEFECT #6 (seeded, unfixed on `start`): the log line below
    includes the assignee's email address and the full task
    description. Emails are personal data and descriptions can
    contain anything a user typed (including personal data about
    someone else) -- neither belongs in a log stream that is often
    retained far longer, and read by far more people, than anyone
    submitting a task expects.
    """
    if idempotency_key:
        existing = conn.execute(
            "SELECT id FROM tasks WHERE idempotency_key = ?", (idempotency_key,)
        ).fetchone()
        if existing:
            return existing["id"]
        # <-- the race window: another thread can run the SELECT above,
        # also find nothing, and also reach the INSERT below before this
        # thread's INSERT commits.

    cur = conn.execute(
        """
        INSERT INTO tasks (title, description, assignee_email, status, idempotency_key)
        VALUES (?, ?, ?, 'open', ?)
        """,
        (title, description, assignee_email, idempotency_key),
    )
    conn.commit()
    task_id = cur.lastrowid

    logger.info(
        "task created id=%s title=%r assignee_email=%s description=%r",
        task_id, title, assignee_email, description,
    )
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
