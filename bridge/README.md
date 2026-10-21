# Antigravity Multi-Developer Bridge & Orchestration Engine

This directory contains the local Windows bridge server for the **Antigravity Multi-Developer Control Center & Project Backlog** (Tasks 1.63 & 1.64).

It bridges the public GitHub Pages web interface (`https://wxstescripts.github.io/Roblox-Studio-AI/control-center/`) with local Antigravity workflows across multiple team members on Windows.

---

## 1. Architecture & Execution Flow

```
+-------------------------------------------------------------+
|  GitHub Pages (Browser Client)                              |
|  /control-center/index.html                                 |
|  Multi-Developer Backlog Board & Queue UI                   |
+------------------------------+------------------------------+
                               | (1) Authenticated REST (Bearer Auth per Developer)
                               v
+-------------------------------------------------------------+
|   Local Windows Bridge Server (bridge/server.py:8765)       |
|   • Developer Identity & Role Check (Lead vs Developer)     |
|   • Exclusive Resource Locks & Conflict Detection Engine     |
|   • Approval Gating (Unapproved tasks blocked from execute) |
|   • Project Lead Agent Audit & Backlog Generator            |
+---------------+------------------------------+--------------+
                | (2) Queue & Backlog Store    | (3) Safe Handoff
                v                              v
+---------------+---------------+  +-----------+-----------------------------------+
|  .queue/                      |  |  • Staged to .queue/staged_prompt.md          |
|  • tasks.json (Active queue)  |  |  • Prompt copied to Windows clipboard (clip)  |
|  • backlog.json (Shared board)|  |  • System notification chime / audio alert    |
|  • audit.log (Security trail) |  |  • Ready for instant paste into Antigravity   |
|  (100% Gitignored)            |  +-----------------------------------------------+
+-------------------------------+
```

---

## 2. Multi-Developer Identity & Role Model

The bridge enables multiple developers to coordinate without sharing personal AI subscriptions, API keys, or browser sessions:

| Developer ID | Default Display Name | Role | Default Claiming Agent | Example Focus |
| :--- | :--- | :---: | :--- | :--- |
| `dev_lead` | Project Lead | `lead` | `Antigravity-Lead-IDE` | Architecture audits, backlog approvals, integration |
| `dev_1` | Frontend & UI Dev | `developer` | `Antigravity-Dev1-IDE` | Responsive HUD, pet inventory, icons, UITheme |
| `dev_2` | Systems & Mining Dev | `developer` | `Antigravity-Dev2-IDE` | Cavern mining, economy balance, server DataStore |

### Role Permissions
* **Project Lead (`lead`):** Can propose tasks, accept proposed tasks into active backlog, approve execution mode, trigger Lead Agent audits, and override lock warnings.
* **Developer (`developer`):** Can propose tasks, claim assigned tasks, comment on decision logs, execute plan-first mode, and update task progress. Cannot approve execution of high-risk tasks without Lead sign-off.

---

## 3. Exclusive Resource Locking & Conflict Policy

### The Roblox Studio Live Place Mutex
Roblox Studio place `109317675035550` operates as a single live DataModel. Concurrent destructive edits to world assemblies or scripts within Studio can cause desynchronization or race conditions.
* The bridge tracks exclusive resource locks: e.g., `RobloxStudio:LivePlace`, `File:MiningService.luau`, `File:PetConfig.luau`.
* When a task claiming `RobloxStudio:LivePlace` is active, any other task attempting to claim the same resource is flagged with a **409 Conflict** error.
* Code tasks targeting independent files (or run in isolated git branches) proceed concurrently without conflict.

---

## 4. REST API Endpoints

### Public
* `GET /api/health` — Bridge status, version, and server capabilities.

### Authenticated (Bearer Token Required)
* `POST /api/auth/verify` — Validates developer token and returns user profile.
* `GET /api/developers` — Lists configured developer identities and roles.
* `GET /api/locks` — Lists active exclusive resource locks and holders.
* `GET /api/backlog` — Returns all shared backlog items annotated with conflict warnings.
* `GET /api/backlog/<id>` — Returns specific backlog item details.
* `POST /api/backlog/propose` — Proposes a new backlog task.
* `POST /api/backlog/<id>/accept` — Accepts proposed task into active backlog (Lead only).
* `POST /api/backlog/<id>/assign` — Assigns task to developer, branch, and agent.
* `POST /api/backlog/<id>/comment` — Adds discussion comment or decision log.
* `POST /api/backlog/generate-audit` — Runs Project Lead Agent audit and regenerates backlog.
* `GET /api/tasks` — Lists active queue tasks.
* `GET /api/tasks/<id>` — Retrieves specific queue task.
* `POST /api/tasks/submit` — Enqueues prompt with conflict checks.
* `POST /api/tasks/<id>/claim` — Claims task, stages to `.queue/staged_prompt.md`, copies to clipboard via `clip.exe`. Enforces approval gate.
* `POST /api/tasks/<id>/approve` — Explicit Lead approval for execution mode.
* `POST /api/tasks/<id>/status` — Updates status (`in_progress`, `completed`, `failed`).
* `POST /api/tasks/<id>/cancel` — Cancels a task.
* `GET /api/audit` — Returns recent security audit log trail.

---

## 5. Quickstart Instructions

```powershell
# From the repository root:
python bridge/server.py
```

Output:
```text
======================================================================
Antigravity Multi-Developer Bridge running at http://127.0.0.1:8765
Queue Storage: C:\Users\heckz\Downloads\Roblox-Studio-AI\.queue\tasks.json
Backlog Storage: C:\Users\heckz\Downloads\Roblox-Studio-AI\.queue\backlog.json
Active Lead Key: agy_control_center_key_2026
======================================================================
Bridge is ready to accept multi-developer prompt and backlog requests.
```

Connect via the [Prompt Control Center](https://wxstescripts.github.io/Roblox-Studio-AI/control-center/).
