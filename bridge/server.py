"""
bridge/server.py
Local Windows Bridge & Authenticated Task Queue for Antigravity Web Prompt Control Center.

Part of Task 1.63 — Pet Mining Empire Development Architecture.
"""

import os
import sys
import json
import time
import uuid
import hmac
import hashlib
import logging
import argparse
import threading
import subprocess
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

# Base Directory Setup
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
QUEUE_DIR = os.path.join(ROOT_DIR, ".queue")
TASKS_FILE = os.path.join(QUEUE_DIR, "tasks.json")
AUDIT_LOG_FILE = os.path.join(QUEUE_DIR, "audit.log")
STAGED_PROMPT_FILE = os.path.join(QUEUE_DIR, "staged_prompt.md")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "bridge_config.json")
TEMPLATE_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.template.json")

# Ensure queue directory exists
os.makedirs(QUEUE_DIR, exist_ok=True)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(AUDIT_LOG_FILE, encoding="utf-8", mode="a")
    ]
)

# Global thread lock for atomic queue operations
queue_lock = threading.Lock()


def load_config():
    """Loads configuration with defaults and fallback to template."""
    config = {
        "server": {
            "host": "127.0.0.1",
            "port": 8765,
            "cors_origins": ["*"]
        },
        "auth": {
            "auth_key": os.environ.get("BRIDGE_AUTH_KEY", "")
        },
        "bridge": {
            "auto_claim": False,
            "copy_to_clipboard": True,
            "notify_on_claim": True
        },
        "safety": {
            "max_prompt_length": 25000,
            "default_mode": "plan-first",
            "require_approval_for_execute": True
        }
    }

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
                for k in user_cfg:
                    if isinstance(user_cfg[k], dict) and k in config:
                        config[k].update(user_cfg[k])
                    else:
                        config[k] = user_cfg[k]
        except Exception as e:
            logging.warning(f"Failed to load bridge_config.json: {e}")

    # If auth key is still empty, generate a session-specific secure random token
    if not config["auth"]["auth_key"]:
        generated = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:24]
        config["auth"]["auth_key"] = f"agy_{generated}"
        logging.info("=" * 70)
        logging.info(f"Generated Session Auth Key: {config['auth']['auth_key']}")
        logging.info("Use this key in the Web Prompt Control Center interface.")
        logging.info("=" * 70)

    return config


def load_tasks():
    """Reads tasks database from disk."""
    with queue_lock:
        if not os.path.exists(TASKS_FILE):
            return []
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading tasks: {e}")
            return []


def save_tasks(tasks):
    """Atomically writes tasks database to disk."""
    with queue_lock:
        temp_file = TASKS_FILE + ".tmp"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)
            if os.path.exists(TASKS_FILE):
                os.replace(temp_file, TASKS_FILE)
            else:
                os.rename(temp_file, TASKS_FILE)
            return True
        except Exception as e:
            logging.error(f"Error saving tasks: {e}")
            if os.path.exists(temp_file):
                try: os.remove(temp_file)
                except: pass
            return False


def copy_to_windows_clipboard(text):
    """Copies text to the Windows clipboard via native clip.exe with timeout."""
    if sys.platform != "win32":
        return False
    try:
        # Use native Windows clip.exe (fast, zero PowerShell overhead)
        proc = subprocess.Popen(
            ["clip"],
            stdin=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        proc.communicate(input=text, timeout=2.0)
        return proc.returncode == 0
    except Exception as e:
        logging.warning(f"Clipboard copy skipped or timed out: {e}")
        return False


def notify_windows(title, message):
    """Plays Windows system notification or console beep."""
    try:
        if sys.platform == "win32":
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except Exception:
        pass


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Multi-threaded HTTP server for non-blocking concurrent requests."""
    daemon_threads = True


class BridgeRequestHandler(BaseHTTPRequestHandler):
    """Handles REST API requests from the GitHub Pages Control Center."""

    server_version = "AntigravityBridge/1.0"

    def _send_cors_headers(self):
        """Sets CORS headers allowing web interface cross-origin requests."""
        origin = self.headers.get("Origin", "*")
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, X-Requested-With")
        self.send_header("Access-Control-Allow-Credentials", "true")

    def _send_json(self, status_code, data):
        """Sends a JSON response with CORS headers."""
        response_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(response_bytes)

    def _send_error(self, status_code, message):
        """Sends an error response."""
        self._send_json(status_code, {"error": message, "status": "error"})

    def do_OPTIONS(self):
        """Responds to preflight CORS requests."""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def _authenticate(self):
        """Checks Authorization: Bearer <key> against configured auth key."""
        auth_header = self.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return False
        token = auth_header[7:].strip()
        expected = self.server.config["auth"]["auth_key"]
        return hmac.compare_digest(token, expected)

    def _read_json_body(self):
        """Reads and parses incoming JSON request body."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 10 * 1024 * 1024: # 10MB limit
                return None
            body_bytes = self.rfile.read(content_length)
            return json.loads(body_bytes.decode("utf-8"))
        except Exception as e:
            logging.warning(f"Invalid JSON request: {e}")
            return None

    # -------------------------------------------------------------
    # GET Handlers
    # -------------------------------------------------------------
    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/")

        # Health check does not require auth
        if path == "/api/health" or path == "":
            self._send_json(200, {
                "status": "online",
                "service": "Antigravity Web Prompt Bridge",
                "version": "1.0.0",
                "handoff_mode": "secure_queue_manual_clipboard",
                "antigravity_status": "active_desktop_ide",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            return

        # All other endpoints require authentication
        if not self._authenticate():
            self._send_error(401, "Unauthorized: Valid Bearer token required")
            return

        if path == "/api/tasks":
            tasks = load_tasks()
            # Sort newest first
            tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            self._send_json(200, {"tasks": tasks, "count": len(tasks)})
            return

        if path.startswith("/api/tasks/"):
            task_id = path.split("/")[3]
            tasks = load_tasks()
            task = next((t for t in tasks if t.get("id") == task_id), None)
            if task:
                self._send_json(200, {"task": task})
            else:
                self._send_error(404, f"Task {task_id} not found")
            return

        if path == "/api/audit":
            if os.path.exists(AUDIT_LOG_FILE):
                with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
                    lines = f.readlines()[-100:] # Last 100 lines
                self._send_json(200, {"audit_log": lines})
            else:
                self._send_json(200, {"audit_log": []})
            return

        self._send_error(404, "Endpoint not found")

    # -------------------------------------------------------------
    # POST Handlers
    # -------------------------------------------------------------
    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/")

        # Auth verification endpoint
        if path == "/api/auth/verify":
            if self._authenticate():
                self._send_json(200, {"authenticated": True, "message": "Access granted"})
            else:
                self._send_error(401, "Invalid authentication credentials")
            return

        # All mutating actions require authentication
        if not self._authenticate():
            self._send_error(401, "Unauthorized: Valid Bearer token required")
            return

        body = self._read_json_body() or {}

        # 1. Submit Task
        if path == "/api/tasks/submit":
            prompt = body.get("prompt", "").strip()
            if not prompt:
                self._send_error(400, "Field 'prompt' is required and cannot be empty")
                return

            max_len = self.server.config["safety"]["max_prompt_length"]
            if len(prompt) > max_len:
                self._send_error(400, f"Prompt length ({len(prompt)}) exceeds maximum allowed ({max_len})")
                return

            mode = body.get("mode", self.server.config["safety"]["default_mode"])
            if mode not in ["plan-first", "execute"]:
                mode = "plan-first"

            title = body.get("title", "").strip()
            if not title:
                # Derive title from first line of prompt
                first_line = prompt.split("\n")[0].strip("#* -")
                title = (first_line[:60] + "...") if len(first_line) > 60 else first_line
                if not title: title = "Untitled Task"

            now_iso = datetime.now(timezone.utc).isoformat()
            task_seq = int(time.time() * 1000) % 100000
            task_id = f"TASK-{task_seq:05d}"

            require_approval = body.get("require_approval", False)
            if mode == "execute" and self.server.config["safety"]["require_approval_for_execute"]:
                require_approval = True

            new_task = {
                "id": task_id,
                "title": title,
                "prompt": prompt,
                "mode": mode,
                "category": body.get("category", "General"),
                "status": "pending",
                "require_approval": require_approval,
                "approval": {
                    "required": require_approval,
                    "approved": False,
                    "approved_at": None
                },
                "created_at": now_iso,
                "claimed_at": None,
                "completed_at": None,
                "logs": [
                    f"[{now_iso}] Task submitted to queue (Mode: {mode}, Approval Required: {require_approval})"
                ],
                "completion_summary": None,
                "artifacts": {
                    "report_ref": None,
                    "commit_sha": None,
                    "gallery_ref": None,
                    "screenshots": []
                }
            }

            tasks = load_tasks()
            tasks.append(new_task)
            save_tasks(tasks)

            logging.info(f"Task submitted: {task_id} — '{title}' (Mode: {mode})")

            # Check if auto-claim is enabled
            if self.server.config["bridge"]["auto_claim"]:
                self._claim_task(new_task)

            self._send_json(201, {"success": True, "task": new_task})
            return

        # 2. Claim Task (Atomic handoff)
        if path.endswith("/claim"):
            parts = path.split("/")
            if len(parts) >= 4:
                task_id = parts[3]
                tasks = load_tasks()
                task = next((t for t in tasks if t.get("id") == task_id), None)
                if not task:
                    self._send_error(404, f"Task {task_id} not found")
                    return
                if task["status"] not in ["pending", "awaiting_approval"]:
                    self._send_error(409, f"Task {task_id} cannot be claimed (current status: {task['status']})")
                    return

                self._claim_task(task)
                save_tasks(tasks)
                self._send_json(200, {"success": True, "task": task})
                return

        # 3. Approve Task
        if path.endswith("/approve"):
            parts = path.split("/")
            if len(parts) >= 4:
                task_id = parts[3]
                tasks = load_tasks()
                task = next((t for t in tasks if t.get("id") == task_id), None)
                if not task:
                    self._send_error(404, f"Task {task_id} not found")
                    return

                now_iso = datetime.now(timezone.utc).isoformat()
                task["approval"]["approved"] = True
                task["approval"]["approved_at"] = now_iso
                task["logs"].append(f"[{now_iso}] Task execution explicitly approved by user.")
                if task["status"] == "awaiting_approval":
                    task["status"] = "running"
                save_tasks(tasks)

                logging.info(f"Task {task_id} approved for execution.")
                self._send_json(200, {"success": True, "task": task})
                return

        # 4. Update Task Status & Logs
        if path.endswith("/status"):
            parts = path.split("/")
            if len(parts) >= 4:
                task_id = parts[3]
                tasks = load_tasks()
                task = next((t for t in tasks if t.get("id") == task_id), None)
                if not task:
                    self._send_error(404, f"Task {task_id} not found")
                    return

                new_status = body.get("status")
                if new_status and new_status in ["pending", "claimed", "running", "awaiting_approval", "completed", "failed", "cancelled"]:
                    task["status"] = new_status
                    if new_status == "completed":
                        task["completed_at"] = datetime.now(timezone.utc).isoformat()

                if "log" in body:
                    now_iso = datetime.now(timezone.utc).isoformat()
                    task["logs"].append(f"[{now_iso}] {body['log']}")

                if "completion_summary" in body:
                    task["completion_summary"] = body["completion_summary"]

                if "artifacts" in body and isinstance(body["artifacts"], dict):
                    task["artifacts"].update(body["artifacts"])

                save_tasks(tasks)
                self._send_json(200, {"success": True, "task": task})
                return

        # 5. Cancel Task
        if path.endswith("/cancel"):
            parts = path.split("/")
            if len(parts) >= 4:
                task_id = parts[3]
                tasks = load_tasks()
                task = next((t for t in tasks if t.get("id") == task_id), None)
                if not task:
                    self._send_error(404, f"Task {task_id} not found")
                    return

                if task["status"] in ["completed", "cancelled"]:
                    self._send_error(400, f"Task already in terminal state: {task['status']}")
                    return

                now_iso = datetime.now(timezone.utc).isoformat()
                task["status"] = "cancelled"
                task["logs"].append(f"[{now_iso}] Task cancelled by user.")
                save_tasks(tasks)

                logging.info(f"Task {task_id} cancelled.")
                self._send_json(200, {"success": True, "task": task})
                return

        self._send_error(404, "Endpoint not found")

    def _claim_task(self, task):
        """Performs atomic claim and local handoff staging for Antigravity."""
        now_iso = datetime.now(timezone.utc).isoformat()
        task["status"] = "running" if not task["require_approval"] else "awaiting_approval"
        task["claimed_at"] = now_iso

        # 1. Format prompt for staging
        formatted_prompt = (
            f"<!-- ANTIGRAVITY STAGED TASK: {task['id']} -->\n"
            f"# {task['title']}\n\n"
            f"**Task ID:** {task['id']}  \n"
            f"**Mode:** {task['mode']}  \n"
            f"**Submitted:** {task['created_at']}  \n\n"
            f"## Instructions\n\n"
            f"{task['prompt']}\n"
        )

        # 2. Write to local staging file
        try:
            with open(STAGED_PROMPT_FILE, "w", encoding="utf-8") as f:
                f.write(formatted_prompt)
            task["logs"].append(f"[{now_iso}] Prompt staged to {os.path.basename(STAGED_PROMPT_FILE)}")
        except Exception as e:
            logging.warning(f"Failed to write staging file: {e}")

        # 3. Copy to Windows clipboard
        if self.server.config["bridge"]["copy_to_clipboard"]:
            if copy_to_windows_clipboard(task["prompt"]):
                task["logs"].append(f"[{now_iso}] Prompt copied to Windows clipboard ready for Antigravity IDE paste.")
            else:
                task["logs"].append(f"[{now_iso}] Clipboard copy skipped or unavailable.")

        # 4. Trigger notification
        if self.server.config["bridge"]["notify_on_claim"]:
            notify_windows("Antigravity Bridge", f"Task {task['id']} claimed and staged!")

        logging.info(f"Task {task['id']} claimed and staged for Antigravity handoff.")


def run_server(host="127.0.0.1", port=8765, auth_key=None, auto_claim=False):
    """Starts the multi-threaded bridge HTTP server."""
    config = load_config()
    if host: config["server"]["host"] = host
    if port: config["server"]["port"] = int(port)
    if auth_key: config["auth"]["auth_key"] = auth_key
    if auto_claim: config["bridge"]["auto_claim"] = True

    server_address = (config["server"]["host"], config["server"]["port"])
    httpd = ThreadedHTTPServer(server_address, BridgeRequestHandler)
    httpd.config = config

    logging.info("=" * 70)
    logging.info(f"Antigravity Web Bridge running at http://{config['server']['host']}:{config['server']['port']}")
    logging.info(f"Auth Key: {config['auth']['auth_key']}")
    logging.info(f"Queue Storage: {TASKS_FILE}")
    logging.info("=" * 70)
    logging.info("Bridge is ready to accept authenticated prompt submissions.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("Shutting down bridge server...")
        httpd.shutdown()
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Web Prompt Local Bridge")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind server (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind server (default: 8765)")
    parser.add_argument("--auth-key", default=None, help="Secret authentication key for API access")
    parser.add_argument("--auto-claim", action="store_true", help="Automatically claim tasks upon submission")
    args = parser.parse_args()

    run_server(host=args.host, port=args.port, auth_key=args.auth_key, auto_claim=args.auto_claim)
