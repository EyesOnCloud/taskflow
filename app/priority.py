"""Priority scoring for tasks.

DEFECT #5 (seeded, unfixed on the `start` branch): the threshold below
(`days_overdue >= 3`) was copied from a spreadsheet during the original
build. Nobody currently on the team knows why 3 was chosen instead of
2 or 5, and there is no test pinning this behavior -- so a future
"cleanup" refactor could silently change it and nobody would notice.

This is intentionally left as-is on `start`. The fix on `final` does
NOT invent a justification for the number (that would be dishonest) --
it adds characterization tests that pin the CURRENT behavior exactly,
so any future change to it is a deliberate, visible decision instead
of an accident.
"""


def calculate_priority(days_overdue, status):
    """Return 'high' or 'normal' for a task.

    Completed tasks are never high priority regardless of how overdue
    they were before completion.
    """
    if status == "done":
        return "normal"
    if days_overdue >= 3:
        return "high"
    return "normal"
