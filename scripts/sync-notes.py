#!/usr/bin/env python3
"""
Obsidian 笔记同步脚本

功能：将 _notes/ 目录下的 Obsidian 笔记自动转换为 Jekyll 博客文章，
      并放到 _posts/ 目录下。

用法：
    python3 scripts/sync-notes.py           # 手动运行
    python3 scripts/sync-notes.py --watch   # 监视模式（持续监听文件变化）

笔记格式要求：
    - 文件名: YYYY-MM-DD-标题.md
    - 需要 front matter: title, date, categories, tags
    - 没有 front matter 的笔记会被自动补全（提取文件名中的日期）

原理：
    1. 读取 _notes/ 下的 .md 文件
    2. 检查是否有合法的 Jekyll front matter
    3. 没有的话自动添加（从文件名推断日期和标题）
    4. 复制到 _posts/ 目录
    5. 可选：运行 git commit + push 触发部署
"""

import os
import re
import sys
import yaml
import shutil
from datetime import datetime
from pathlib import Path

NOTES_DIR = Path(__file__).resolve().parent.parent / "_notes"
POSTS_DIR = Path(__file__).resolve().parent.parent / "_posts"

# 文件名匹配: 2024-01-01-标题.md
FILENAME_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$")

DEFAULT_CATEGORY = "踩坑实录"
DEFAULT_TAGS = ["笔记"]

def parse_front_matter(content: str):
    """解析 Jekyll front matter，返回 (metadata_dict, body_text)"""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1]) or {}
                return meta, parts[2].strip()
            except yaml.YAMLError:
                return {}, content
    return {}, content


def build_front_matter(title: str, date_str: str, categories=None, tags=None):
    """构建 front matter 字符串"""
    meta = {
        "title": title,
        "date": date_str,
        "categories": categories or [DEFAULT_CATEGORY],
        "tags": tags or DEFAULT_TAGS,
    }
    return "---\n" + yaml.dump(meta, allow_unicode=True, default_flow_style=False) + "---\n"


def sync_notes():
    """同步所有笔记"""
    if not NOTES_DIR.exists():
        print(f"[skip] _notes 目录不存在: {NOTES_DIR}")
        return

    notes = sorted(NOTES_DIR.glob("*.md"))
    if not notes:
        print("[info] _notes 目录为空，没有笔记需要同步")
        return

    synced = 0
    for note_path in notes:
        # 跳过 README
        if note_path.name.upper() == "README.MD":
            continue

        content = note_path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(content)

        m = FILENAME_PATTERN.match(note_path.name)

        # 确定标题
        if "title" not in meta or not meta["title"]:
            if m:
                meta["title"] = m.group(2).replace("-", " ").replace("_", " ")
            else:
                meta["title"] = note_path.stem

        # 确定日期
        if "date" not in meta or not meta["date"]:
            if m:
                meta["date"] = m.group(1)
            else:
                meta["date"] = datetime.now().strftime("%Y-%m-%d")

        # 确定分类和标签
        meta.setdefault("categories", [DEFAULT_CATEGORY])
        meta.setdefault("tags", DEFAULT_TAGS)

        # 重建完整文件内容
        new_content = build_front_matter(
            title=meta["title"],
            date_str=meta["date"],
            categories=meta["categories"],
            tags=meta["tags"],
        ) + body

        # 写入 _posts/
        post_name = note_path.name
        dest = POSTS_DIR / post_name
        dest.write_text(new_content, encoding="utf-8")

        print(f"[sync] {note_path.name} → _posts/{post_name}")
        synced += 1

    print(f"\n✅ 同步完成！共处理 {synced} 篇笔记，已放到 _posts/ 目录。")
    print("   现在可以 git add, commit, push 部署了。")


def watch_mode():
    """监视模式，持续监听 _notes/ 目录变化"""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("[error] 需要安装 watchdog: pip install watchdog")
        sys.exit(1)

    class NoteHandler(FileSystemEventHandler):
        def on_created(self, event):
            if event.src_path.endswith(".md") and "_notes" in event.src_path:
                print(f"[watch] 检测到新笔记: {os.path.basename(event.src_path)}")
                sync_notes()

        def on_modified(self, event):
            if event.src_path.endswith(".md") and "_notes" in event.src_path:
                print(f"[watch] 笔记已修改: {os.path.basename(event.src_path)}")
                sync_notes()

    print("[watch] 正在监视 _notes/ 目录... (Ctrl+C 停止)")
    event_handler = NoteHandler()
    observer = Observer()
    observer.schedule(event_handler, str(NOTES_DIR), recursive=False)
    observer.start()

    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    if "--watch" in sys.argv:
        watch_mode()
    else:
        sync_notes()
