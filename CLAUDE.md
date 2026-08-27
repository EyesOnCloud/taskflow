# TaskFlow -- Repository Guidance for Claude

TaskFlow is a small, single-service team task tracker. Stdlib-only
Python: `http.server` for the API, `sqlite3` for storage, no ORM, no
message broker, no Docker required.

## Build & test

- Run the app: `python3 app/main.py`
- Run the tests: `pytest -q`
- No install step is required for the app itself. `pytest` is the only
  external tool this project needs.

## Non-negotiable rules

- **Every migration in `migrations/` must have a working `downgrade()`.**
  A migration that only implements `upgrade()` is not done. Verify by
  actually calling `migrate_down()` in a test, not by reading the code.
- **Never log `assignee_email` or `description` (or any field derived
  from them) in `app/task_service.py` or anywhere else.** These are
  personal data and do not belong in logs.
- **Any outbound HTTP call (see `app/notify.py`) must set an explicit
  timeout.** No exceptions.
- **Any endpoint that can trigger more than one outbound call per
  request (see `/tasks/bulk-notify`) must be rate-limited or capped.**

## Structure

- `app/main.py` -- HTTP routing and request handling
- `app/task_service.py` -- task CRUD logic
- `app/notify.py` -- outbound webhook client
- `app/priority.py` -- priority scoring
- `migrations/` -- schema migrations (custom runner, not Alembic --
  this project has no external dependencies)
- `tests/` -- pytest suite, runnable standalone with no other services

## Scope

Prefer the smallest patch that fixes the stated defect and its test.
Do not refactor unrelated code in the same change.
