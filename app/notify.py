"""Outbound webhook notification for task events.

Defects #2, #3, and #7 are fixed here and in app/main.py. See
docs/ANSWER_KEY.md for the full mapping.
"""
import json
import logging
import time
import urllib.request
import urllib.error

logger = logging.getLogger("taskflow.notify")

DEFAULT_TIMEOUT = 5.0  # seconds, connect+read combined (urlopen's single knob)
MAX_ATTEMPTS = 3
BACKOFF_BASE = 0.2  # seconds

# --- Fix for Defect #7 (ambiguous retry ownership) ---------------------
# Decision, made explicit here instead of left implicit: send_webhook()
# is the SOLE owner of retrying a webhook delivery. Callers (see
# app/main.py's bulk-notify handler) must NOT layer their own retry
# loop on top of this function -- doing so would let one failed
# delivery multiply into MAX_ATTEMPTS^2 real outbound calls. If a
# caller needs to know whether delivery ultimately failed, it should
# catch the exception this function raises and record/report the
# failure -- not retry it again itself.
# -------------------------------------------------------------------

# --- Fix for Defect #2 (no timeout) + a simple circuit breaker ---------
_consecutive_failures = 0
_circuit_open_until = 0.0
_FAILURE_THRESHOLD = 5
_COOLDOWN_SECONDS = 30.0


class CircuitOpenError(RuntimeError):
    """Raised when the circuit breaker is open and a call is skipped."""


def send_webhook(url, payload, timeout=DEFAULT_TIMEOUT):
    """POST a JSON payload to an external webhook URL.

    Applies an explicit timeout (Defect #2), bounded retries with
    backoff, and a circuit breaker that stops sending requests for a
    cooldown period after repeated consecutive failures -- protecting
    a struggling downstream receiver from being hit with retries while
    it is already failing.
    """
    global _consecutive_failures, _circuit_open_until

    now = time.monotonic()
    if now < _circuit_open_until:
        raise CircuitOpenError(
            f"circuit open for {_circuit_open_until - now:.1f}s more "
            "after repeated webhook failures"
        )

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )

    attempts = 0
    last_error = None
    while attempts < MAX_ATTEMPTS:
        attempts += 1
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                _consecutive_failures = 0
                return resp.status
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempts < MAX_ATTEMPTS:
                time.sleep(BACKOFF_BASE * (2 ** (attempts - 1)))
            continue

    _consecutive_failures += 1
    if _consecutive_failures >= _FAILURE_THRESHOLD:
        _circuit_open_until = time.monotonic() + _COOLDOWN_SECONDS
        logger.warning(
            "circuit breaker opened after %s consecutive webhook failures",
            _consecutive_failures,
        )

    raise RuntimeError(f"webhook delivery failed after {attempts} attempts: {last_error}")
