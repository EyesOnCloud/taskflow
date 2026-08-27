"""Characterization tests for app/priority.py -- Defect #5.

STUB (start branch): only a couple of cases are pinned, with TODOs
marking the coverage gap. This mirrors the state a real team's test
suite is often in -- partial coverage, known gap, not yet prioritized.
The `final` branch fills this in completely (see docs/ANSWER_KEY.md).
"""
from app.priority import calculate_priority


def test_open_task_under_threshold_is_normal():
    assert calculate_priority(days_overdue=2, status="open") == "normal"


def test_open_task_at_threshold_is_high():
    assert calculate_priority(days_overdue=3, status="open") == "high"


# TODO: pin behavior for days_overdue == 0 and negative values
# TODO: pin behavior for status == "done" regardless of days_overdue
# TODO: pin behavior for status == "in_progress"
# TODO: decide/document why 3 is the threshold instead of 2 or 5 -- nobody
#       currently knows; do NOT invent a justification, just pin behavior
