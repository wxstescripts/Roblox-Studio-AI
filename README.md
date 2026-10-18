# Pet Mining Empire — Development Evidence & Review Gallery

[![Review Gallery](https://img.shields.io/badge/Review%20Gallery-Live-00DCFF?style=for-the-badge&logo=roblox&logoColor=black)](https://wxstescripts.github.io/Roblox-Studio-AI/)
[![Task Reports](https://img.shields.io/badge/Task%20Reports-50%20Published-FFCC00?style=for-the-badge&logo=markdown&logoColor=black)](https://wxstescripts.github.io/Roblox-Studio-AI/reports/index.html)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Active-00E676?style=for-the-badge&logo=github&logoColor=white)](https://wxstescripts.github.io/Roblox-Studio-AI/review-gallery/index.html)

This repository serves as the official public review gallery, task-indexed visual evidence hub, and engineering report library for **Pet Mining Empire**. It contains genuine in-engine screenshots, viewport audits, and UI verifications captured directly from Roblox Studio, alongside full Markdown documentation for all completed tasks.

---

## 🌐 Live Review Website Links

- **Interactive Screenshot Gallery:** [https://wxstescripts.github.io/Roblox-Studio-AI/review-gallery/index.html](https://wxstescripts.github.io/Roblox-Studio-AI/review-gallery/index.html)
- **Interactive Task Reports Reader:** [https://wxstescripts.github.io/Roblox-Studio-AI/reports/index.html](https://wxstescripts.github.io/Roblox-Studio-AI/reports/index.html)
- **Portal Landing Page:** [https://wxstescripts.github.io/Roblox-Studio-AI/](https://wxstescripts.github.io/Roblox-Studio-AI/)
- **Machine-Readable Metadata:**
  - Gallery Metadata: [`docs/review-gallery/gallery_data.json`](docs/review-gallery/gallery_data.json)
  - Reports Index: [`docs/reports/reports_data.json`](docs/reports/reports_data.json)

---

## 📄 Published Task Reports (Tasks 1.8 – 1.57)

50 authoritative engineering and verification reports are published in [`docs/reports/`](docs/reports/) and readable in the interactive [Reports Reader](https://wxstescripts.github.io/Roblox-Studio-AI/reports/index.html):

| Category | Task Range | Count | Primary Focus |
| :--- | :---: | :---: | :--- |
| **Tooling & Documentation** | Task 1.56 – 1.57 | 2 | Automated screenshot workflow, review gallery, and GitHub Pages publication |
| **UI Redesign & Design System** | Task 1.50 – 1.55 | 6 | UI Theme, Vector Icon Pack integration, Equipment Forge modal, HUD redesign & verification |
| **Plot Dressing & Wayfinding** | Task 1.46 – 1.48 | 3 | Construction detailing, cable conduits, power cabinets, signage repair, plot onboarding |
| **Progression Design** | Task 1.49 | 1 | Personal mine progression & architecture design |
| **Environment Art Overhaul** | Task 1.32 – 1.45 | 14 | Hub plaza derrick, quarry cliffs, roads, ore node assets, headframe portal, cavern transit |
| **Pet Systems & Economy** | Task 1.22 – 1.31 | 10 | Starter pets, hatching, assist cadence, security, persistence, inventory UX, economy audits |
| **Progression & Caverns** | Task 1.18 – 1.21 | 4 | Deep cavern mining, Stage 2 integration, Stage 3 bulkhead, equipment shop balance |
| **World & Environment** | Task 1.11 – 1.17 | 7 | Initial hub environment blockout, progressive mine, visual quality review, retaining wall fixes |
| **Tycoon & Production** | Task 1.8 – 1.10 | 3 | Machine upgrades, conveyor automation, production system verification |

*(Note: Tasks 1.1–1.7 were completed during initial pre-report project setup; no markdown report artifacts exist for them.)*

---

## 📸 Verified Task Evidence Index

| Task ID | Task Title | Category | Verification Mode | Screenshots | Associated Report |
| :---: | :--- | :---: | :---: | :--- | :---: |
| **Task 1.56** | Automated Screenshot & Public Review Gallery | World & UI | Both (Play & Edit) | [`World Overview`](docs/review-gallery/screenshots/Task-1.56/Task-1.56_world_20261018_154710.jpg) · [`Live UI`](docs/review-gallery/screenshots/Task-1.56/Task-1.56_ui_20261018_154710.jpg) | [Task 1.56 Report](docs/reports/task_1_56_screenshot_workflow_report.md) |
| **Task 1.55** | UI Pack Asset Integration | World & UI | Play Mode | [`Plot Overview`](docs/review-gallery/screenshots/Task-1.55/Task-1.55_world_20261018_154727.jpg) · [`Vector Icon HUD`](docs/review-gallery/screenshots/Task-1.55/Task-1.55_ui_20261018_154727.jpg) | [Task 1.55 Report](docs/reports/task_1_55_ui_pack_integration_report.md) |
| **Task 1.54** | Responsive Equipment Shop Redesign | World & UI | Play Mode | [`Mine Portal`](docs/review-gallery/screenshots/Task-1.54/Task-1.54_world_20261018_154734.jpg) · [`Equipment Forge Modal`](docs/review-gallery/screenshots/Task-1.54/Task-1.54_ui_20261018_154734.jpg) | [Task 1.54 Report](docs/reports/task_1_54_equipment_shop_redesign_report.md) |

---

## 🛠 Automation & Tooling

The evidence capture and report indexing scripts are available in [`tools/`](tools/):

```bash
# Ingest evidence for a completed task
python tools/capture_task_evidence.py \
  --task 1.56 \
  --title "Screenshot Workflow" \
  --world-image path/to/world.jpg \
  --ui-image path/to/ui.jpg

# Rebuild gallery web app
python tools/capture_task_evidence.py --rebuild-only

# Recompile reports catalog metadata
python tools/generate_reports_metadata.py
```
