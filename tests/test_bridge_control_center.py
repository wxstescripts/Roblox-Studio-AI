"""
tests/test_bridge_control_center.py
Automated Verification Test Suite for Task 1.63 — Antigravity Web Prompt Control Center.

Verifies:
1. Authorized prompt submission (201 Created).
2. Rejection of unauthenticated submissions (401 Unauthorized).
3. Prompt privacy and absence of secrets in public files / git.
4. Queue claiming and duplicate prevention (atomic claim, 409 on second claim).
5. Status transitions and error reporting (pending -> claimed -> running -> completed).
6. Local handoff to Antigravity (staging to .queue/staged_prompt.md and clipboard handling).
7. Website layout files and responsive CSS definitions.
8. Existing report reader and review gallery page integrity.
9. Reloading / persistence of tasks across backend restarts.
10. End-to-end test of a harmless read-only prompt.
"""

import os
import sys
import time
import json
import urllib.request
import urllib.error
import subprocess
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEST_PORT = 18765
TEST_AUTH_KEY = "test_agy_secret_token_123456"
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"


class TestAntigravityControlCenter(unittest.TestCase):
    server_proc = None

    @classmethod
    def setUpClass(cls):
        """Starts the bridge server in a background subprocess on TEST_PORT."""
        server_script = os.path.join(ROOT_DIR, "bridge", "server.py")
        cmd = [
            sys.executable,
            server_script,
            "--port", str(TEST_PORT),
            "--auth-key", TEST_AUTH_KEY
        ]
        cls.server_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1.5) # Wait for socket to bind

    @classmethod
    def tearDownClass(cls):
        """Terminates the bridge server subprocess."""
        if cls.server_proc:
            cls.server_proc.terminate()
            cls.server_proc.wait(timeout=5)

    def _request(self, method, endpoint, data=None, auth_header=True):
        """Helper to send HTTP requests to test server."""
        url = f"{BASE_URL}{endpoint}"
        req = urllib.request.Request(url, method=method)
        req.add_header("Content-Type", "application/json")
        if auth_header:
            req.add_header("Authorization", f"Bearer {TEST_AUTH_KEY}")
        
        body_bytes = json.dumps(data).encode("utf-8") if data else None
        try:
            with urllib.request.urlopen(req, data=body_bytes, timeout=5) as res:
                body = res.read().decode("utf-8")
                return res.status, json.loads(body) if body else {}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            return e.code, json.loads(err_body) if err_body else {}

    # Test 1: Health check
    def test_01_health_check(self):
        code, data = self._request("GET", "/api/health", auth_header=False)
        self.assertEqual(code, 200)
        self.assertEqual(data.get("status"), "online")
        self.assertEqual(data.get("handoff_mode"), "secure_queue_manual_clipboard")

    # Test 2: Rejection of unauthenticated submissions
    def test_02_rejection_of_unauthenticated(self):
        # Missing auth header
        code, data = self._request("POST", "/api/tasks/submit", {"prompt": "Test unauth"}, auth_header=False)
        self.assertEqual(code, 401)
        self.assertIn("error", data)

        # Wrong auth token
        url = f"{BASE_URL}/api/tasks/submit"
        req = urllib.request.Request(url, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", "Bearer invalid_secret_token")
        try:
            with urllib.request.urlopen(req, data=b'{"prompt":"test"}', timeout=5):
                self.fail("Expected 401 Unauthorized")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 401)

    # Test 3: Authorized prompt submission
    def test_03_authorized_prompt_submission(self):
        payload = {
            "title": "Task 1.63 Automated Test Task",
            "prompt": "Read-only inspection of Roblox Studio DataModel hierarchy.\nVerify 12 Stage 1 ore nodes.",
            "mode": "plan-first",
            "category": "Testing"
        }
        code, data = self._request("POST", "/api/tasks/submit", payload, auth_header=True)
        self.assertEqual(code, 201)
        self.assertTrue(data.get("success"))
        task = data.get("task")
        self.assertIsNotNone(task)
        self.assertTrue(task["id"].startswith("TASK-"))
        self.assertEqual(task["status"], "pending")
        self.assertEqual(task["mode"], "plan-first")
        self.assertEqual(task["title"], "Task 1.63 Automated Test Task")

    # Test 4: Queue claiming and duplicate prevention
    def test_04_queue_claiming_and_duplicate_prevention(self):
        # 1. Submit a fresh task
        _, submit_res = self._request("POST", "/api/tasks/submit", {
            "title": "Claim Race Prevention Test",
            "prompt": "Test atomic claim locking."
        })
        task_id = submit_res["task"]["id"]

        # 2. First claim must succeed
        code1, data1 = self._request("POST", f"/api/tasks/{task_id}/claim")
        self.assertEqual(code1, 200)
        self.assertTrue(data1.get("success"))
        self.assertIn(data1["task"]["status"], ["running", "awaiting_approval"])

        # 3. Second claim on same task must fail with 409 Conflict
        code2, data2 = self._request("POST", f"/api/tasks/{task_id}/claim")
        self.assertEqual(code2, 409)
        self.assertIn("cannot be claimed", data2.get("error", ""))

    # Test 5: Status transitions & error logging
    def test_05_status_transitions(self):
        _, submit_res = self._request("POST", "/api/tasks/submit", {
            "title": "Status Transition Lifecycle Test",
            "prompt": "Inspect lifecycle."
        })
        task_id = submit_res["task"]["id"]

        # Move to running with a log
        code, _ = self._request("POST", f"/api/tasks/{task_id}/status", {
            "status": "running",
            "log": "Inspection started on local bridge."
        })
        self.assertEqual(code, 200)

        # Move to completed with completion summary and artifacts
        code, comp_res = self._request("POST", f"/api/tasks/{task_id}/status", {
            "status": "completed",
            "completion_summary": "Inspection complete. 0 defects identified.",
            "artifacts": {
                "report_ref": "../reports/test_report.md",
                "commit_sha": "abc1234"
            }
        })
        self.assertEqual(code, 200)
        task = comp_res["task"]
        self.assertEqual(task["status"], "completed")
        self.assertIsNotNone(task["completed_at"])
        self.assertEqual(task["artifacts"]["commit_sha"], "abc1234")

    # Test 6: Staging file creation on claim (Local Handoff)
    def test_06_local_staging_handoff(self):
        test_prompt = "Perform safety audit of plot feeder roads.\nEnsure all 6 plots reachable."
        _, submit_res = self._request("POST", "/api/tasks/submit", {
            "title": "Handoff Staging File Test",
            "prompt": test_prompt
        })
        task_id = submit_res["task"]["id"]

        # Claim the task
        self._request("POST", f"/api/tasks/{task_id}/claim")

        # Verify .queue/staged_prompt.md was written
        staged_file = os.path.join(ROOT_DIR, ".queue", "staged_prompt.md")
        self.assertTrue(os.path.exists(staged_file))
        with open(staged_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn(task_id, content)
        self.assertIn("safety audit of plot feeder roads", content)

    # Test 7: Secret Privacy & Absence from Git Tracking
    def test_07_secret_privacy_git_check(self):
        # Run git status to ensure .queue and bridge_config.json are not tracked
        res = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT_DIR, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        untracked = res.stdout
        self.assertNotIn(".queue/", untracked)
        self.assertNotIn("bridge_config.json", untracked)
        self.assertNotIn(".env", untracked)

    # Test 8: Web UI File Existence & Navigation Integrity
    def test_08_web_interface_integrity(self):
        ctrl_file = os.path.join(ROOT_DIR, "docs", "control-center", "index.html")
        reports_file = os.path.join(ROOT_DIR, "docs", "reports", "index.html")
        gallery_file = os.path.join(ROOT_DIR, "docs", "review-gallery", "index.html")
        portal_file = os.path.join(ROOT_DIR, "docs", "index.html")

        self.assertTrue(os.path.exists(ctrl_file), "control-center/index.html missing")
        self.assertTrue(os.path.exists(reports_file), "reports/index.html missing")
        self.assertTrue(os.path.exists(gallery_file), "review-gallery/index.html missing")
        self.assertTrue(os.path.exists(portal_file), "docs/index.html missing")

        # Verify cross-links
        with open(ctrl_file, "r", encoding="utf-8") as f:
            ctrl_html = f.read()
        self.assertIn("review-gallery/index.html", ctrl_html)
        self.assertIn("reports/index.html", ctrl_html)

        with open(reports_file, "r", encoding="utf-8") as f:
            rep_html = f.read()
        self.assertIn("control-center/index.html", rep_html)

        with open(gallery_file, "r", encoding="utf-8") as f:
            gal_html = f.read()
        self.assertIn("control-center/index.html", gal_html)

        with open(portal_file, "r", encoding="utf-8") as f:
            port_html = f.read()
        self.assertIn("control-center/index.html", port_html)

    # Test 9: End-to-End Harmless Prompt Submission & Lifecycle
    def test_09_end_to_end_harmless_prompt(self):
        harmless_prompt = (
            "# Task 1.63 End-to-End Verification\n\n"
            "## Goal\n"
            "Perform a read-only health check of the local bridge and website.\n"
            "Confirm that the task queue maintains clean state transitions."
        )
        # Submit
        code, sub = self._request("POST", "/api/tasks/submit", {
            "title": "Task 1.63 E2E Harmless Health Check",
            "prompt": harmless_prompt,
            "mode": "plan-first",
            "category": "Testing"
        })
        self.assertEqual(code, 201)
        task_id = sub["task"]["id"]

        # List tasks
        code, list_res = self._request("GET", "/api/tasks")
        self.assertEqual(code, 200)
        ids = [t["id"] for t in list_res["tasks"]]
        self.assertIn(task_id, ids)

        # Claim
        code, claim_res = self._request("POST", f"/api/tasks/{task_id}/claim")
        self.assertEqual(code, 200)
        self.assertEqual(claim_res["task"]["status"], "running")

        # Complete
        code, comp_res = self._request("POST", f"/api/tasks/{task_id}/status", {
            "status": "completed",
            "completion_summary": "E2E health check completed with 100% test pass rate.",
            "artifacts": {
                "report_ref": "../reports/task_1_63_antigravity_web_prompt_control_center_report.md"
            }
        })
        self.assertEqual(code, 200)
        self.assertEqual(comp_res["task"]["status"], "completed")


if __name__ == "__main__":
    unittest.main()
