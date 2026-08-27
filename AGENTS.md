# TaskFlow -- Repository Guidance for Codex

TaskFlow is a small, single-service team task tracker. Stdlib-only
Python: `http.server` for the API, `sqlite3` for storage, no ORM, no
message broker, no Docker required.

## Build & test

- Run the app: `python3 app/main.py`
- Run the tests: `pytest -q`
- No install step is required for the app itself. `pytest` is the only
  external tool this project needs.

## Enforced rules

- Every migration in `migrations/` must have a working `downgrade()`.
  Verify with a test that actually calls it -- do not take a
  reviewer's word for it.
- Never log `assignee_email` or `description` (or anything derived
  from them) anywhere in the codebase.
- Every outbound HTTP call must set an explicit timeout.
- Any endpoint that can trigger more than one outbound call per
  request must be rate-limited or capped.

## Structure

- `app/main.py` -- HTTP routing and request handling
- `app/task_service.py` -- task CRUD logic
- `app/notify.py` -- outbound webhook client
- `app/priority.py` -- priority scoring
- `migrations/` -- schema migrations (custom runner, no external deps)
- `tests/` -- pytest suite, runnable standalone

## Scope

Prefer the smallest patch that fixes the stated defect and its test.
Do not refactor unrelated code in the same change.
