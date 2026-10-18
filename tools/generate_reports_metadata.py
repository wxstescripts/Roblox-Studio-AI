"""
tools/generate_reports_metadata.py
Compiles metadata for all task markdown reports in docs/reports into reports_data.json.
"""

import os
import glob
import json
import re

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORTS_DIR = os.path.join(REPO_DIR, "docs", "reports")
GALLERY_DATA_FILE = os.path.join(REPO_DIR, "docs", "review-gallery", "gallery_data.json")

def categorize_task(num):
    if num <= 10:
        return "Tycoon & Production"
    elif num <= 17:
        return "World & Environment"
    elif num <= 21:
        return "Progression & Caverns"
    elif num <= 31:
        return "Pet Systems & Economy"
    elif num <= 45:
        return "Environment Art Overhaul"
    elif num <= 48:
        return "Plot Dressing & Wayfinding"
    elif num == 49:
        return "Architecture Design"
    elif num <= 55:
        return "UI Redesign & Design System"
    else:
        return "Tooling & Documentation"

def main():
    gallery_map = {}
    if os.path.exists(GALLERY_DATA_FILE):
        with open(GALLERY_DATA_FILE, "r", encoding="utf-8") as f:
            for item in json.load(f):
                gallery_map[item["taskId"]] = item

    report_files = sorted(glob.glob(os.path.join(REPORTS_DIR, "task_*.md")))
    print(f"Found {len(report_files)} report files in {REPORTS_DIR}")

    items = []
    for r in report_files:
        fname = os.path.basename(r)
        m = re.search(r"task_(\d+)_(\d+)", fname)
        if not m:
            continue
        major, minor = int(m.group(1)), int(m.group(2))
        task_id = f"Task-{major}.{minor}"

        with open(r, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        raw_title = ""
        for l in lines[:5]:
            if l.startswith("#"):
                raw_title = l.lstrip("#").strip()
                break
        if not raw_title:
            raw_title = f"Task {major}.{minor} Report"

        raw_title = raw_title.replace("\ufffd", "—").strip()

        summary = ""
        for i, l in enumerate(lines[:35]):
            if any(kw in l.lower() for kw in ["executive summary", "objective", "overview"]):
                for next_l in lines[i+1:i+6]:
                    if not next_l.startswith("#") and len(next_l) > 20:
                        summary = next_l
                        break
                if summary:
                    break
        if not summary:
            for l in lines[1:12]:
                if not l.startswith("#") and len(l) > 30:
                    summary = l
                    break

        summary = summary.replace("\ufffd", "—").strip()
        if len(summary) > 220:
            summary = summary[:217] + "..."

        size = os.path.getsize(r)
        cat = categorize_task(minor)

        g_item = gallery_map.get(task_id)
        has_shots = g_item is not None and len(g_item.get("images", [])) > 0
        shots = []
        if has_shots:
            for img in g_item.get("images", []):
                shots.append({
                    "filename": img.get("filename"),
                    "category": img.get("category"),
                    "mode": img.get("mode"),
                    "description": img.get("description"),
                    "relativePath": "../review-gallery/" + img.get("relativePath"),
                    "publicUrl": img.get("publicUrl"),
                })

        items.append({
            "taskId": task_id,
            "taskMajor": major,
            "taskMinor": minor,
            "filename": fname,
            "title": raw_title,
            "category": cat,
            "sizeBytes": size,
            "summary": summary,
            "hasScreenshots": has_shots,
            "screenshotCount": len(shots),
            "screenshots": shots,
            "rawUrl": f"https://raw.githubusercontent.com/wxstescripts/Roblox-Studio-AI/main/docs/reports/{fname}"
        })

    # Sort descending by task number
    items.sort(key=lambda x: (x["taskMajor"], x["taskMinor"]), reverse=True)

    out_file = os.path.join(REPORTS_DIR, "reports_data.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)

    print(f"Generated {out_file} with {len(items)} reports.")
    for it in items[:6]:
        print(f"  {it['taskId']}: {it['title']} ({it['sizeBytes']} bytes, screenshots: {it['screenshotCount']})")

if __name__ == "__main__":
    main()
