# Pet Mining Empire — Task Evidence & Review Gallery

This directory contains the automated, task-indexed screenshot evidence gallery for **Pet Mining Empire**. It documents visual verification for every eligible development and design task across world environments, mining infrastructure, and user interfaces.

---

## Gallery Architecture

```
docs/review-gallery/
├── index.html                 # Responsive, standalone industrial-themed review gallery
├── gallery_data.json          # Machine-readable task index & screenshot metadata database
├── README.md                  # This documentation
└── screenshots/
    ├── Task-1.54/             # Task 1.54 evidence (Equipment Forge modal)
    ├── Task-1.55/             # Task 1.55 evidence (UI pack icons integration)
    ├── Task-1.56/             # Task 1.56 evidence (Live verification & tooling)
    └── Task-X.XX/             # Subsequent task evidence
```

---

## Live Review Options

### 1. Local Browser Review
Open `docs/review-gallery/index.html` directly in any web browser:
```bash
start docs/review-gallery/index.html
```

### 2. GitHub Pages Public Review (When Configured)
When a Git repository is connected and GitHub Pages is enabled for the repository, the gallery is automatically accessible worldwide at:
```
https://<username>.github.io/<repository-name>/docs/review-gallery/
```

To enable GitHub Pages:
1. Ensure git tracking is active:
   ```bash
   git add docs/review-gallery tools .agents
   git commit -m "docs: update review gallery"
   git push origin main
   ```
2. In your GitHub repository:
   - Navigate to **Settings** > **Pages**.
   - Under **Build and deployment** > **Source**, select **Deploy from a branch**.
   - Under **Branch**, select `main` and set the folder to `/docs`.
   - Click **Save**.

---

## Ingesting Evidence from Antigravity Tasks

Run the capture CLI tool from the project root:

```bash
# Ingest both World and UI screenshots
python tools/capture_task_evidence.py \
  --task 1.56 \
  --title "Automated Screenshot & Public Review Gallery" \
  --world-image path/to/world_screenshot.jpg \
  --ui-image path/to/ui_screenshot.jpg \
  --notes "Automated evidence workflow implemented."

# Force overwrite if re-capturing a task
python tools/capture_task_evidence.py --task 1.56 ... --force

# Rebuild index.html from gallery_data.json
python tools/capture_task_evidence.py --rebuild-only
```

---

## Deduplication & Error Safety

- **Deduplication:** The ingestion pipeline checks `gallery_data.json` before registering images. If a task is already indexed, it safely skips re-registering unless `--force` is explicitly provided.
- **Session Safety:** If Play mode is entered for UI screenshots, the tool verifies client initialization and safely terminates Play mode upon completion, never interrupting an ongoing developer session.
- **Non-Destructive:** Tooling files are isolated to `tools/` and `docs/review-gallery/`. No gameplay, progression, or economy code is touched.
