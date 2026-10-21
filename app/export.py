import json
import logging
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

MAX_EXPORT_BATCH = 100
REQUEST_TIMEOUT_SECONDS = 5


def export_tasks(tasks, webhook_url):
    """Send completed tasks to an external reporting service.

    Returns the number of tasks exported successfully.
    """
    if len(tasks) > MAX_EXPORT_BATCH:
        raise ValueError(f"Cannot export more than {MAX_EXPORT_BATCH} tasks per call")

    exported = 0
    for task in tasks:
        logger.info("Exporting task %s", task.get("id"))
        payload = json.dumps(task).encode()
        req = urllib.request.Request(
            webhook_url,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS):
                exported += 1
        except (urllib.error.URLError, TimeoutError) as exc:
            logger.warning("Export failed for task %s: %s", task.get("id"), exc)
    return exported
