import json
import logging
import urllib.request

logger = logging.getLogger(__name__)

def export_tasks(tasks, webhook_url):
    """Send completed tasks to an external reporting service."""
    for task in tasks:
        logger.info("Exporting task %s", task.get("id"))
        payload = json.dumps(task).encode()
        req = urllib.request.Request(
            webhook_url,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=5)
