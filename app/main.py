"""TaskFlow HTTP API -- stdlib only (http.server), no framework.

Endpoints:
  POST   /tasks              create a task
  GET    /tasks/{id}         fetch one task
  GET    /tasks?status=      list tasks, optionally filtered
  PATCH  /tasks/{id}         update status / priority
  POST   /tasks/bulk-notify  fire the webhook for every 'done' task
"""
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, __file__.rsplit("/app/", 1)[0]) if "/app/" in __file__ else None

from app import db, task_service, notify, priority  # noqa: E402

TASK_ID_RE = re.compile(r"^/tasks/(\d+)$")
NOTIFY_WEBHOOK_URL = "http://localhost:9/webhook"  # placeholder target for the lab


class TaskFlowHandler(BaseHTTPRequestHandler):
    server_version = "TaskFlow/0.1"

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def do_POST(self):
        parsed = urlparse(self.path)
        conn = db.get_connection()
        try:
            if parsed.path == "/tasks":
                body = self._read_json_body()
                task_id = task_service.create_task(
                    conn,
                    title=body.get("title"),
                    description=body.get("description"),
                    assignee_email=body.get("assignee_email"),
                    idempotency_key=body.get("idempotency_key"),
                )
                self._send_json(201, task_service.get_task(conn, task_id))
            elif parsed.path == "/tasks/bulk-notify":
                self._bulk_notify(conn)
            else:
                self._send_json(404, {"error": "not found"})
        finally:
            conn.close()

    # FIXED (Defect #3): a hard per-request cap on how many outbound
    # webhook calls one bulk-notify request can trigger. If the
    # backlog is larger than this, we notify what we safely can and
    # tell the caller explicitly how much was left over, rather than
    # silently firing an unbounded burst at the downstream receiver.
    MAX_NOTIFIES_PER_REQUEST = 50

    def _bulk_notify(self, conn):
        tasks = task_service.done_tasks(conn)
        to_send = tasks[: self.MAX_NOTIFIES_PER_REQUEST]
        skipped = len(tasks) - len(to_send)

        results = []
        for t in to_send:
            try:
                status = notify.send_webhook(NOTIFY_WEBHOOK_URL, {"task_id": t["id"], "status": t["status"]})
                results.append({"task_id": t["id"], "ok": True, "status": status})
            except Exception as exc:  # noqa: BLE001
                results.append({"task_id": t["id"], "ok": False, "error": str(exc)})

        self._send_json(
            200,
            {
                "notified": len(results),
                "results": results,
                "skipped_due_to_rate_limit": skipped,
            },
        )

    def do_GET(self):
        parsed = urlparse(self.path)
        conn = db.get_connection()
        try:
            match = TASK_ID_RE.match(parsed.path)
            if match:
                task = task_service.get_task(conn, int(match.group(1)))
                if task is None:
                    self._send_json(404, {"error": "not found"})
                else:
                    self._send_json(200, task)
            elif parsed.path == "/tasks":
                qs = parse_qs(parsed.query)
                status = qs.get("status", [None])[0]
                self._send_json(200, task_service.list_tasks(conn, status=status))
            else:
                self._send_json(404, {"error": "not found"})
        finally:
            conn.close()

    def do_PATCH(self):
        parsed = urlparse(self.path)
        match = TASK_ID_RE.match(parsed.path)
        if not match:
            self._send_json(404, {"error": "not found"})
            return
        body = self._read_json_body()
        conn = db.get_connection()
        try:
            task_id = int(match.group(1))
            new_priority = None
            if "days_overdue" in body:
                current = task_service.get_task(conn, task_id)
                status_for_calc = body.get("status", current["status"] if current else "open")
                new_priority = priority.calculate_priority(body["days_overdue"], status_for_calc)
            updated = task_service.update_task(
                conn, task_id, status=body.get("status"), priority=new_priority
            )
            if updated is None:
                self._send_json(404, {"error": "not found"})
            else:
                self._send_json(200, updated)
        finally:
            conn.close()

    def log_message(self, fmt, *args):
        pass  # keep test/demo output quiet


def run(port=8000):
    from migrations import runner
    conn = db.get_connection()
    runner.migrate_up(conn)
    conn.close()
    server = HTTPServer(("0.0.0.0", port), TaskFlowHandler)
    print(f"TaskFlow listening on :{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
