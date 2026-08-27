"""Outbound webhook notification for task events.

Seeds DEFECT #2, #3, and #7 (see docs/ANSWER_KEY.md for the full list).
"""
import json
import logging
import urllib.request
import urllib.error

logger = logging.getLogger("taskflow.notify")


def send_webhook(url, payload, timeout=None):
    """POST a JSON payload to an external webhook URL.

    DEFECT #2 (seeded, unfixed on `start`): no timeout is applied to
    the outbound call. `urlopen()` will block forever (or until the
    OS socket layer gives up, which can be minutes) if the remote
    endpoint accepts the connection and then never responds. This is
    exactly the kind of bug that looks fine in every local test
    against a fast mock server and only bites in production against a
    slow or half-dead endpoint.

    DEFECT #7 (seeded, unfixed on `start`): the retry loop below and
    the caller in main.py's bulk-notify handler BOTH may retry on
    failure, with no single documented owner of "whose job is it to
    retry this request." That ambiguity is exactly what Day 2 / Lab 2
    asks participants to resolve in a task contract before touching
    code.
    """
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )

    attempts = 0
    last_error = None
    while attempts < 3:
        attempts += 1
        try:
            # NOTE: no `timeout=` argument here -- this is Defect #2.
            with urllib.request.urlopen(req) as resp:
                return resp.status
        except urllib.error.URLError as exc:
            last_error = exc
            continue
    raise RuntimeError(f"webhook delivery failed after {attempts} attempts: {last_error}")
