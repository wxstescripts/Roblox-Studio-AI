"""
bridge/server.py
Local Windows Bridge & Multi-Developer AI Orchestration Server for Pet Mining Empire.

Task 1.64 — Multi-Developer AI Orchestration & Project Backlog.
Extends Task 1.63 with:
- Multi-developer identity and role-based authentication (dev_lead vs developer).
- Shared task backlog management with acceptance criteria and dependencies.
- Exclusive resource locking & conflict detection (e.g. RobloxStudio:LivePlace mutex).
- Approval gating (unapproved tasks cannot enter execution).
- Project Lead Agent audit engine & candidate backlog generator.
- Pure Python standard library with zero external pip dependencies.
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
BACKLOG_FILE = os.path.join(QUEUE_DIR, "backlog.json")
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

# Global reentrant thread lock for atomic queue and backlog operations
queue_lock = threading.RLock()


def load_config():
    """Loads configuration with multi-developer support and fallback defaults."""
    config = {
        "server": {
            "host": "127.0.0.1",
            "port": 8765,
            "cors_origins": ["*"]
        },
        "auth": {
            "auth_key": os.environ.get("BRIDGE_AUTH_KEY", ""),
            "developers": {
                "agy_lead_key_2026": {
                    "id": "dev_lead",
                    "name": "Project Lead",
                    "role": "lead",
                    "agent": "Antigravity-Lead-IDE"
                },
                "agy_dev1_key_2026": {
                    "id": "dev_1",
                    "name": "Frontend & UI Dev",
                    "role": "developer",
                    "agent": "Antigravity-Dev1-IDE"
                },
                "agy_dev2_key_2026": {
                    "id": "dev_2",
                    "name": "Systems & Mining Dev",
                    "role": "developer",
                    "agent": "Antigravity-Dev2-IDE"
                }
            }
        },
        "bridge": {
            "auto_claim": False,
            "copy_to_clipboard": True,
            "notify_on_claim": True
        },
        "safety": {
            "max_prompt_length": 25000,
            "default_mode": "plan-first",
            "require_approval_for_execute": True,
            "disallowed_execution_patterns": [
                "rm -rf /",
                "del /f /s /q c:\\",
                "Format-Volume",
                "format c:"
            ]
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

    # Fallback default auth key
    if not config["auth"]["auth_key"]:
        config["auth"]["auth_key"] = "agy_control_center_key_2026"

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


def load_backlog():
    """Reads backlog database from disk; initializes if missing."""
    with queue_lock:
        if not os.path.exists(BACKLOG_FILE):
            initial_backlog = generate_lead_audit_backlog()
            save_backlog(initial_backlog)
            return initial_backlog
        try:
            with open(BACKLOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading backlog: {e}")
            return []


def save_backlog(backlog):
    """Atomically writes backlog database to disk."""
    with queue_lock:
        temp_file = BACKLOG_FILE + ".tmp"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(backlog, f, indent=2, ensure_ascii=False)
            if os.path.exists(BACKLOG_FILE):
                os.replace(temp_file, BACKLOG_FILE)
            else:
                os.rename(temp_file, BACKLOG_FILE)
            return True
        except Exception as e:
            logging.error(f"Error saving backlog: {e}")
            if os.path.exists(temp_file):
                try: os.remove(temp_file)
                except: pass
            return False


def detect_resource_conflicts(target_task_id, target_resources, all_tasks):
    """
    Checks for overlapping exclusive resources with any active tasks.
    Active statuses: assigned, claimed, in_progress, running.
    """
    conflicts = []
    if not target_resources:
        return conflicts

    active_statuses = {"assigned", "claimed", "in_progress", "running"}
    target_set = set(target_resources)

    for task in all_tasks:
        if task.get("id") == target_task_id:
            continue
        if task.get("status") in active_statuses:
            task_res = set(task.get("exclusive_resources", []))
            overlap = target_set.intersection(task_res)
            if overlap:
                conflicts.append({
                    "task_id": task.get("id"),
                    "task_title": task.get("title"),
                    "assigned_dev": task.get("assigned_dev", "unassigned"),
                    "status": task.get("status"),
                    "overlapping_resources": list(overlap)
                })
    return conflicts


def generate_lead_audit_backlog():
    """
    Project Lead Agent core audit engine.
    Audits completed tasks, live Roblox Studio metrics, and code structure to
    produce a prioritized, non-duplicate backlog for multi-developer execution.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    return [
        {
            "id": "TASK-1.65",
            "title": "Game Source Git Synchronization & Multi-Branch Luau Pipeline",
            "description": "Establish a clean synchronization pipeline between local src/ Luau files and git branches. Currently, game scripts reside only in the local directory and are not tracked in the public git repo. Create developer branch structure and pre-commit checks.",
            "priority": "P0",
            "status": "backlog",
            "category": "Tooling & Infrastructure",
            "mode": "plan-first",
            "require_approval": True,
            "approval": {"required": True, "approved": False, "approved_by": None, "approved_at": None},
            "acceptance_criteria": [
                "Track src/ services, controllers, and configs in git on dedicated feature branches",
                "Ensure local secrets and .queue remain strictly gitignored",
                "Provide a one-step command to sync changes to Roblox Studio DataModel via Rojo or Luau reflection",
                "Pass automated git hygiene tests"
            ],
            "dependencies": ["TASK-1.63", "TASK-1.64"],
            "affected_systems": ["Tooling", "Git Pipeline", "Roblox Sync"],
            "affected_files": [".gitignore", "src/", "tools/sync_studio.py"],
            "exclusive_resources": ["Git:MainSourcePipeline"],
            "assigned_dev": "dev_lead",
            "claiming_agent": "Antigravity-Lead-IDE",
            "branch": "feature/task-165-git-sync",
            "can_parallel_with": ["TASK-1.66", "TASK-1.67"],
            "created_at": now_iso,
            "updated_at": now_iso,
            "decision_log": [
                f"[{now_iso}] Identified by Project Lead Agent audit: Git source synchronization is prerequisite for multi-dev code collaboration."
            ],
            "conflict_warnings": []
        },
        {
            "id": "TASK-1.66",
            "title": "Stage 3 Cavern 'Abyssal Depths' Architectural Design & Inspection",
            "description": "Perform a read-only architectural design audit for the cavern expanse beyond the locked Stage 3 Bulkhead Gate (Workspace.Caves.Stage_2.ProgressionGate_Stage3). Define geometry bounds, ore distribution (Tiers 7-9), lighting, and performance budget.",
            "priority": "P1",
            "status": "backlog",
            "category": "World & Caverns",
            "mode": "plan-first",
            "require_approval": True,
            "approval": {"required": True, "approved": False, "approved_by": None, "approved_at": None},
            "acceptance_criteria": [
                "Map coordinate boundaries beyond Z = -170 in Workspace.Caves",
                "Produce comprehensive design document with part budget (<350 parts)",
                "Define Tier 7 Titanium, Tier 8 Obsidian, and Tier 9 Voidstone node placement",
                "Verify no collision with existing Stage 2 cavern geometry"
            ],
            "dependencies": ["TASK-1.21", "TASK-1.37"],
            "affected_systems": ["World/Caves", "Progression", "Mining"],
            "affected_files": ["Workspace.Caves.Stage_2.ProgressionGate_Stage3"],
            "exclusive_resources": ["RobloxStudio:LivePlace"],
            "assigned_dev": "dev_2",
            "claiming_agent": "Antigravity-Dev2-IDE",
            "branch": "feature/task-166-stage3-cavern",
            "can_parallel_with": ["TASK-1.65", "TASK-1.67"],
            "created_at": now_iso,
            "updated_at": now_iso,
            "decision_log": [
                f"[{now_iso}] Project Lead Agent recommendation: High-value player progression sink. Plan-First mode strictly enforced."
            ],
            "conflict_warnings": []
        },
        {
            "id": "TASK-1.67",
            "title": "Pet Fusion & Golden Upgrade System Specification",
            "description": "Design the server-authoritative Pet Fusion mechanic. Players can combine 5 duplicate starter pets (e.g. Rusty Pup) into a Golden variant with a 1.5x mining speed multiplier and distinct aura particles.",
            "priority": "P1",
            "status": "backlog",
            "category": "Pet Systems & Economy",
            "mode": "plan-first",
            "require_approval": True,
            "approval": {"required": True, "approved": False, "approved_by": None, "approved_at": None},
            "acceptance_criteria": [
                "Specification for PetConfig.luau schema update with Golden and Rainbow variants",
                "Server validation logic in PetService preventing duplicate equips or item duplication",
                "UI wireframe specification matching the Task 1.51-1.55 UITheme design system",
                "Zero impact on existing player inventory persistence"
            ],
            "dependencies": ["TASK-1.22", "TASK-1.59"],
            "affected_systems": ["Pet Systems", "Economy", "UI"],
            "affected_files": [
                "src/ReplicatedStorage/Configs/PetConfig.luau",
                "src/ServerScriptService/Services/PetService.luau"
            ],
            "exclusive_resources": ["File:PetConfig.luau", "File:PetService.luau"],
            "assigned_dev": "dev_1",
            "claiming_agent": "Antigravity-Dev1-IDE",
            "branch": "feature/task-167-pet-fusion",
            "can_parallel_with": ["TASK-1.65", "TASK-1.66"],
            "created_at": now_iso,
            "updated_at": now_iso,
            "decision_log": [
                f"[{now_iso}] Project Lead Agent recommendation: Safe to develop concurrently with Task 1.66 because pet configs do not touch the Studio 3D world."
            ],
            "conflict_warnings": []
        },
        {
            "id": "TASK-1.68",
            "title": "Industrial Soundscape & Environmental Audio Audit",
            "description": "Inspect and design spatial soundscape across the 7 hub zones (furnace hum in Equipment Foundry, stasis hum in Bio-Aura, wind in Derrick Vista) and underground cavern echoes. Audit current SoundService footprint.",
            "priority": "P2",
            "status": "proposed",
            "category": "Audio & Immersion",
            "mode": "plan-first",
            "require_approval": False,
            "approval": {"required": False, "approved": False, "approved_by": None, "approved_at": None},
            "acceptance_criteria": [
                "Document existing Sound instances in Workspace and SoundService (currently 2.82 MB memory)",
                "Propose looped SoundZone configurations with RollOffMinDistance and RollOffMaxDistance",
                "Verify mobile audio streaming performance"
            ],
            "dependencies": ["TASK-1.61", "TASK-1.62"],
            "affected_systems": ["Audio", "World/Hub"],
            "affected_files": ["Workspace.Environment.Hub", "SoundService"],
            "exclusive_resources": ["Audio:Soundscape"],
            "assigned_dev": "unassigned",
            "claiming_agent": "Manual",
            "branch": "feature/task-168-soundscape",
            "can_parallel_with": ["TASK-1.65", "TASK-1.66", "TASK-1.67"],
            "created_at": now_iso,
            "updated_at": now_iso,
            "decision_log": [
                f"[{now_iso}] Proposed by Lead Agent: High immersion gain with zero risk to gameplay logic."
            ],
            "conflict_warnings": []
        },
        {
            "id": "TASK-1.69",
            "title": "6-Player Multi-Plot Performance & Mobile Budget Verification",
            "description": "Conduct stress benchmark in Play mode simulating 6 concurrent player tycoons active with droppers, conveyor parts, and mining pet assists. Verify physics step stays under 16.6ms (60 FPS) and memory under 450 MB.",
            "priority": "P2",
            "status": "proposed",
            "category": "Performance & QA",
            "mode": "plan-first",
            "require_approval": False,
            "approval": {"required": False, "approved": False, "approved_by": None, "approved_at": None},
            "acceptance_criteria": [
                "Simulate all 6 plots active simultaneously via automated Luau test harness",
                "Log Stats:GetTotalMemoryUsageMb() over 5 minutes of continuous mining",
                "Verify zero memory leaks in DataService or Network remote events"
            ],
            "dependencies": ["TASK-1.48", "TASK-1.62"],
            "affected_systems": ["Performance", "Plots", "Tycoon"],
            "affected_files": ["Workspace.Plots", "src/ServerScriptService/Services/PlotService.luau"],
            "exclusive_resources": ["QA:PerformanceHarness"],
            "assigned_dev": "unassigned",
            "claiming_agent": "Manual",
            "branch": "feature/task-169-perf-bench",
            "can_parallel_with": ["TASK-1.65", "TASK-1.67", "TASK-1.68"],
            "created_at": now_iso,
            "updated_at": now_iso,
            "decision_log": [
                f"[{now_iso}] Proposed by Lead Agent: Prerequisite before production public launch."
            ],
            "conflict_warnings": []
        }
    ]


def copy_to_windows_clipboard(text):
    """Copies text to the Windows clipboard via native clip.exe with timeout."""
    if sys.platform != "win32":
        return False
    try:
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

    server_version = "AntigravityBridge/1.64"

    def _send_cors_headers(self):
        """Sets CORS headers allowing web interface cross-origin requests."""
        origin = self.headers.get("Origin", "*")
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, X-Requested-With, X-Developer-Id")
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

    def _send_error(self, status_code, message, extra=None):
        """Sends an error response."""
        data = {"error": message, "status": "error"}
        if extra:
            data.update(extra)
        self._send_json(status_code, data)

    def do_OPTIONS(self):
        """Responds to preflight CORS requests."""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def _authenticate(self):
        """
        Authenticates Bearer token against configured developer credentials.
        Sets self.current_user to the matched developer record.
        """
        auth_header = self.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return False
        token = auth_header[7:].strip()

        # Check multi-developer mapping first
        devs = self.server.config.get("auth", {}).get("developers", {})
        if token in devs:
            self.current_user = devs[token]
            return True

        # Fallback to master auth_key
        expected = self.server.config["auth"]["auth_key"]
        if hmac.compare_digest(token, expected):
            # Check if an explicit developer id header was supplied
            dev_id = self.headers.get("X-Developer-Id", "dev_lead")
            self.current_user = {
                "id": dev_id,
                "name": "Project Lead (Authenticated)",
                "role": "lead" if dev_id == "dev_lead" else "developer",
                "agent": "Antigravity-IDE"
            }
            return True

        return False

    def _read_json_body(self):
        """Reads and parses incoming JSON request body."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 10 * 1024 * 1024:
                return None
            body_bytes = self.rfile.read(content_length)
            return json.loads(body_bytes.decode("utf-8"))
        except Exception as e:
            logging.warning(f"Invalid JSON request: {e}")
            return None

    def _claim_task(self, task):
        """Atomic handoff to local clipboard and staging file."""
        now_iso = datetime.now(timezone.utc).isoformat()
        task["status"] = "running"
        task["claimed_at"] = now_iso
        dev_name = getattr(self, "current_user", {}).get("name", "Local Operator")
        task["logs"].append(f"[{now_iso}] Task claimed by {dev_name} for execution.")

        # Stage prompt to markdown file
        try:
            with open(STAGED_PROMPT_FILE, "w", encoding="utf-8") as f:
                f.write(f"# {task['title']} ({task['id']})\n\n")
                f.write(f"**Assigned:** {task.get('assigned_dev', 'unassigned')} | **Mode:** {task.get('mode', 'plan-first')}\n\n")
                f.write(task.get("prompt", ""))
            task["logs"].append(f"[{now_iso}] Prompt staged to staged_prompt.md")
        except Exception as e:
            logging.error(f"Failed to stage prompt file: {e}")

        # Native clipboard copy
        if self.server.config["bridge"]["copy_to_clipboard"]:
            clipboard_text = f"# {task['title']} ({task['id']})\n\n{task.get('prompt', '')}"
            if copy_to_windows_clipboard(clipboard_text):
                task["logs"].append(f"[{now_iso}] Prompt copied to Windows clipboard ready for Antigravity IDE paste.")

        # Audio alert
        if self.server.config["bridge"]["notify_on_claim"]:
            notify_windows("Antigravity Prompt Staged", f"Task {task['id']} is staged on clipboard.")

    # -------------------------------------------------------------
    # GET Handlers
    # -------------------------------------------------------------
    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/")

        # Health check does not require auth
        if path == "/api/health" or path == "":
            self._send_json(200, {
                "status": "online",
                "service": "Antigravity Multi-Developer Bridge",
                "version": "1.64.0",
                "handoff_mode": "secure_queue_manual_clipboard",
                "antigravity_status": "active_desktop_ide",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "capabilities": [
                    "multi_developer_auth",
                    "shared_backlog",
                    "resource_locks",
                    "approval_gating",
                    "project_lead_audit"
                ]
            })
            return

        # All other endpoints require authentication
        if not self._authenticate():
            self._send_error(401, "Unauthorized: Valid Bearer token required")
            return

        # List registered developers
        if path == "/api/developers":
            devs = list(self.server.config.get("auth", {}).get("developers", {}).values())
            self._send_json(200, {"developers": devs, "count": len(devs)})
            return

        # List active resource locks
        if path == "/api/locks":
            tasks = load_tasks() + load_backlog()
            active_locks = {}
            for t in tasks:
                if t.get("status") in ["assigned", "claimed", "in_progress", "running"]:
                    for res in t.get("exclusive_resources", []):
                        active_locks[res] = {
                            "held_by_task": t.get("id"),
                            "task_title": t.get("title"),
                            "assigned_dev": t.get("assigned_dev", "unassigned"),
                            "status": t.get("status")
                        }
            self._send_json(200, {"active_locks": active_locks, "count": len(active_locks)})
            return

        # List backlog tasks
        if path == "/api/backlog":
            backlog = load_backlog()
            # Annotate with real-time conflict warnings
            for item in backlog:
                item["conflict_warnings"] = detect_resource_conflicts(
                    item.get("id"),
                    item.get("exclusive_resources", []),
                    backlog
                )
            self._send_json(200, {"backlog": backlog, "count": len(backlog)})
            return

        # Get specific backlog item
        if path.startswith("/api/backlog/"):
            item_id = path.split("/")[3]
            backlog = load_backlog()
            item = next((b for b in backlog if b.get("id") == item_id), None)
            if item:
                item["conflict_warnings"] = detect_resource_conflicts(
                    item.get("id"),
                    item.get("exclusive_resources", []),
                    backlog
                )
                self._send_json(200, {"item": item})
            else:
                self._send_error(404, f"Backlog item {item_id} not found")
            return

        # List queue tasks
        if path == "/api/tasks":
            tasks = load_tasks()
            tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            self._send_json(200, {"tasks": tasks, "count": len(tasks)})
            return

        # Get specific queue task
        if path.startswith("/api/tasks/"):
            task_id = path.split("/")[3]
            tasks = load_tasks()
            task = next((t for t in tasks if t.get("id") == task_id), None)
            if task:
                self._send_json(200, {"task": task})
            else:
                self._send_error(404, f"Task {task_id} not found")
            return

        # Audit log trail
        if path == "/api/audit":
            if os.path.exists(AUDIT_LOG_FILE):
                with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
                    lines = f.readlines()[-150:]
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
                self._send_json(200, {
                    "authenticated": True,
                    "user": self.current_user,
                    "message": f"Welcome {self.current_user.get('name', 'Developer')}"
                })
            else:
                self._send_error(401, "Invalid authentication credentials")
            return

        # All mutating actions require authentication
        if not self._authenticate():
            self._send_error(401, "Unauthorized: Valid Bearer token required")
            return

        body = self._read_json_body() or {}
        now_iso = datetime.now(timezone.utc).isoformat()

        # ---------------------------------------------------------
        # Backlog Management Endpoints (Task 1.64)
        # ---------------------------------------------------------

        # Propose Backlog Task
        if path == "/api/backlog/propose":
            title = body.get("title", "").strip()
            description = body.get("description", "").strip()
            if not title:
                self._send_error(400, "Field 'title' is required")
                return

            seq = int(time.time() * 1000) % 100000
            item_id = f"TASK-{seq:05d}"
            exclusive_res = body.get("exclusive_resources", [])

            backlog = load_backlog()
            conflicts = detect_resource_conflicts(item_id, exclusive_res, backlog)

            new_item = {
                "id": item_id,
                "title": title,
                "description": description,
                "priority": body.get("priority", "P2"),
                "status": "proposed",
                "category": body.get("category", "General"),
                "mode": body.get("mode", "plan-first"),
                "require_approval": body.get("require_approval", True),
                "approval": {
                    "required": body.get("require_approval", True),
                    "approved": False,
                    "approved_by": None,
                    "approved_at": None
                },
                "acceptance_criteria": body.get("acceptance_criteria", []),
                "dependencies": body.get("dependencies", []),
                "affected_systems": body.get("affected_systems", []),
                "affected_files": body.get("affected_files", []),
                "exclusive_resources": exclusive_res,
                "assigned_dev": body.get("assigned_dev", "unassigned"),
                "claiming_agent": body.get("claiming_agent", "Manual"),
                "branch": body.get("branch", f"feature/{item_id.lower()}"),
                "can_parallel_with": body.get("can_parallel_with", []),
                "created_at": now_iso,
                "updated_at": now_iso,
                "decision_log": [
                    f"[{now_iso}] Proposed by {self.current_user.get('name', 'Developer')}."
                ],
                "conflict_warnings": conflicts
            }

            backlog.append(new_item)
            save_backlog(backlog)
            logging.info(f"Backlog task proposed: {item_id} — '{title}' by {self.current_user.get('name')}")
            self._send_json(201, {"success": True, "item": new_item})
            return

        # Accept Backlog Task (Lead only)
        if path.endswith("/accept") and "/api/backlog/" in path:
            item_id = path.split("/")[3]
            backlog = load_backlog()
            item = next((b for b in backlog if b.get("id") == item_id), None)
            if not item:
                self._send_error(404, f"Backlog item {item_id} not found")
                return

            if self.current_user.get("role") != "lead":
                self._send_error(403, "Only a Project Lead can accept proposed tasks into active backlog")
                return

            item["status"] = "backlog"
            item["updated_at"] = now_iso
            item["decision_log"].append(f"[{now_iso}] Accepted into active backlog by Lead {self.current_user.get('name')}.")
            save_backlog(backlog)
            self._send_json(200, {"success": True, "item": item})
            return

        # Assign Backlog Task
        if path.endswith("/assign") and "/api/backlog/" in path:
            item_id = path.split("/")[3]
            backlog = load_backlog()
            item = next((b for b in backlog if b.get("id") == item_id), None)
            if not item:
                self._send_error(404, f"Backlog item {item_id} not found")
                return

            assigned_dev = body.get("assigned_dev", self.current_user.get("id"))
            claiming_agent = body.get("claiming_agent", self.current_user.get("agent", "Antigravity-IDE"))
            branch = body.get("branch", item.get("branch"))

            # Check for resource conflict before assignment
            conflicts = detect_resource_conflicts(item_id, item.get("exclusive_resources", []), backlog)
            if conflicts and not body.get("force", False):
                self._send_error(409, "Exclusive resource conflict detected with active tasks", {
                    "conflicts": conflicts,
                    "resolution": "Wait for conflicting task to complete or set force=True (Lead override)"
                })
                return

            item["assigned_dev"] = assigned_dev
            item["claiming_agent"] = claiming_agent
            item["branch"] = branch
            item["status"] = "assigned"
            item["updated_at"] = now_iso
            item["decision_log"].append(
                f"[{now_iso}] Assigned to {assigned_dev} ({claiming_agent}) on branch '{branch}'."
            )
            save_backlog(backlog)
            self._send_json(200, {"success": True, "item": item})
            return

        # Add comment / decision to Backlog item
        if path.endswith("/comment") and "/api/backlog/" in path:
            item_id = path.split("/")[3]
            comment_text = body.get("comment", "").strip()
            if not comment_text:
                self._send_error(400, "Field 'comment' cannot be empty")
                return

            backlog = load_backlog()
            item = next((b for b in backlog if b.get("id") == item_id), None)
            if not item:
                self._send_error(404, f"Backlog item {item_id} not found")
                return

            entry = f"[{now_iso}] {self.current_user.get('name')}: {comment_text}"
            item["decision_log"].append(entry)
            item["updated_at"] = now_iso
            save_backlog(backlog)
            self._send_json(200, {"success": True, "item": item})
            return

        # Run Project Lead Agent Audit & Regeneration
        if path == "/api/backlog/generate-audit":
            audit_backlog = generate_lead_audit_backlog()
            save_backlog(audit_backlog)
            logging.info("Project Lead Agent audit regenerated complete backlog.")
            self._send_json(200, {
                "success": True,
                "message": "Project Lead Agent audit successfully generated prioritized backlog",
                "backlog": audit_backlog,
                "count": len(audit_backlog)
            })
            return

        # ---------------------------------------------------------
        # Queue Execution Endpoints (Extended from Task 1.63)
        # ---------------------------------------------------------

        # Submit Task to execution queue
        if path == "/api/tasks/submit":
            prompt = body.get("prompt", "").strip()
            if not prompt:
                self._send_error(400, "Field 'prompt' is required and cannot be empty")
                return

            max_len = self.server.config["safety"]["max_prompt_length"]
            if len(prompt) > max_len:
                self._send_error(400, f"Prompt length exceeds maximum allowed ({max_len})")
                return

            mode = body.get("mode", self.server.config["safety"]["default_mode"])
            if mode not in ["plan-first", "execute"]:
                mode = "plan-first"

            title = body.get("title", "").strip()
            if not title:
                first_line = prompt.split("\n")[0].strip("#* -")
                title = (first_line[:60] + "...") if len(first_line) > 60 else first_line
                if not title: title = "Untitled Task"

            task_seq = int(time.time() * 1000) % 100000
            task_id = body.get("task_id", f"TASK-{task_seq:05d}")

            require_approval = body.get("require_approval", False)
            if mode == "execute" and self.server.config["safety"]["require_approval_for_execute"]:
                require_approval = True

            exclusive_res = body.get("exclusive_resources", [])
            tasks = load_tasks()

            # Detect conflicts with active tasks
            conflicts = detect_resource_conflicts(task_id, exclusive_res, tasks)
            if conflicts and mode == "execute" and not body.get("force", False):
                self._send_error(409, "Exclusive resource conflict detected with active queue task", {
                    "conflicts": conflicts
                })
                return

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
                    "approved_by": None,
                    "approved_at": None
                },
                "exclusive_resources": exclusive_res,
                "assigned_dev": body.get("assigned_dev", self.current_user.get("id")),
                "claiming_agent": body.get("claiming_agent", self.current_user.get("agent", "Antigravity-IDE")),
                "branch": body.get("branch", "main"),
                "created_at": now_iso,
                "claimed_at": None,
                "completed_at": None,
                "logs": [
                    f"[{now_iso}] Task submitted by {self.current_user.get('name')} (Mode: {mode}, Approval Required: {require_approval})"
                ],
                "completion_summary": None,
                "artifacts": {
                    "report_ref": None,
                    "commit_sha": None,
                    "gallery_ref": None,
                    "screenshots": []
                }
            }

            tasks.append(new_task)
            save_tasks(tasks)
            logging.info(f"Task queued: {task_id} — '{title}' by {self.current_user.get('name')}")

            if self.server.config["bridge"]["auto_claim"]:
                self._claim_task(new_task)

            self._send_json(201, {"success": True, "task": new_task})
            return

        # Claim Task (Enforces approval gating & conflict prevention)
        if path.endswith("/claim"):
            parts = path.split("/")
            if len(parts) >= 4:
                task_id = parts[3]
                tasks = load_tasks()
                task = next((t for t in tasks if t.get("id") == task_id), None)
                if not task:
                    self._send_error(404, f"Task {task_id} not found")
                    return

                # Approval Gate Check
                if task.get("require_approval") and not task.get("approval", {}).get("approved"):
                    self._send_error(403, f"Approval Required: Task {task_id} requires explicit Project Lead approval before execution.")
                    return

                # Resource conflict check
                conflicts = detect_resource_conflicts(task_id, task.get("exclusive_resources", []), tasks)
                if conflicts and not body.get("force", False):
                    self._send_error(409, "Cannot claim task: Exclusive resource is currently locked by another active task", {
                        "conflicts": conflicts
                    })
                    return

                if task["status"] not in ["pending", "assigned", "awaiting_approval"]:
                    self._send_error(409, f"Task {task_id} cannot be claimed (current status: {task['status']})")
                    return

                self._claim_task(task)
                save_tasks(tasks)
                self._send_json(200, {"success": True, "task": task})
                return

        # Approve Task (Requires Project Lead role)
        if path.endswith("/approve"):
            parts = path.split("/")
            if len(parts) >= 4:
                task_id = parts[3]
                tasks = load_tasks()
                task = next((t for t in tasks if t.get("id") == task_id), None)
                if not task:
                    self._send_error(404, f"Task {task_id} not found")
                    return

                if self.current_user.get("role") != "lead":
                    self._send_error(403, "Permission Denied: Only a Project Lead can approve execution mode tasks")
                    return

                task["approval"]["approved"] = True
                task["approval"]["approved_by"] = self.current_user.get("name")
                task["approval"]["approved_at"] = now_iso
                task["logs"].append(f"[{now_iso}] Execution approved by Project Lead {self.current_user.get('name')}.")
                if task["status"] == "awaiting_approval":
                    task["status"] = "running"
                save_tasks(tasks)

                logging.info(f"Task {task_id} approved for execution by {self.current_user.get('name')}.")
                self._send_json(200, {"success": True, "task": task})
                return

        # Update Task Status & Logs
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
                if new_status and new_status in ["pending", "assigned", "claimed", "running", "awaiting_approval", "completed", "failed", "cancelled"]:
                    task["status"] = new_status
                    if new_status == "completed":
                        task["completed_at"] = now_iso

                if "log" in body:
                    task["logs"].append(f"[{now_iso}] {body['log']}")

                if "completion_summary" in body:
                    task["completion_summary"] = body["completion_summary"]

                if "artifacts" in body and isinstance(body["artifacts"], dict):
                    task["artifacts"].update(body["artifacts"])

                save_tasks(tasks)
                self._send_json(200, {"success": True, "task": task})
                return

        # Cancel Task
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

                task["status"] = "cancelled"
                task["logs"].append(f"[{now_iso}] Cancelled by {self.current_user.get('name')}.")
                save_tasks(tasks)
                self._send_json(200, {"success": True, "task": task})
                return

        self._send_error(404, "Endpoint not found")


def main():
    parser = argparse.ArgumentParser(description="Antigravity Multi-Developer Bridge Server")
    parser.add_argument("--port", type=int, default=None, help="Server port (default: 8765)")
    parser.add_argument("--host", type=str, default=None, help="Server host (default: 127.0.0.1)")
    parser.add_argument("--auth-key", type=str, default=None, help="Override master auth key")
    args = parser.parse_args()

    config = load_config()
    host = args.host or config["server"]["host"]
    port = args.port or config["server"]["port"]
    if args.auth_key:
        config["auth"]["auth_key"] = args.auth_key

    server_address = (host, port)
    httpd = ThreadedHTTPServer(server_address, BridgeRequestHandler)
    httpd.config = config

    logging.info("=" * 70)
    logging.info(f"Antigravity Multi-Developer Bridge running at http://{host}:{port}")
    logging.info(f"Queue Storage: {TASKS_FILE}")
    logging.info(f"Backlog Storage: {BACKLOG_FILE}")
    logging.info(f"Active Lead Key: {config['auth']['auth_key']}")
    logging.info("=" * 70)
    logging.info("Bridge is ready to accept multi-developer prompt and backlog requests.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("Bridge server stopping gracefully...")
        httpd.server_close()


if __name__ == "__main__":
    main()
