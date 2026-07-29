# Eagle 4.0 on-disk internals (reverse-engineered)

> Reverse-engineered on macOS + Eagle 4.0. Undocumented and version-specific — a future Eagle
> release may change any of this. Verify before trusting it on an irreplaceable library.

## Two sources of truth

Eagle 4.0 reads from **library-caches** on launch and treats each item's `metadata.json` as backup:

- `~/Library/Application Support/Eagle/library-caches/*.txt` — NDJSON, one item per line. Read
  here on startup.
- `{library}/images/{id}.info/metadata.json` — per-item backup. Safe to write **only while Eagle
  is quit**.

## Cache read order matters

The caches directory holds **one complete cache plus smaller incremental caches** (recent changes
only, with ids that overlap the complete one). If you read files in arbitrary order and dedupe by
id, you can "see" an item in a tiny incremental cache first and then skip the rest of the complete
cache — losing most of your items.

**Rule:** read the **largest cache first**, then the rest, deduping by id. `ordered_cache_files()`
implements this by sorting `.txt` files by size, descending. (In the library this was first built
on, the complete cache happened to be one specific file; sorting by size generalizes that to any
library.)

## A single rename touches FIVE places

Miss one and the thumbnail or preview breaks:

1. **Every `library-caches/*.txt`** line containing the item id — update `name` / `folders` /
   `tags` / `lastModified`.
2. **`{id}.info/metadata.json`** — same fields; set `lastModified` to now.
3. **The image file** — `old-name.ext` → `new-name.ext`.
4. **The thumbnail** — `old-name_thumbnail.png` → `new-name_thumbnail.png`.
5. **`{library}/mtime.json`** — set the item's mtime to now.

Extras:

- If metadata has `"noThumbnail": true`, delete that key and regenerate the thumbnail:
  `sips -s format png -Z 300 <image> --out <name>_thumbnail.png`.
- `.url` items have no media file — only metadata needs updating.

## Eagle must be quit before writing

Eagle rewrites metadata live. If it is open while a script writes, the changes are lost or the
cache is corrupted. Every apply path here calls `require_eagle_quit()` first and refuses to run
while the Eagle process is alive.

## Creating subfolders

Add child nodes under a parent in `{library}/metadata.json` (the `folders` tree). Each node needs
`id` / `name` / `description` / `children` / `modificationTime` / `tags` / `iconColor` /
`password` / `passwordTips`. Then move items by replacing the parent id with the new child id in
their `folders` arrays across the caches and each item's metadata. Use unique uppercase ids for new
folders so they never collide with Eagle's own ids.
