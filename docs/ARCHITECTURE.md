# Architecture

## The one idea

**Separate the thinking from the rendering.** Everything that can be decided or checked before a single frame is
rendered lives in plain JSON and plain Python. The renderer is a replaceable dependency at the edge.

That is why a broken HyperFrames release can never corrupt your production paperwork, and why the whole suite runs
in CI with no GPU, no network and no ffmpeg.

## Layers

```
        ┌──────────────────────────────────────────────────────────┐
        │  skills  (.claude/skills, mirrored to .agents/skills)    │  procedure + contracts
        ├──────────────────────────────────────────────────────────┤
        │  sutra CLI  (tools/sutra, stdlib only)                   │  resolve · check · spec · gate · loop · library
        ├──────────────────────────────────────────────────────────┤
        │  config      brand/ × packs/ × locales/ × formats/        │  data, versioned, validated in CI
        ├──────────────────────────────────────────────────────────┤
        │  timeline.json                                            │  THE CONTRACT between edit and QA
        ├──────────────────────────────────────────────────────────┤
        │  HyperFrames (render) · ffmpeg (loudness) · whisper (words) │  optional, replaceable
        └──────────────────────────────────────────────────────────┘
```

## `timeline.json` is the contract

```json
{"version":"1.0","video":"demo-30s","format":"long-16x9","duration_s":30.0,
 "shots":[{"i":0,"start_s":0.0,"end_s":1.3,"kind":"words","text":["3 TOOLS"]}]}
```

Every measurement in this repo reads this file. Nothing reads the render except the audio gate. Consequences:

- the spec verifier, all five gates and the retention loop work on a **30-line JSON**, not an MP4
- a fix is a diff in JSON, not a re-render
- anyone can review an edit in a pull request
- you can test a whole production system in milliseconds

The edit skill must emit it. If a build script does not, write it first — it is 20 lines and it unlocks everything.

## Config resolution and provenance

`sutra resolve` merges five layers in a fixed order and records where **every leaf value** came from:

```
defaults → brand/design.json → packs/<cat>.json → locales/<locale>.json → formats/<format>.json
```

```bash
sutra resolve --pack comedy --locale hinglish --format portrait-9x16
# "max_hold_s": 1.54,  provenance: "pacing.max_hold_s": "format:portrait-9x16"
```

Why provenance is not optional: the first support question is always *"why is my caption 30 characters?"* and the
answer should be one lookup, not an archaeology session. It also makes conflicts visible — a calm pack plus a fast
format produces a warning, not a silent average.

Format multipliers are applied **after** merging (`portrait` = shot durations × 0.7), so a pack never has to know it
is being rendered vertically.

## Validators are hand-written

`tools/sutra/validate.py` has no `jsonschema` dependency. Tradeoff: ~120 lines to maintain, in exchange for
`git clone` being the entire install. For a tool whose audience includes non-programmers on Windows, that trade is
obviously correct. CI enforces it (`! grep -rn '^import (requests|numpy|PIL|jsonschema|yaml)' tools/sutra`).

## Gates are cheap, loud, and never silent

Each gate returns `PASS | FAIL | SKIP` + a detail string + offenders with timestamps. A missing dependency is a
`SKIP` **with the install command printed**, never a silent pass. A gate that passes on sight is not a gate.

## What belongs where

| you want to change | change this | not this |
|---|---|---|
| pace for one category | `packs/<cat>.json → spec_patch.pacing` | the build script |
| pace for vertical | `formats/portrait-9x16.json → pacing_mult` | every pack |
| caption width for Hindi | `locales/hi.json → caption.max_chars_per_line` | the skill prose |
| your colours | `brand/design.json` | the templates |
| a new check | `tools/sutra/gates.py` + one test | a paragraph in a skill |
| a new category | `packs/<new>.json` + a PR with 3 video ids | a fork |

## Adding a gate

1. write `def mygate(tl, R)` in `gates.py` returning `_res("PASS"|"FAIL"|"SKIP", detail, offenders)`
2. append it to `ALL`
3. add one passing and one failing test in `tests/test_sutra.py`
4. document the threshold in `docs/CATEGORIES.md`

Ten minutes, and it can never regress.

## Deliberate non-goals

- **No renderer.** HyperFrames owns pixels. Owning both would make this unmaintainable in a week.
- **No model calls in the core.** The agent brings the intelligence; this repo brings the constraints.
- **No dashboards.** A table in a terminal prints faster and reads better in a diff.
- **No auto-fix.** The gate reports; the human decides. Automation that "corrects" silently destroys trust in the
  numbers.
