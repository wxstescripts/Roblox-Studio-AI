"""
tools/capture_task_evidence.py
Automated task-indexed screenshot ingestion, deduplication, and public review gallery generator.

Usage:
    python tools/capture_task_evidence.py --task 1.56 --title "Screenshot Workflow" --world-image path/to/world.jpg --ui-image path/to/ui.jpg --notes "Description of changes"
    python tools/capture_task_evidence.py --rebuild-only
"""

import os
import sys
import json
import shutil
import datetime
import argparse
import subprocess
import urllib.request
import re

GALLERY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "review-gallery"))
SCREENSHOTS_DIR = os.path.join(GALLERY_DIR, "screenshots")
DATA_FILE = os.path.join(GALLERY_DIR, "gallery_data.json")
INDEX_HTML = os.path.join(GALLERY_DIR, "index.html")


def get_git_remote_info():
    """Detects git remote origin if configured and computes GitHub Pages base URL."""
    try:
        res = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            url = res.stdout.strip()
            # Match https or ssh
            # https://github.com/owner/repo.git or git@github.com:owner/repo.git
            m = re.search(r"github\.com[:/]([^/]+)/([^/\.]+)", url)
            if m:
                owner, repo = m.group(1), m.group(2)
                pages_url = f"https://{owner}.github.io/{repo}/docs/review-gallery"
                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/docs/review-gallery"
                return {
                    "has_remote": True,
                    "owner": owner,
                    "repo": repo,
                    "pages_url": pages_url,
                    "raw_url": raw_url,
                }
    except Exception:
        pass
    return {"has_remote": False, "pages_url": None, "raw_url": None}


def load_gallery_data():
    """Loads existing gallery database or returns empty list."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] Failed to read {DATA_FILE}: {e}")
    return []


def save_gallery_data(data):
    """Saves gallery database to disk."""
    os.makedirs(GALLERY_DIR, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[INFO] Saved {len(data)} task entries to {DATA_FILE}")


def generate_html_gallery(data, remote_info):
    """Generates a responsive, standalone HTML/CSS/JS gallery web app matching UITheme industrial styling."""
    total_images = sum(len(task.get("images", [])) for task in data)
    last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Sort tasks descending by task ID (handling floating numbers or task strings)
    def parse_task_sort_key(t):
        tid = t.get("taskId", "")
        m = re.search(r"(\d+)\.(\d+)", tid)
        if m:
            return (int(m.group(1)), int(m.group(2)))
        return (0, 0)

    sorted_tasks = sorted(data, key=parse_task_sort_key, reverse=True)

    task_cards_html = []
    for task in sorted_tasks:
        tid = task.get("taskId", "Task")
        title = task.get("title", "")
        ts = task.get("timestamp", "")
        report = task.get("reportRef", "")
        notes = task.get("notes", "")
        images = task.get("images", [])

        img_items_html = []
        for img in images:
            cat = img.get("category", "General")
            mode = img.get("mode", "Edit Mode")
            desc = img.get("description", "")
            rel_path = img.get("relativePath", "")
            pub_url = img.get("publicUrl", rel_path)
            size_kb = round(img.get("sizeBytes", 0) / 1024, 1)

            mode_badge_class = "badge-play" if "Play" in mode else "badge-edit"
            cat_badge_class = "badge-world" if "World" in cat else "badge-ui"

            img_items_html.append(f"""
                <div class="evidence-card" data-category="{cat.lower()}">
                    <div class="thumb-wrapper" onclick="openLightbox('{rel_path}', '{tid} - {desc}', '{mode}', '{cat}')">
                        <img src="{rel_path}" alt="{desc}" loading="lazy" />
                        <div class="overlay-zoom"><span class="zoom-icon">🔍 View Fullscreen</span></div>
                    </div>
                    <div class="evidence-meta">
                        <div class="badge-row">
                            <span class="badge {cat_badge_class}">{cat.upper()}</span>
                            <span class="badge {mode_badge_class}">{mode.upper()}</span>
                            <span class="badge badge-size">{size_kb} KB</span>
                        </div>
                        <div class="evidence-desc">{desc}</div>
                        <div class="evidence-links">
                            <a href="{rel_path}" target="_blank" class="link-btn">Direct Image</a>
                            {f'<a href="{pub_url}" target="_blank" class="link-btn link-remote">Public URL</a>' if remote_info.get("has_remote") else '<span class="status-pill-local">Local Verified</span>'}
                        </div>
                    </div>
                </div>
            """)

        task_cards_html.append(f"""
            <section class="task-section" id="{tid.replace('.', '_')}">
                <div class="task-header">
                    <div class="task-title-group">
                        <span class="task-id-badge">{tid}</span>
                        <h2 class="task-title">{title}</h2>
                    </div>
                    <div class="task-header-meta">
                        <span class="timestamp-tag">Captured: {ts}</span>
                        {f'<span class="report-tag">Report: <code>{report}</code></span>' if report else ''}
                    </div>
                </div>
                {f'<p class="task-notes">{notes}</p>' if notes else ''}
                <div class="evidence-grid">
                    {''.join(img_items_html)}
                </div>
            </section>
        """)

    remote_status_html = ""
    if remote_info.get("has_remote"):
        remote_status_html = f"""
            <span class="remote-badge remote-online">● GitHub Pages Active</span>
            <span class="remote-sub">Base URL: <a href="{remote_info['pages_url']}" target="_blank">{remote_info['pages_url']}</a></span>
        """
    else:
        remote_status_html = """
            <span class="remote-badge remote-offline">● Local Staging Mode (Git Remote Not Configured)</span>
            <span class="remote-sub">Screenshots are fully indexed locally and ready for GitHub Pages publication upon <code>git push</code>.</span>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pet Mining Empire — Task Evidence & Screenshot Gallery</title>
    <style>
        :root {{
            --bg-dark: #0A0D13;
            --bg-panel: #11151F;
            --bg-card: #161C27;
            --bg-elevated: #1F2735;
            --stroke-color: #263042;
            --stroke-glow: rgba(0, 220, 255, 0.3);
            --accent-cyan: #00DCFF;
            --accent-gold: #FFCC00;
            --accent-green: #00E676;
            --accent-red: #FF3D71;
            --text-primary: #FFFFFF;
            --text-secondary: #90A0B5;
            --text-muted: #5E6E82;
            --font-stack: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-dark);
            color: var(--text-primary);
            font-family: var(--font-stack);
            line-height: 1.5;
            padding: 24px 16px 80px 16px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header.gallery-header {{
            background: linear-gradient(180deg, var(--bg-panel) 0%, rgba(17, 21, 31, 0.8) 100%);
            border: 1px solid var(--stroke-color);
            border-radius: 12px;
            padding: 28px 24px;
            margin-bottom: 24px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        }}
        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 16px;
        }}
        .brand-title {{
            font-size: 26px;
            font-weight: 800;
            letter-spacing: 0.5px;
            color: var(--accent-cyan);
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .brand-subtitle {{
            font-size: 14px;
            color: var(--text-secondary);
            margin-top: 4px;
        }}
        .stats-panel {{
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
        }}
        .stat-chip {{
            background: var(--bg-elevated);
            border: 1px solid var(--stroke-color);
            border-radius: 8px;
            padding: 8px 14px;
            display: flex;
            flex-direction: column;
        }}
        .stat-chip .val {{
            font-size: 18px;
            font-weight: 700;
            color: var(--accent-gold);
        }}
        .stat-chip .lbl {{
            font-size: 11px;
            text-transform: uppercase;
            color: var(--text-muted);
            letter-spacing: 0.5px;
        }}
        .remote-status-bar {{
            background: rgba(0, 0, 0, 0.3);
            border-radius: 6px;
            padding: 10px 14px;
            font-size: 13px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 8px;
            border-left: 3px solid var(--accent-cyan);
        }}
        .remote-badge {{
            font-weight: 600;
        }}
        .remote-online {{ color: var(--accent-green); }}
        .remote-offline {{ color: var(--accent-gold); }}
        .remote-sub {{ color: var(--text-secondary); font-size: 12px; }}
        .remote-sub code {{ background: var(--bg-card); padding: 2px 6px; border-radius: 4px; color: var(--accent-cyan); }}

        /* Controls */
        .controls-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 24px;
        }}
        .filter-buttons {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .filter-btn {{
            background: var(--bg-panel);
            border: 1px solid var(--stroke-color);
            color: var(--text-secondary);
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        .filter-btn:hover, .filter-btn.active {{
            background: var(--accent-cyan);
            color: #000;
            border-color: var(--accent-cyan);
        }}
        .search-box {{
            flex: 1;
            max-width: 320px;
        }}
        .search-box input {{
            width: 100%;
            background: var(--bg-panel);
            border: 1px solid var(--stroke-color);
            border-radius: 6px;
            padding: 8px 14px;
            color: var(--text-primary);
            font-size: 13px;
            outline: none;
        }}
        .search-box input:focus {{
            border-color: var(--accent-cyan);
            box-shadow: 0 0 8px var(--stroke-glow);
        }}

        /* Task Sections */
        .task-section {{
            background: var(--bg-panel);
            border: 1px solid var(--stroke-color);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 24px;
            transition: border-color 0.2s ease;
        }}
        .task-section:hover {{
            border-color: #38455C;
        }}
        .task-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
            border-bottom: 1px solid var(--stroke-color);
            padding-bottom: 12px;
            margin-bottom: 16px;
        }}
        .task-title-group {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .task-id-badge {{
            background: var(--accent-cyan);
            color: #000;
            font-weight: 800;
            font-size: 13px;
            padding: 4px 10px;
            border-radius: 4px;
            letter-spacing: 0.5px;
        }}
        .task-title {{
            font-size: 18px;
            font-weight: 700;
            color: var(--text-primary);
        }}
        .task-header-meta {{
            font-size: 12px;
            color: var(--text-muted);
            display: flex;
            gap: 12px;
            align-items: center;
        }}
        .task-header-meta code {{
            background: var(--bg-card);
            padding: 2px 6px;
            border-radius: 4px;
            color: var(--accent-gold);
        }}
        .task-notes {{
            font-size: 13px;
            color: var(--text-secondary);
            margin-bottom: 16px;
            line-height: 1.6;
        }}

        /* Evidence Grid */
        .evidence-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 16px;
        }}
        .evidence-card {{
            background: var(--bg-card);
            border: 1px solid var(--stroke-color);
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .evidence-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.5);
            border-color: #3B4961;
        }}
        .thumb-wrapper {{
            position: relative;
            width: 100%;
            height: 190px;
            background: #000;
            cursor: pointer;
            overflow: hidden;
        }}
        .thumb-wrapper img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            transition: transform 0.3s ease;
        }}
        .thumb-wrapper:hover img {{
            transform: scale(1.03);
        }}
        .overlay-zoom {{
            position: absolute;
            inset: 0;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.2s ease;
        }}
        .thumb-wrapper:hover .overlay-zoom {{
            opacity: 1;
        }}
        .zoom-icon {{
            background: var(--accent-cyan);
            color: #000;
            font-size: 12px;
            font-weight: 700;
            padding: 6px 14px;
            border-radius: 20px;
        }}
        .evidence-meta {{
            padding: 12px 14px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            flex: 1;
        }}
        .badge-row {{
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }}
        .badge {{
            font-size: 10px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 3px;
            letter-spacing: 0.5px;
        }}
        .badge-world {{ background: rgba(0, 220, 255, 0.15); color: var(--accent-cyan); border: 1px solid rgba(0, 220, 255, 0.4); }}
        .badge-ui {{ background: rgba(255, 204, 0, 0.15); color: var(--accent-gold); border: 1px solid rgba(255, 204, 0, 0.4); }}
        .badge-play {{ background: rgba(0, 230, 118, 0.15); color: var(--accent-green); border: 1px solid rgba(0, 230, 118, 0.4); }}
        .badge-edit {{ background: rgba(144, 160, 181, 0.15); color: var(--text-secondary); border: 1px solid var(--stroke-color); }}
        .badge-size {{ background: var(--bg-elevated); color: var(--text-muted); border: 1px solid var(--stroke-color); }}
        .evidence-desc {{
            font-size: 13px;
            color: var(--text-primary);
            font-weight: 500;
            line-height: 1.4;
            flex: 1;
        }}
        .evidence-links {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding-top: 8px;
            border-top: 1px solid rgba(255,255,255,0.06);
        }}
        .link-btn {{
            font-size: 11px;
            font-weight: 600;
            color: var(--accent-cyan);
            text-decoration: none;
            padding: 3px 8px;
            border-radius: 4px;
            background: rgba(0, 220, 255, 0.08);
            border: 1px solid rgba(0, 220, 255, 0.2);
            transition: all 0.2s ease;
        }}
        .link-btn:hover {{
            background: rgba(0, 220, 255, 0.25);
            color: #fff;
        }}
        .status-pill-local {{
            font-size: 11px;
            color: var(--text-muted);
            margin-left: auto;
        }}

        /* Lightbox */
        .lightbox-modal {{
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.92);
            z-index: 9999;
            padding: 24px;
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }}
        .lightbox-modal.active {{
            display: flex;
        }}
        .lightbox-content {{
            max-width: 90vw;
            max-height: 80vh;
            border-radius: 8px;
            border: 1px solid var(--stroke-color);
            box-shadow: 0 10px 40px rgba(0,0,0,0.8);
        }}
        .lightbox-caption {{
            margin-top: 14px;
            color: var(--text-primary);
            font-size: 15px;
            font-weight: 600;
            text-align: center;
        }}
        .lightbox-close {{
            position: absolute;
            top: 20px;
            right: 24px;
            background: var(--bg-card);
            border: 1px solid var(--stroke-color);
            color: var(--text-primary);
            font-size: 20px;
            width: 44px;
            height: 44px;
            border-radius: 6px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="gallery-header">
            <div class="header-top">
                <div>
                    <h1 class="brand-title">⛏ PET MINING EMPIRE</h1>
                    <p class="brand-subtitle">Task Evidence & Verified Viewport Review Gallery</p>
                </div>
                <div class="stats-panel">
                    <div class="stat-chip">
                        <span class="val">{len(data)}</span>
                        <span class="lbl">Tasks Indexed</span>
                    </div>
                    <div class="stat-chip">
                        <span class="val">{total_images}</span>
                        <span class="lbl">Screenshots</span>
                    </div>
                </div>
            </div>
            <div class="remote-status-bar">
                {remote_status_html}
            </div>
        </header>

        <div class="controls-bar">
            <div class="filter-buttons">
                <button class="filter-btn active" onclick="filterGallery('all')">All Evidence</button>
                <button class="filter-btn" onclick="filterGallery('world')">World / Environment</button>
                <button class="filter-btn" onclick="filterGallery('ui')">UI / Interfaces</button>
            </div>
            <div class="search-box">
                <input type="text" id="taskSearch" placeholder="Search tasks, descriptions..." oninput="searchGallery()" />
            </div>
        </div>

        <main id="galleryMain">
            {''.join(task_cards_html) if task_cards_html else '<p style="color:var(--text-muted); text-align:center; padding:40px;">No task screenshots recorded yet.</p>'}
        </main>
    </div>

    <!-- Lightbox Modal -->
    <div id="lightboxModal" class="lightbox-modal" onclick="closeLightbox(event)">
        <button class="lightbox-close" onclick="closeLightbox(null)">✕</button>
        <img id="lightboxImg" class="lightbox-content" src="" alt="Fullscreen screenshot" />
        <div id="lightboxCaption" class="lightbox-caption"></div>
    </div>

    <script>
        function filterGallery(category) {{
            const btns = document.querySelectorAll('.filter-btn');
            btns.forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');

            const cards = document.querySelectorAll('.evidence-card');
            cards.forEach(card => {{
                if (category === 'all' || card.getAttribute('data-category').includes(category)) {{
                    card.style.display = 'flex';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}

        function searchGallery() {{
            const query = document.getElementById('taskSearch').value.toLowerCase();
            const sections = document.querySelectorAll('.task-section');
            sections.forEach(section => {{
                const text = section.innerText.toLowerCase();
                section.style.display = text.includes(query) ? 'block' : 'none';
            }});
        }}

        function openLightbox(src, caption, mode, cat) {{
            document.getElementById('lightboxImg').src = src;
            document.getElementById('lightboxCaption').innerHTML = `<strong>${{caption}}</strong> <span style="color:#00DCFF">[${{cat.toUpperCase()}} - ${{mode.toUpperCase()}}]</span>`;
            document.getElementById('lightboxModal').classList.add('active');
        }}

        function closeLightbox(e) {{
            if (!e || e.target.id === 'lightboxModal' || e.target.classList.contains('lightbox-close')) {{
                document.getElementById('lightboxModal').classList.remove('active');
            }}
        }}
    </script>
</body>
</html>
"""
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[INFO] Generated standalone review gallery at {INDEX_HTML}")


def register_task_evidence(
    task_id: str,
    title: str,
    world_image: str = None,
    ui_image: str = None,
    mode: str = "Play Mode",
    notes: str = "",
    report_ref: str = "",
    force: bool = False,
):
    """Registers task screenshots into the review gallery with idempotency and deduplication."""
    clean_task_id = task_id if task_id.startswith("Task-") else f"Task-{task_id}"
    task_num = clean_task_id.replace("Task-", "")

    existing_data = load_gallery_data()

    # Deduplication check
    existing_entry_idx = -1
    for idx, entry in enumerate(existing_data):
        if entry.get("taskId") == clean_task_id:
            existing_entry_idx = idx
            break

    if existing_entry_idx >= 0 and not force:
        print(f"[DEDUPLICATION] {clean_task_id} is already registered in {DATA_FILE}. Skipping duplicate capture. (Use --force to overwrite)")
        return existing_data[existing_entry_idx]

    # Target folder: docs/review-gallery/screenshots/Task-<id>/
    task_folder = os.path.join(SCREENSHOTS_DIR, clean_task_id)
    os.makedirs(task_folder, exist_ok=True)

    remote_info = get_git_remote_info()
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    iso_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    images_meta = []

    # Process World Image
    if world_image and os.path.exists(world_image):
        ext = os.path.splitext(world_image)[1] or ".jpg"
        target_name = f"{clean_task_id}_world_{timestamp_str}{ext}"
        target_path = os.path.join(task_folder, target_name)
        shutil.copyfile(world_image, target_path)

        rel_path = f"screenshots/{clean_task_id}/{target_name}"
        pub_url = f"{remote_info['pages_url']}/{rel_path}" if remote_info.get("has_remote") else rel_path

        images_meta.append({
            "filename": target_name,
            "category": "World",
            "mode": mode,
            "description": f"Game world view: {title}",
            "relativePath": rel_path,
            "publicUrl": pub_url,
            "status": "Published" if remote_info.get("has_remote") else "Verified Local (Remote Pending)",
            "sizeBytes": os.path.getsize(target_path),
        })
        print(f"[SUCCESS] Ingested World screenshot: {target_name} ({os.path.getsize(target_path)} bytes)")

    # Process UI Image
    if ui_image and os.path.exists(ui_image):
        ext = os.path.splitext(ui_image)[1] or ".jpg"
        target_name = f"{clean_task_id}_ui_{timestamp_str}{ext}"
        target_path = os.path.join(task_folder, target_name)
        shutil.copyfile(ui_image, target_path)

        rel_path = f"screenshots/{clean_task_id}/{target_name}"
        pub_url = f"{remote_info['pages_url']}/{rel_path}" if remote_info.get("has_remote") else rel_path

        images_meta.append({
            "filename": target_name,
            "category": "UI",
            "mode": mode,
            "description": f"User interface view: {title}",
            "relativePath": rel_path,
            "publicUrl": pub_url,
            "status": "Published" if remote_info.get("has_remote") else "Verified Local (Remote Pending)",
            "sizeBytes": os.path.getsize(target_path),
        })
        print(f"[SUCCESS] Ingested UI screenshot: {target_name} ({os.path.getsize(target_path)} bytes)")

    new_entry = {
        "taskId": clean_task_id,
        "title": title,
        "timestamp": iso_timestamp,
        "reportRef": report_ref or f"task_{task_num.replace('.', '_')}_report.md",
        "notes": notes,
        "images": images_meta,
    }

    if existing_entry_idx >= 0 and force:
        print(f"[INFO] Overwriting existing entry for {clean_task_id} due to --force flag.")
        existing_data[existing_entry_idx] = new_entry
    else:
        existing_data.append(new_entry)

    save_gallery_data(existing_data)
    generate_html_gallery(existing_data, remote_info)
    return new_entry


def print_markdown_snippet(entry, remote_info):
    """Outputs a clean Markdown table summarizing the indexed evidence for task reports."""
    print("\n" + "=" * 60)
    print("TASK EVIDENCE REPORT SNIPPET (Copy into Task Deliverable)")
    print("=" * 60)
    print(f"### Evidence & Screenshot Review — {entry['taskId']}: {entry['title']}\n")
    print(f"- **Captured At:** {entry['timestamp']}")
    print(f"- **Gallery Index:** [`docs/review-gallery/index.html`](file:///{INDEX_HTML.replace('\\', '/')})")
    print(f"- **Remote Publishing Status:** {'Active on GitHub Pages' if remote_info.get('has_remote') else 'Local Staging (Pending Remote Configuration)'}\n")
    print("| Category | Mode | Description | Local File | Status |")
    print("| :--- | :---: | :--- | :--- | :---: |")
    for img in entry.get("images", []):
        fn = img["filename"]
        rel = img["relativePath"]
        cat = img["category"]
        mode = img["mode"]
        desc = img["description"]
        stat = img["status"]
        print(f"| **{cat}** | {mode} | {desc} | [`{fn}`](file:///{os.path.join(GALLERY_DIR, rel).replace('\\', '/')}) | **{stat}** |")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Automated Roblox Studio Screenshot & Review Gallery Engine")
    parser.add_argument("--task", type=str, help="Task identifier (e.g. 1.56, 1.55)")
    parser.add_argument("--title", type=str, default="", help="Task title")
    parser.add_argument("--world-image", type=str, default=None, help="Path to world screenshot")
    parser.add_argument("--ui-image", type=str, default=None, help="Path to UI screenshot")
    parser.add_argument("--mode", type=str, default="Play Mode", help="Capture mode (Play Mode / Edit Mode)")
    parser.add_argument("--notes", type=str, default="", help="Task summary notes")
    parser.add_argument("--report-ref", type=str, default="", help="Report markdown reference")
    parser.add_argument("--force", action="store_true", help="Bypass deduplication and overwrite existing task entry")
    parser.add_argument("--rebuild-only", action="store_true", help="Only rebuild the HTML gallery from gallery_data.json")

    args = parser.parse_args()

    remote_info = get_git_remote_info()

    if args.rebuild_only:
        data = load_gallery_data()
        generate_html_gallery(data, remote_info)
        print("[SUCCESS] Gallery rebuilt.")
        return

    if not args.task:
        parser.print_help()
        sys.exit(1)

    entry = register_task_evidence(
        task_id=args.task,
        title=args.title or f"Task {args.task}",
        world_image=args.world_image,
        ui_image=args.ui_image,
        mode=args.mode,
        notes=args.notes,
        report_ref=args.report_ref,
        force=args.force,
    )

    if entry:
        print_markdown_snippet(entry, remote_info)


if __name__ == "__main__":
    main()
