# Verification Notes

TaskFlow has zero runtime dependencies (Python stdlib only), so unlike
the earlier RxFlow reference build in this course, everything below
was actually run -- real threads, a real file-backed SQLite database,
and the real `pytest` test runner. Nothing here is a simulation.

## `start` branch

```
$ pytest -q
...
FAILED tests/test_concurrency.py::test_concurrent_create_with_same_idempotency_key_does_not_duplicate
FAILED tests/test_migrations.py::test_downgrade_actually_removes_priority_score_column
2 failed, 4 passed in 0.09s
```

Both failures are the intended, real reproductions of seeded defects:

- `test_concurrent_create_with_same_idempotency_key_does_not_duplicate`
  forces two real OS threads (each with its own sqlite3 connection) to
  the same file-backed database through the exact interleaving that
  exposes Defect #1: `AssertionError: expected exactly 1 task for this
  idempotency key, found 2`.
- `test_downgrade_actually_removes_priority_score_column` calls the
  real `migrate_down()` and confirms Defect #4: the `priority_score`
  column is still present after "downgrading," because the seeded
  `downgrade()` is a no-op.

`tests/test_priority.py` on `start` is a deliberate stub (2 cases, with
TODOs marking the coverage gap) -- this is Defect #5's "no test
coverage" state, not a bug to fail on; both stubbed cases pass because
they happen to match current behavior.

## `final` branch

```
$ pytest -q
...........
11 passed in 0.07s
```

All 11 tests pass, including the two that failed on `start` (now
exercising the real fix, not a relaxed test) and the 5 additional
characterization cases added for Defect #5.

## What was checked, method by method

- `python3 -m py_compile` on every changed file on both branches --
  confirms no syntax errors.
- `pytest -q` actually executed on both branches (not simulated) --
  see the two runs above.
- `git diff --stat start final` confirms exactly which files changed
  between the two branches (see below); no unrelated files were
  touched.

```
$ git diff --stat start final
 app/main.py                                      | 21 +++++--
 app/notify.py                                    | 68 +++++++++++++++-------
 app/task_service.py                              | 45 +++++++++------
 migrations/0002_add_priority_score.py            | 43 +++++++++++---
 migrations/0003_add_idempotency_unique_index.py  | 21 +++++++
 migrations/runner.py                             |  1 +
 tests/test_priority.py                           | 32 ++++++++---
 7 files changed
```

## What this does and doesn't prove

The concurrency fix is verified against real SQLite under real thread
contention in this exact sandbox -- that's a stronger guarantee than
the RxFlow build in this course could get (RxFlow's ORM/async stack
was never installable here, so its concurrency fix could only be
verified with a hand-built asyncio simulation). What is NOT verified
here: behavior under a real production load (thousands of concurrent
clients, real network latency to a real webhook receiver), and the
HTTP layer in `app/main.py` was compiled and read-reviewed but not
exercised with a live running server in this pass -- run `python3
app/main.py` plus a manual `curl`/Postman pass before treating the API
surface itself as fully verified.
