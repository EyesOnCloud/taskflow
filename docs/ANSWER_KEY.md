# TaskFlow -- Answer Key (Instructor Use)

Seven defects are seeded into the `start` branch. All seven are fixed
on the `final` branch. This file maps each one to its ticket, its
file, and what a correct fix looks like.

| # | Name | Ticket (give this to participants) | File(s) | What a correct fix does |
|---|------|--------------------------------------|---------|--------------------------|
| 1 | Duplicate task creation | "Some tasks get created twice when someone double-clicks Save." | `app/task_service.py` | Add a real UNIQUE constraint/index on `idempotency_key` and handle the resulting `IntegrityError` by returning the existing row, instead of trusting the check-then-act SELECT alone. |
| 2 | No timeout on webhook call | "The bulk-notify endpoint sometimes hangs for minutes." | `app/notify.py` | Add an explicit `timeout=` to `urlopen()`, with bounded retry/backoff and (recommended) a simple circuit breaker. |
| 3 | No backpressure on bulk-notify | "A bulk notify against 5,000 done tasks took down the webhook receiver." | `app/main.py` (`_bulk_notify`) | Cap concurrent/total outbound calls per request (a rate limiter or a hard batch size), and fail fast/return a partial result instead of firing everything unbounded. |
| 4 | Broken migration downgrade | "We can't roll back the priority_score migration in staging." | `migrations/0002_add_priority_score.py` | Implement a real downgrade -- SQLite requires rebuilding the table without the column (`ALTER TABLE ... DROP COLUMN` is not available in the SQLite version this project targets). |
| 5 | Untested priority threshold | "Nobody knows why days_overdue >= 3 means high priority, and there's no test." | `app/priority.py`, `tests/test_priority.py` | Add full characterization test coverage for every branch. Do NOT invent a justification for the number 3 -- pin the current behavior honestly. |
| 6 | PII in logs | "Assignee emails are showing up in our log aggregator." | `app/task_service.py` | Remove `assignee_email` and `description` from the `logger.info(...)` call in `create_task()`. Log only non-personal fields (task id, status). |
| 7 | Ambiguous retry ownership | "We're not sure if the client or the server should retry a failed notify." | `app/notify.py`, `app/main.py` | Resolve explicitly, in a code comment and in the task contract: pick one owner (recommended: `send_webhook()`'s internal retry is authoritative; callers should not also retry the same logical request), and document why in the ticket's task contract before touching code. |

## Do not let participants "fix" all seven in one sitting

This repo is designed so a fresh `start` clone gives a participant all
seven defects at once -- unlike the earlier RxFlow version of this
course, TaskFlow's two-track design (Claude Days 1-5, Codex Days 6-10)
has EACH tool independently close all seven from the same starting
point, rather than staging some defects for later. If you are running
a single-tool workshop instead of the full two-track course, it is
fine to have participants close all seven in one lab sequence.

## Verification note

Every fix above was verified for real: `pytest -q` was run against
both the `start` branch (where `test_concurrent_create_with_same_idempotency_key_does_not_duplicate`
and `test_downgrade_actually_removes_priority_score_column` are
expected to fail, demonstrating the real bugs) and the `final` branch
(where the full suite passes). See the repository's top-level
`VERIFICATION_NOTES.md` for the actual command output.

Unlike the earlier RxFlow reference build in this course, no external
package installation was needed to get this real verification --
TaskFlow has zero runtime dependencies, so the `start`/`final`
comparison here is an actual pytest run, not a simulation.
