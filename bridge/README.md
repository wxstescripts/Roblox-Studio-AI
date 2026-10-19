# Antigravity Web Prompt Local Bridge & Queue Engine

This directory contains the local Windows bridge server for the **Antigravity Web Prompt Control Center** (Task 1.63).

It bridges the public GitHub Pages web interface (`https://wxstescripts.github.io/Roblox-Studio-AI/control-center/`) with the user's local Antigravity workflow on Windows.

---

## 1. Architecture & Execution Flow

```
+-----------------------------------+
|  GitHub Pages (Browser Client)    |
|  /control-center/index.html       |
+-----------------+-----------------+
                  |  (1) Authenticated REST (Bearer Auth)
                  v
+-----------------+-----------------+
|   Local Windows Bridge Server     |
|   bridge/server.py (Port 8765)    |
+--------+------------------+-------+
         | (2) Queue Store  | (3) Safe Handoff
         v                  v
+--------+--------+  +------+------------------------------------------+
|  .queue/        |  |  • Staged to .queue/staged_prompt.md            |
|  • tasks.json   |  |  • Formatted prompt copied to Windows clipboard |
|  • audit.log    |  |  • System notification chime / audio alert      |
|  (Gitignored)   |  |  • Ready for instant paste into Antigravity IDE |
+-----------------+  +-------------------------------------------------+
```

### Why Manual Handoff via Clipboard / Staging?
The installed Antigravity version on this host is the **Antigravity Desktop IDE** (`Antigravity.exe`), which operates as an interactive developer pair programmer. Standalone headless CLI binaries (`agy`) or global SDK modules (`google-antigravity`) with cloud API keys are not installed in the default environment.

Rather than simulating headless execution with fragile window hooks, the bridge provides:
1. **Zero Secret Leakage:** Prompts, queue data, and auth keys are kept on your local PC in `.queue/` and never written to public GitHub issues or public JSON files.
2. **Instant Staging:** Claiming a task instantly writes the full prompt to `.queue/staged_prompt.md` and copies the text directly to your Windows clipboard.
3. **One-Paste Delivery:** You simply press `Ctrl+V` into your active Antigravity chat window and hit Enter.
4. **Status Feedback:** You or the bridge updates task status, logs, and links back to the website.

---

## 2. Quickstart Instructions

### Starting the Bridge Locally

Run with Python 3:

```powershell
# From the repository root:
python bridge/server.py
```

By default, the server runs on `http://127.0.0.1:8765` and will print a generated session auth key on first launch:
```text
======================================================================
Generated Session Auth Key: agy_4b8f3e2d1c9a0...
Use this key in the Web Prompt Control Center interface.
======================================================================
```

### Custom Authentication Key

You can pass a custom passkey using an argument or environment variable:

```powershell
python bridge/server.py --auth-key "my-secret-prompt-key"
```

Or set `BRIDGE_AUTH_KEY`:
```powershell
$env:BRIDGE_AUTH_KEY = "my-secret-prompt-key"
python bridge/server.py
```

### Auto-Claiming Mode

If you want the bridge to automatically claim incoming prompts, copy them to your clipboard, and notify you as soon as they arrive:

```powershell
python bridge/server.py --auto-claim
```

---

## 3. Remote / Mobile Access Options

If you wish to submit prompts from your mobile phone or outside your home network, you can securely expose the bridge endpoint using a free Cloudflare Tunnel or local tunnel:

### Option A: Free Cloudflare Tunnel (Recommended)
1. Download `cloudflared` from [Cloudflare Releases](https://github.com/cloudflare/cloudflared/releases).
2. Run a quick tunnel:
   ```powershell
   cloudflared tunnel --url http://localhost:8765
   ```
3. Copy the generated `https://<random>.trycloudflare.com` URL.
4. Enter that URL in the **Backend URL** field in the Web Prompt Control Center on your phone!
5. All traffic remains end-to-end encrypted and protected by your Bearer Auth Key.

---

## 4. API Endpoints Reference

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `GET` | `/api/health` | Health check & service status | No |
| `POST` | `/api/auth/verify` | Validate auth key credentials | Yes |
| `GET` | `/api/tasks` | List queued tasks (newest first) | Yes |
| `GET` | `/api/tasks/<id>` | Full details & execution logs | Yes |
| `POST` | `/api/tasks/submit` | Submit a new multiline task | Yes |
| `POST` | `/api/tasks/<id>/claim` | Claim task & trigger clipboard handoff | Yes |
| `POST` | `/api/tasks/<id>/approve` | Explicitly approve execution-mode task | Yes |
| `POST` | `/api/tasks/<id>/status` | Update task status, logs & artifacts | Yes |
| `POST` | `/api/tasks/<id>/cancel` | Cancel a pending/staged task | Yes |
| `GET` | `/api/audit` | Read recent audit trail entries | Yes |
