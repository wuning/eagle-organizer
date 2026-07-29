"""Shared helpers for Eagle Organizer scripts.

Centralizes config loading, the "Eagle must be quit" guard, timestamped backups,
and the cache-file read order. All scripts read library_path / cache_path from
config.json (falling back to config.example.json for smoke tests).
"""
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_CACHE = "~/Library/Application Support/Eagle/library-caches"


def load_config():
    for name in ("config.json", "config.example.json"):
        path = os.path.join(ROOT, name)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                cfg = json.load(f)
            cfg["_source"] = name
            return _expand(cfg)
    sys.exit("No config found. Copy config.example.json to config.json first.")


def _expand(cfg):
    cfg["library_path"] = os.path.expanduser(cfg["library_path"])
    cfg["cache_path"] = os.path.expanduser(cfg.get("cache_path", DEFAULT_CACHE))
    return cfg


def require_eagle_quit():
    """Abort unless Eagle is fully quit — it overwrites metadata while running."""
    try:
        running = subprocess.run(
            ["pgrep", "-x", "Eagle"], capture_output=True
        ).returncode == 0
    except FileNotFoundError:
        running = False  # no pgrep (non-macOS) — trust the user
    if running:
        sys.exit("Eagle is still running. Quit it fully (Cmd+Q), then re-run.")


def now_ms():
    return int(time.time() * 1000)


def ordered_cache_files(cache_path):
    """Return cache .txt files, largest first.

    Eagle keeps one complete cache plus smaller incremental caches (recent changes
    only, with overlapping ids). Reading the largest — most complete — cache first,
    then deduping by id, avoids skipping items that appear only in the complete cache.
    """
    files = [f for f in os.listdir(cache_path) if f.endswith(".txt")]
    files.sort(key=lambda f: os.path.getsize(os.path.join(cache_path, f)), reverse=True)
    return files


def backup(cfg):
    """Snapshot library-caches + library metadata before any write.

    NOTE: per-item image/thumbnail renames are not snapshotted here. Back up the
    whole .library before your first --apply.
    """
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = os.path.join(ROOT, "backups", stamp)
    os.makedirs(dest, exist_ok=True)
    shutil.copytree(cfg["cache_path"], os.path.join(dest, "library-caches"))
    for name in ("metadata.json", "mtime.json"):
        src = os.path.join(cfg["library_path"], name)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dest, name))
    print(f"backup -> backups/{stamp}")
    return dest
