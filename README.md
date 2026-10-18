# Pet Mining Empire — Development Evidence & Review Gallery

[![Review Gallery](https://img.shields.io/badge/Review%20Gallery-Live-00DCFF?style=for-the-badge&logo=roblox&logoColor=black)](https://wxstescripts.github.io/Roblox-Studio-AI/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Active-00E676?style=for-the-badge&logo=github&logoColor=white)](https://wxstescripts.github.io/Roblox-Studio-AI/review-gallery/index.html)

This repository serves as the official public review gallery and task-indexed visual evidence hub for **Pet Mining Empire**. It contains genuine in-engine screenshots, viewport audits, and UI verifications captured directly from Roblox Studio across implementation tasks.

---

## 🌐 Live Review Gallery Links

- **Interactive Gallery Web App:** [https://wxstescripts.github.io/Roblox-Studio-AI/review-gallery/index.html](https://wxstescripts.github.io/Roblox-Studio-AI/review-gallery/index.html)
- **Portal Landing Page:** [https://wxstescripts.github.io/Roblox-Studio-AI/](https://wxstescripts.github.io/Roblox-Studio-AI/)
- **Machine-Readable Metadata:** [`docs/review-gallery/gallery_data.json`](docs/review-gallery/gallery_data.json)

---

## 📸 Verified Task Evidence Index

| Task ID | Task Title | Category | Verification Mode | Screenshots |
| :---: | :--- | :---: | :---: | :--- |
| **Task 1.56** | Automated Screenshot & Public Review Gallery | World & UI | Both (Play & Edit) | [`World Overview`](docs/review-gallery/screenshots/Task-1.56/Task-1.56_world_20261018_154710.jpg) · [`Live UI`](docs/review-gallery/screenshots/Task-1.56/Task-1.56_ui_20261018_154710.jpg) |
| **Task 1.55** | UI Pack Asset Integration | World & UI | Play Mode | [`Plot Overview`](docs/review-gallery/screenshots/Task-1.55/Task-1.55_world_20261018_154727.jpg) · [`Vector Icon HUD`](docs/review-gallery/screenshots/Task-1.55/Task-1.55_ui_20261018_154727.jpg) |
| **Task 1.54** | Responsive Equipment Shop Redesign | World & UI | Play Mode | [`Mine Portal`](docs/review-gallery/screenshots/Task-1.54/Task-1.54_world_20261018_154734.jpg) · [`Equipment Forge Modal`](docs/review-gallery/screenshots/Task-1.54/Task-1.54_ui_20261018_154734.jpg) |

---

## 🛠 Automation & Tooling

The evidence capture and gallery generation engine is available in [`tools/capture_task_evidence.py`](tools/capture_task_evidence.py).

```bash
# Ingest evidence for a completed task
python tools/capture_task_evidence.py \
  --task 1.57 \
  --title "Connect Screenshot Gallery to GitHub Pages" \
  --world-image path/to/world.jpg \
  --ui-image path/to/ui.jpg

# Rebuild gallery HTML web app
python tools/capture_task_evidence.py --rebuild-only
```
