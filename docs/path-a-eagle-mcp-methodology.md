# Path A — Run the methodology through Eagle's official MCP

> **TL;DR** — Don't reimplement Eagle's file operations. Since Eagle 4.0 Build 12 (Sept 2025) there
> is an **official Eagle MCP server** and an **official Eagle Skill** that already do the mechanics
> safely. The durable value of this project is the *organizing methodology* for product/UI-design
> reference libraries. Path A packages that methodology as a layer on top of Eagle's official tools.

## What Eagle already provides (so we don't rebuild it)

- **Eagle MCP** — a local HTTP MCP server at `http://localhost:41596/mcp`
  (Plugins → Plugin Center → search "MCP" → Install → Enable). Requires Eagle 4.0 Build 12+.
  Connect any agent (Claude Code / Cursor / etc.). Docs:
  <https://en.eagle.cool/support/article/eagle-mcp-server>
- **Eagle Skill** — a lighter, out-of-the-box Skill package you drop into your AI tool's skills
  folder; **explicitly supports Claude Code**, and consumes fewer tokens than MCP (brief description
  + reference files loaded on demand). Docs:
  <https://en.eagle.cool/support/article/eagle-skill>
- Both expose the operations we used to hack by hand: create/rename folders, add/merge/retire tags,
  rewrite names/descriptions, move items, query stats. They also enforce an **"analyze → confirm →
  execute"** SOP, which is exactly the safety net our scripts had to build manually.

**Consequence:** the generic "organize my library" capability is now a commodity Eagle ships for
free. Reimplementing it (or promoting a file-hacking version) competes with the vendor and loses.

## What is still ours (the defensible layer)

Eagle's official Skill is deliberately **generic**. Our differentiator is a **domain-specific
organizing system for product / UI-design reference libraries**:

1. **Naming templates** — `competitor-{feature}-{product}-{detail}`, `inspiration-{feature}-{trait}`,
   `resource-{type}-{name}-{source}`, `work-{yyyymm}-{project}`.
2. **A tag taxonomy with fixed dimensions** — usage / type / platform / (optional) product, with the
   rule "only add a product/source tag when you can confirm it."
3. **A UI-screen → folder map** — Dashboard, Form, List/Feed, Modal, Empty State, Error/Warn, etc.
4. **Heuristics a generic pass won't know:**
   - A walkthrough video is a *flow* → tag `type-flow` and file it under its **starting** screen,
     not under "Animation".
   - Any folder with **> 20 items** is a candidate for a themed subfolder split (5–25 per subfolder).
   - Group by function/theme, never by product or source.
5. **Visual-analysis discipline** — webp/video must be looked at (extract 5 frames from mp4/webm),
   never guessed from filename.

That "taste layer" is what turns Eagle's generic engine into a library a design team can actually
navigate. Eagle provides the hands; we provide the judgment.

## Deliverable shape

A tiny **methodology pack** (not an operations engine):

```
product-design-eagle-methodology/
├── SKILL.md          # the taxonomy + heuristics above, written as instructions that call
│                     #   Eagle MCP / Eagle Skill tools (no file paths, no cache hacking)
├── taxonomy.md       # the naming templates + tag dimensions + screen→folder map (editable)
└── README.md         # "install Eagle MCP (or Eagle Skill) first, then load this on top"
```

Setup for an end user:

1. Install + enable the **Eagle MCP** plugin (or copy the **Eagle Skill** package) — official.
2. Point Claude Code at it.
3. Load this methodology pack so Claude applies *our* naming/tagging/foldering rules when it drives
   Eagle's tools.
4. Always run "output the change list first; execute after confirmation" (Eagle's own SOP).

## Why this beats the file-hacking version

| | File-hack (current repo) | Path A (methodology on official MCP) |
|---|---|---|
| Safety | Must quit Eagle; can corrupt cache | Eagle handles writes safely, live |
| Future-proof | Breaks when Eagle changes disk format | Rides the official, supported API |
| Value | Mechanics (now commoditized) | Domain methodology (still scarce) |
| Effort | Already built | Small — mostly reusing our taxonomy text |

## Open questions before building

- Confirm the exact Eagle MCP tool names/params against the live server (query it once it's
  installed) so `SKILL.md` references them precisely.
- Decide packaging: standalone repo, or a folder inside `eagle-organizer` labelled "MCP edition".
- Decide whether to keep the file-hack version public at all, or fold it into `docs/` as the
  "pre-MCP, reverse-engineered" reference.

## Next step

When ready: install the Eagle MCP plugin, let Claude query it once to capture the real tool surface,
then port `taxonomy.md` from the existing `config.example.json` + `SKILL.md`. Est. small — a few
hours, most of it reusing text we already wrote.
