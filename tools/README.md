# Pet Mining Empire — Development Tooling Suite

This directory contains automation utilities and tooling scripts for **Pet Mining Empire**.

---

## 1. `capture_task_evidence.py`

A dedicated automation script for capturing, indexing, deduplicating, and publishing visual screenshot evidence from Roblox Studio tasks.

### Features
- **Idempotency & Deduplication:** Prevents duplicate task entries. Use `--force` to intentionally overwrite.
- **Dual-Category Coverage:** Separately tracks `World` (environment, mines, hub) and `UI` (HUD, modals, shops) evidence.
- **Cross-Platform Compatibility:** Operates on Windows, macOS, and Linux; handles local path translation and GitHub Pages URL computation.
- **Standalone Gallery Generation:** Compiles `docs/review-gallery/index.html` with zero external dependencies, featuring an interactive lightbox modal and search filter.
- **Honest Remote Detection:** Detects whether a Git remote is active. If not configured, clearly flags status as `Verified Local (Remote Pending)` rather than falsifying publication.

### Usage Examples

```bash
# Ingest evidence for completed task
python tools/capture_task_evidence.py \
  --task 1.55 \
  --title "UI Pack Asset Integration" \
  --ui-image "C:/path/to/task155_ui_pack_integrated.jpg" \
  --world-image "C:/path/to/task148_plot_full_dressed_overview.jpg" \
  --mode "Play Mode" \
  --notes "Replaced placeholders with 31 verified vector icons across HUD and Equipment Forge."

# Rebuild gallery HTML only
python tools/capture_task_evidence.py --rebuild-only
```

---

## 2. Antigravity Hook Integration

Antigravity executes commands declared in `.agents/hooks.json` at execution lifecycle milestones:

- **`Stop` Event:** Runs `python tools/capture_task_evidence.py --rebuild-only` whenever an Antigravity execution turn terminates, keeping `index.html` freshly updated and in sync with `gallery_data.json`.
