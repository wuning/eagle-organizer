# The Organizing System

**English** · [繁體中文](METHODOLOGY.zh-TW.md)

An opinionated methodology for organizing a **product / UX design reference library** — the
judgment layer that a generic "tidy my library" pass can't give you.

> Eagle now ships an official [AI feature](https://en.eagle.cool/blog/post/eagle-plugin-mcp-skill)
> that renames, tags, and sorts your library through a safe API — for most people, that's the tool
> to use. But a tool *executes*; it doesn't decide what "organized" should mean **for your work**.
> This document is that decision. Run it with the bundled scripts, or **paste the preset below into
> Eagle's official AI** and give it your taste.

## The premise

Organizing isn't archiving. It's a design problem: **you first decide how a thing *should* be
found.** That's the same skill you use for navigation, IA, and search filters — pointed at your own
files instead of a product.

## Three rules

### 1. Naming is predicting how future-you will search

Not "what is this?" but "what will I type when I want it back?" So lock names into a few sentence
patterns — the *same kind of thing always uses the same pattern*:

| Kind | Pattern | Example |
|---|---|---|
| Competitor | `competitor-{feature}-{product}-{detail}` | `competitor-deposit-productA-creditcard` |
| Inspiration | `inspiration-{feature}-{trait}` | `inspiration-onboarding-gradient-motion` |
| Resource | `resource-{type}-{name}-{source}` | `resource-icon-weather-set-figma` |
| Your own work | `work-{yyyymm}-{project}` | `work-202607-projectX` |

The point isn't pretty formatting. It's that six months later you don't have to remember the
filename — only what you were thinking.

### 2. Tags are dimensions, not decoration

More tags ≠ better. Fix a few axes and stay inside them:

- **usage** — `reference` · `competitor-research` · `design-resource` · `inspiration` · `work-screenshot`
- **type** — `screenshot` · `animation` · `illustration` · `icon` · `vector` · `logo` · `banner` · `dataviz` · `flow`
- **platform** — `app` · `web` · `webapp`

One discipline I never break: **if you're unsure of the product / source, leave it untagged.** A
wrong tag is worse than no tag — it lies to future-you.

### 3. Folders by screen function, not by product

Dashboard, form, list, modal, empty state, error page… The axis a UI designer actually reaches for
is *"what kind of screen is this,"* not *"which app is it from."* Number them so they sort:

`05-Dashboard` · `07-List-Feed` · `09-Form` · …

## Two judgments no generic tool will make

**1. A flow recording is filed under its *starting screen*, not under "animation."** When you go
looking for "how others design a withdrawal flow," you search from the *withdrawal* feature — not
from "this is a moving video." Format is not the axis; **intent is.**

**2. Any folder over ~20 items should split into themed subfolders.** A folder you have to scroll
three pages through is not organized. Split by theme, aim for 5–25 items per subfolder — anything
smaller isn't worth its own folder.

## Use it *with* Eagle's official AI

This system is portable. Paste the preset below into the official
[Eagle MCP / Eagle Skill](https://en.eagle.cool/support/article/eagle-mcp-server) (works with
Claude Code, Cursor, and others). It encodes the taxonomy above and runs dry-run first:

```text
You are organizing a product/UX design reference library. Follow this system exactly.

Naming (same kind of thing → same pattern):
- competitor:  competitor-{feature}-{product}-{detail}
- inspiration: inspiration-{feature}-{trait}
- resource:    resource-{type}-{name}-{source}
- my work:     work-{yyyymm}-{project}

Tags — use only these axes; if the product/source is uncertain, leave it untagged:
- usage:    reference | competitor-research | design-resource | inspiration | work-screenshot
- type:     screenshot | animation | illustration | icon | vector | logo | banner | dataviz | flow
- platform: app | web | webapp

Folders — by SCREEN FUNCTION, not by product (dashboard, form, list, modal, empty state, error…).
Special rules:
- A flow / screen recording is filed under its STARTING SCREEN's feature, never under "animation."
- Any folder over 20 items: propose themed subfolders of 5–25 items each.

First output a change list (current name → proposed name / tags / folder) and wait for my
confirmation. Do not modify anything until I approve.
```

## Why this is the part that lasts

Execution is becoming nearly free. What a generic AI commoditizes is the *process* — renaming,
moving, tagging. What it can't commoditize is **this**: what your library should look like, for the
way *you* work. Tools will keep changing. "Organizing is a design judgment" won't expire.
