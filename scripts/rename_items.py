"""Rename / re-tag / re-folder Eagle items. Dry-run by default; --apply to write.

    python3 scripts/rename_items.py updates.json          # preview
    python3 scripts/rename_items.py updates.json --apply   # write, after backup

updates.json format (see examples/updates.example.json):
[
  {"id": "ITEMID", "name": "new-name", "folders": ["FOLDERID"], "tags": ["group-value"]}
]
"""
import json
import os
import subprocess
import sys

from eagle_common import (
    backup,
    load_config,
    now_ms,
    ordered_cache_files,
    require_eagle_quit,
)


def preview(updates, cfg):
    print(f"DRY-RUN — {len(updates)} item(s). Nothing written. Add --apply to write.\n")
    base = os.path.join(cfg["library_path"], "images")
    for u in updates:
        info = os.path.join(base, f"{u['id']}.info", "metadata.json")
        old = (
            json.load(open(info, encoding="utf-8"))["name"]
            if os.path.exists(info)
            else "(no local file)"
        )
        print(f"  {u['id']}: {old} -> {u['name']}  "
              f"folders={u.get('folders')} tags={u.get('tags')}")


def _update_caches(updates_by_id, cfg, now):
    cache_path = cfg["cache_path"]
    for fname in ordered_cache_files(cache_path):
        fpath = os.path.join(cache_path, fname)
        out, changed = [], 0
        for line in open(fpath, encoding="utf-8"):
            line = line.rstrip("\n")
            if not line:
                out.append(line)
                continue
            try:
                d = json.loads(line)
            except ValueError:
                out.append(line)
                continue
            if d.get("id") in updates_by_id:
                u = updates_by_id[d["id"]]
                d["name"] = u["name"]
                d["folders"] = u.get("folders", d.get("folders", []))
                d["tags"] = u.get("tags", d.get("tags", []))
                d["lastModified"] = now
                out.append(json.dumps(d, ensure_ascii=False, separators=(",", ":")))
                changed += 1
            else:
                out.append(line)
        if changed:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write("\n".join(out))
            print(f"  cache/{fname}: {changed}")


def _rename_media(info_dir, new_name, ext):
    for fname in os.listdir(info_dir):
        if fname.startswith(".") or fname.endswith(".json") or fname.endswith("_thumbnail.png"):
            continue
        stem = fname.rsplit(".", 1)[0]
        old = os.path.join(info_dir, fname)
        new = os.path.join(info_dir, f"{new_name}.{ext}")
        if old != new:
            os.rename(old, new)
        old_thumb = os.path.join(info_dir, f"{stem}_thumbnail.png")
        new_thumb = os.path.join(info_dir, f"{new_name}_thumbnail.png")
        if os.path.exists(old_thumb) and old_thumb != new_thumb:
            os.rename(old_thumb, new_thumb)
        elif not os.path.exists(new_thumb):
            subprocess.run(
                ["sips", "-s", "format", "png", "-Z", "300", new, "--out", new_thumb],
                capture_output=True,
            )
        break


def apply(updates, cfg):
    require_eagle_quit()
    backup(cfg)
    now = now_ms()

    _update_caches({u["id"]: u for u in updates}, cfg, now)

    base = os.path.join(cfg["library_path"], "images")
    for u in updates:
        meta_file = os.path.join(base, f"{u['id']}.info", "metadata.json")
        if not os.path.exists(meta_file):
            print(f"  skip {u['id']}: no local metadata")
            continue
        d = json.load(open(meta_file, encoding="utf-8"))
        ext = d.get("ext", "")
        d["name"] = u["name"]
        d["folders"] = u.get("folders", d.get("folders", []))
        d["tags"] = u.get("tags", d.get("tags", []))
        d["lastModified"] = now
        d.pop("noThumbnail", None)
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        if ext and ext != "url":
            _rename_media(os.path.dirname(meta_file), u["name"], ext)
        print(f"  {u['id']} -> {u['name']}")

    mtime_path = os.path.join(cfg["library_path"], "mtime.json")
    if os.path.exists(mtime_path):
        mt = json.load(open(mtime_path, encoding="utf-8"))
        for u in updates:
            mt[u["id"]] = now
        with open(mtime_path, "w", encoding="utf-8") as f:
            json.dump(mt, f)
    print("done")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        sys.exit("usage: rename_items.py updates.json [--apply]")
    cfg = load_config()
    with open(args[0], encoding="utf-8") as f:
        updates = json.load(f)
    (apply if "--apply" in sys.argv else preview)(updates, cfg)


if __name__ == "__main__":
    main()
