# TaskFlow

A small, single-service team task tracker, built with zero external
runtime dependencies (Python standard library only: `http.server`,
`sqlite3`, `urllib`, `threading`). Used as the shared sample
application for the "Claude and Codex for Developers" course.

## Branches

- **`start`** -- the broken skeleton. All seven seeded defects are
  present. This is what Day 1 (Claude track) and Day 6 (Codex track)
  both clone from.
- **`final`** -- all seven defects fixed, with full test coverage.
  This is the reference to grade against, not the only correct fix.

Check out whichever one you need:

```bash
git checkout start   # to work the labs
git checkout final   # to see/grade the reference fix
```

## Running it

```bash
python3 app/main.py        # starts the API on :8000
pytest -q                  # runs the test suite
```

No `pip install` is required for the app itself. Only `pytest` needs
to be installed to run the tests (see `requirements.txt`).

## API

- `POST /tasks` -- create a task (`title`, `description`,
  `assignee_email`, optional `idempotency_key`)
- `GET /tasks/{id}` -- fetch one task
- `GET /tasks?status=` -- list tasks, optionally filtered
- `PATCH /tasks/{id}` -- update `status` and/or recompute priority
  from `days_overdue`
- `POST /tasks/bulk-notify` -- fire the webhook for every `done` task

## Docs

- `docs/CONCEPTS.md` -- plain-language primer on the concepts each
  defect touches (race conditions, idempotency, migrations, timeouts,
  backpressure, characterization tests)
- `docs/ANSWER_KEY.md` -- instructor-facing map of all seven defects
  to their fixes (on `final`, this also documents what changed)
- `CLAUDE.md` / `AGENTS.md` -- durable repository guidance for each
  tool
