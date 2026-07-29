"""Split an oversized folder into subfolders and reassign items.

Dry-run by default; --apply to write.

    python3 scripts/subfolder_split.py split.json          # preview
    python3 scripts/subfolder_split.py split.json --apply   # write, after backup

split.json format (see examples/split.example.json):
{
  "parent_id": "PARENTID",
  "new_folders": [{"id": "NEWID", "name": "Sub A", "description": "note"}],
  "item_map": {"ITEMID": "NEWID"}
}
"""
import json
import os
import sys

from eagle_common import (
    backup,
    load_config,
    now_ms,
    ordered_cache_files,
    require_eagle_quit,
)


def preview(spec, cfg):
    new_folders = spec.get("new_folders", [])
    item_map = spec.get("item_map", {})
    print(f"DRY-RUN — {len(new_folders)} new folder(s), {len(item_map)} move(s). "
          f"Add --apply to write.\n")
    for f in new_folders:
        print(f"  + folder {f['name']} ({f['id']}): {f.get('description', '')}")
    for iid, fid in item_map.items():
        print(f"    {iid} -> {fid}")


def _add_children(folders, parent_id, new_children, now):
    for f in folders:
        if f.get("id") == parent_id:
            existing = {c["id"] for c in f.get("children", [])}
            for nc in new_children:
                if nc["id"] not in existing:
                    f.setdefault("children", []).append({
                        "id": nc["id"],
                        "name": nc["name"],
                        "description": nc.get("description", ""),
                        "children": [],
                        "modificationTime": now,
                        "tags": [],
                        "iconColor": "",
                        "password": "",
                        "passwordTips": "",
                    })
            f["modificationTime"] = now
            return True
        if _add_children(f.get("children", []), parent_id, new_children, now):
            return True
    return False


def _move_in_caches(item_map, parent, cfg, now):
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
            iid = d.get("id")
            if iid in item_map and parent in d.get("folders", []):
                new_fid = item_map[iid]
                d["folders"] = [new_fid if x == parent else x for x in d["folders"]]
                d["lastModified"] = now
                out.append(json.dumps(d, ensure_ascii=False, separators=(",", ":")))
                changed += 1
            else:
                out.append(line)
        if changed:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write("\n".join(out))
            print(f"  cache/{fname}: {changed}")


def apply(spec, cfg):
    require_eagle_quit()
    backup(cfg)
    now = now_ms()
    parent = spec["parent_id"]
    item_map = spec.get("item_map", {})

    meta_path = os.path.join(cfg["library_path"], "metadata.json")
    meta = json.load(open(meta_path, encoding="utf-8"))
    _add_children(meta.get("folders", []), parent, spec.get("new_folders", []), now)
    meta["modificationTime"] = now
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"  + {len(spec.get('new_folders', []))} subfolder(s)")

    _move_in_caches(item_map, parent, cfg, now)

    base = os.path.join(cfg["library_path"], "images")
    for iid, new_fid in item_map.items():
        mf = os.path.join(base, f"{iid}.info", "metadata.json")
        if not os.path.exists(mf):
            continue
        d = json.load(open(mf, encoding="utf-8"))
        if parent in d.get("folders", []):
            d["folders"] = [new_fid if x == parent else x for x in d["folders"]]
            d["lastModified"] = now
            with open(mf, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)

    mtime_path = os.path.join(cfg["library_path"], "mtime.json")
    if os.path.exists(mtime_path):
        mt = json.load(open(mtime_path, encoding="utf-8"))
        for iid in item_map:
            mt[iid] = now
        with open(mtime_path, "w", encoding="utf-8") as f:
            json.dump(mt, f)
    print("done")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        sys.exit("usage: subfolder_split.py split.json [--apply]")
    cfg = load_config()
    with open(args[0], encoding="utf-8") as f:
        spec = json.load(f)
    (apply if "--apply" in sys.argv else preview)(spec, cfg)


if __name__ == "__main__":
    main()
