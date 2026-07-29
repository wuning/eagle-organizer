---
name: eagle-organizer
description: Organize an Eagle 4.0 asset library — analyze items visually, suggest consistent names/tags/folders, and safely apply the changes via dry-run-first scripts. Use when the user wants to rename, tag, sort, or split folders in their Eagle library.
---

# Eagle Organizer

A skill for tidying an [Eagle](https://eagle.cool) 4.0 asset library. It visually analyzes your
images and videos, proposes a consistent naming + tagging + folder scheme, and applies the changes
through safe, dry-run-first scripts.

Your own taxonomy (library path, folder IDs, tag vocabulary, naming templates) lives in
`config.json` — copy `config.example.json` to `config.json` and fill it in once. This skill file
contains no library-specific data, so it works for any Eagle 4.0 library.

> ⚠️ These scripts rewrite Eagle's internal cache and metadata. **Always** keep the default dry-run
> for your first pass, fully quit Eagle (Cmd+Q) before applying, and let the scripts make their
> automatic backup. Read `README.md` and `docs/eagle-4.0-internals.md` before your first real run.

## Setup (once)

1. `cp config.example.json config.json`
2. Set `library_path` to your `.library` folder.
3. Generate your folder map: `python3 scripts/discover_folders.py` → paste the printed `folders`
   block into `config.json`.
4. Adjust the `tags` and `naming` sections to your own vocabulary.

## Modes (auto-detected)

**Mode A — Dropped files.** Images/videos attached in chat → visually analyze each, output a
suggestion table.

**Mode B — Folder cleanup.** A folder is named (e.g. "organize the App folder") → read every
item's metadata, infer from name/url/tags, output a suggestion table. Videos (mp4/webm) and webp
**must** be visually analyzed, never guessed from filename.

**Mode C — Subfolder evaluation.** "Which folders need subfolders?" → count items per folder; any
folder with **more than 20 items** gets a subfolder-split proposal grouped by theme.

All three modes share the same naming rules, tag system, and scripts.

## Visual analysis rules

- **webp**: Read the file directly and analyze the frame.
- **mp4 / webm**: extract 5 evenly-spaced frames with ffmpeg, then analyze each:
  ```bash
  TMPDIR=$(mktemp -d); ID="ITEM_ID"; MP4="path/$ID.info/clip.mp4"
  DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$MP4")
  INTERVAL=$(python3 -c "d=float('$DUR'); print(max(1, int(d/5)))")
  ffmpeg -i "$MP4" -vf "fps=1/$INTERVAL" -frames:v 5 "$TMPDIR/${ID}_%02d.jpg" -y -loglevel quiet
  ```
  Then judge: screen type, product, flow start + intermediate screens. A clip that walks through
  multiple screens is a *flow* — tag it `type-flow` and file it under its **starting** screen.

## Naming

Templates live in `config.json → naming`. Defaults:

| Kind | Template | Example |
|------|----------|---------|
| Competitor screenshot | `competitor-{feature}-{product}-{detail}` | `competitor-deposit-acme-usdc` |
| Inspiration | `inspiration-{feature}-{trait}` | `inspiration-onboarding-gradient-motion` |
| Design resource | `resource-{type}-{name}-{source}` | `resource-illustration-brooklyn-streamline` |
| Own work | `work-{yyyymm}-{project}` | `work-2406-redesign` |

## Tags

Tags follow a `group-value` shape and live in `config.json → tags`. Example groups: `usage`,
`type`, `platform`. Only add a product/source tag when you can confirm the source; when unsure,
leave it off.

## Folder classification

Map each screen type to a folder from your library (IDs in `config.json → folders`). A neutral
example set: Navigation, Landing Page, Onboarding, Sign Up / Login, Dashboard, Card, List / Feed,
Table, Form, Search & Filter, Settings, Profile, Modal / Dialog, Toast / Notify, Empty State,
Loading / Skeleton, Error / Warn, Email, Prototype / Flow.

If nothing fits, propose a new folder (keep your `NN-Name` numbering) in the suggestion table.

## Applying changes

1. Present the suggestion table and **wait for confirmation**.
2. Remind the user to fully quit Eagle (Cmd+Q).
3. Run the script in dry-run first (default), review, then re-run with `--apply`.

```bash
python3 scripts/rename_items.py updates.json           # dry-run preview
python3 scripts/rename_items.py updates.json --apply    # writes, after backup
python3 scripts/subfolder_split.py split.json --apply
```

Input file formats are documented at the top of each script and in `examples/`. See
`docs/eagle-4.0-internals.md` for exactly what each script touches and why.
