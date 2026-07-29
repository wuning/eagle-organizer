"""Read-only: print the folder ID -> name map for YOUR Eagle library.

Copy the printed `folders` block into config.json. This script writes nothing.

    python3 scripts/discover_folders.py
"""
import json
import os

from eagle_common import load_config


def walk(folders, prefix=""):
    rows = []
    for f in folders:
        name = f.get("name", "?")
        path = f"{prefix}{name}"
        rows.append((f.get("id", "?"), path))
        rows.extend(walk(f.get("children", []), prefix=path + " / "))
    return rows


def main():
    cfg = load_config()
    meta_path = os.path.join(cfg["library_path"], "metadata.json")
    if not os.path.exists(meta_path):
        raise SystemExit(f"Not found: {meta_path} — check library_path in config.json.")

    meta = json.load(open(meta_path, encoding="utf-8"))
    rows = walk(meta.get("folders", []))

    print(f"# {len(rows)} folders in {cfg['library_path']}\n")
    width = max((len(r[0]) for r in rows), default=8)
    for fid, path in rows:
        print(f"{fid:<{width}}  {path}")

    print("\n# Paste into config.json -> folders (rename values as you like):")
    print(json.dumps(
        {fid: path.split(" / ")[-1] for fid, path in rows},
        ensure_ascii=False, indent=2,
    ))


if __name__ == "__main__":
    main()
