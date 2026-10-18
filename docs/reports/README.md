# Pet Mining Empire — Task Reports Library

This directory contains the authoritative Markdown engineering, verification, and audit reports for **Pet Mining Empire**.

---

## Directory Architecture

```
docs/reports/
├── index.html                 # Interactive task reports browser and Markdown reader web app
├── marked.min.js              # Vendored lightweight Markdown parser (offline & GitHub Pages)
├── reports_data.json          # Machine-readable catalog metadata index for all 50 reports
├── README.md                  # This documentation
└── task_*.md                  # 50 original Markdown reports (Tasks 1.8 through 1.57)
```

---

## Accessing the Reports

- **Interactive Web App:** Open `docs/reports/index.html` or visit `https://wxstescripts.github.io/Roblox-Studio-AI/reports/index.html`
- **Direct Task Routing:** Load any report directly via URL query parameter, e.g. `index.html?task=1.56`
- **Raw Files:** All `.md` files are accessible in this directory and via GitHub raw endpoints.
