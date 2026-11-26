<h1 align="center">sutradhar</h1>
<p align="center"><b>One thread from research to retention.</b><br>
Edit video in code with any agent — Claude Code, Antigravity, Codex, Gemini CLI — in your own brand,
for any creator category, with the numbers checked instead of vibes.</p>

<p align="center">
  <a href="https://github.com/oathanrex/sutradhar/actions/workflows/ci.yml"><img src="https://github.com/oathanrex/sutradhar/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Dependencies-0%20(stdlib%20only)-success.svg" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/Tests-57%20passing-brightgreen.svg" alt="57 Tests">
</p>

<p align="center">
  <code>MIT</code> · <code>zero dependencies in the core</code> · <code>57 tests</code> · <code>10 categories × 6 locales × 4 formats = 240</code>
</p>

---

## The problem nobody solves

Every "AI edits your video" setup dies in the same four places:

1. the look is **described** in adjectives, so every render drifts;
2. there is **no measurement**, so nobody knows if the edit was good until the retention curve says so;
3. the agent **asks you for a screenshot** twelve times and the session stalls;
4. the media has **no licence**, so the video cannot be monetised safely.

sutradhar fixes those four, and nothing else. It is deliberately small: 8 skills, 1 CLI, 0 third-party imports.

## What is different here

| | other setups | sutradhar |
|---|---|---|
| The look | a prompt that says "minimal, dark, punchy" | `brand/design.json` + `brand/style.spec.json` — a render is **verified** against numbers |
| Categories | one style, tuned for one channel | **10 category packs × 6 locales × 4 formats = 240 combinations**, all resolved in CI |
| Pace | guessed per video | `cuts_per_min`, `avg_shot_len_s`, `max_hold_s` from the pack, checked by `sutra spec verify` |
| Publish QA | "looks good to me" | **7 gates**: hook, pace, mobile legibility, licence, loudness/true peak, word coverage, flash |
| Output | a promise | `sutra build` -> scrubbable shot sheet + HyperFrames composition + a content-hash receipt |
| Retention | afterthought | `sutra loop` attributes every drop-off to a **shot kind** and proposes rule changes |
| Rules | a growing document | dated rules with evidence; **rules that lose evidence get deleted** |
| Dependencies | npm + python + a magic stack | core is **stdlib only**; ffmpeg/whisper are optional and named when missing |
| Indian languages | English model silently produces garbage, Devanagari matras clip, Tamil words overflow | 5 Indian locales: `hi · hinglish · mr · ta · bn` — whisper `large-v3`, per-script line heights, caps disabled, width budgeted |

## Install

```bash
git clone https://github.com/oathanrex/sutradhar && cd sutradhar
make test          # 57 tests, no network, no ffmpeg, no GPU
make doctor        # tells you exactly what is missing on your machine
```

Using **Claude Code**: open the folder, it reads `CLAUDE.md`, say `build my brand`.
Using **Antigravity / Gemini CLI**: `.agents/skills` is already synced (or run `make sync`), tell it to read `AGENTS.md` first.

As a **plugin** (Claude Code): `/plugin marketplace add oathanrex/sutradhar` then install `sutradhar` from it —
the manifest lives in `.claude-plugin/`. As a **CLI**: `pipx install .` gives you `sutra` on PATH.

The rendering engine is [HyperFrames](https://github.com/heygen-com/hyperframes) (Apache-2.0, free, HTML → MP4,
`npx hyperframes`). This repo never installs it for you — it writes the project and the timeline HyperFrames
renders. Install it from its own source and pin the version in `examples/demo-30s/project/package.json`.

## 60 seconds of proof

```bash
make preview   # render docs/demo.mp4 and run the render-dependent gates on it
make check     # brand + 10 packs + spec + demo timeline: all clear
make spec      # measured numbers vs spec, PASS/FAIL per metric
make gates     # hook PASS 1.30s · pace PASS · mobile PASS 20 chars 17.4:1 · legal PASS 4 assets · audio SKIP (no render)
make matrix    # 240 pack x locale x format combinations resolved, 0 problems
```

Everything above runs with no network and no ffmpeg. That is the point: **the thinking is testable without the
renderer**, so a broken HyperFrames release cannot silently ruin your paperwork.

## The loop

```
research ──► plan (pack × locale × format) ──► script ──► timeline.json ──► storyboard ✋ ──► render
                                                              │                              │
                                                              ▼                              ▼
                                                    spec verify + 7 gates ◄──────────────  gate ✋
                                                              │
                                    analytics curve ──► sutra loop ──► rules locked or deleted ──┐
                                                              ▲                                    │
                                                              └────────────── next video ◄─────────┘
```

Two human gates per video: **storyboard** before render, **gate review** before publish. Nothing else needs you.

## Skills (8, not 15)

| skill | you say | it produces |
|---|---|---|
| `brand` | "build my brand" | `design.json`, `style.spec.json`, `rules.md`, `about_me/` |
| `plan` | "new video about X" | pack × locale × format, beat table, asset list |
| `research` | a link / "why did this blow up" | evidence table with timestamps + outlier × |
| `script` | "write the script" | a script that fits the beats and your voice |
| `edit` | "edit this" | `timeline.json`, storyboard, render, receipt, changelog |
| `gate` | "is it ready" | 7 PASS/FAIL/SKIP rows with offending timestamps |
| `loop` | "why do people leave" | drop-off → shot kind → rule proposals |
| `shorts` | "make shorts" | self-contained 9:16 cuts, re-hooked, re-gated |

Each skill is a contract: inputs, steps, and a **"done when"** checklist. A skill that cannot be verified did not
finish.

## Categories

`tools-review` is not `comedy`, and pretending otherwise is why generic AI edits look generic.

| pack | cuts/min | max hold | #1 killer |
|---|---|---|---|
| tutorial | 22 | 5.0s | setup too long |
| tool-review | 26 | 4.5s | reviewing without using it |
| faceless-explainer | 30 | 4.0s | static b-roll under a paragraph |
| finance | 20 | 5.0s | numbers read faster than they can be understood |
| education | 18 | 6.0s | talking over a 40-word slide |
| talking-head | 16 | 6.5s | b-roll covering the face too long |
| story | 14 | 8.0s | too many names and dates up front |
| vlog | 24 | 5.0s | grocery-list chronology |
| comedy | 45 | 2.2s | explaining the joke |
| gaming | 38 | 3.0s | highlight with no stakes |

Locales: `en · hi · hinglish · mr · ta · bn`. Formats: `long-16x9 · portrait-9x16 · vertical-4x5 · square-1x1`.
Why a language is a config and not a translation: [docs/LOCALES.md](docs/LOCALES.md). Category plan:
[docs/CATEGORIES.md](docs/CATEGORIES.md). Hindi quickstart: [docs/QUICKSTART-hi.md](docs/QUICKSTART-hi.md).
for the full plan — including the six **creator profiles** and the four **maturity levels**.

## First video, end to end

`docs/ANTIGRAVITY.md` is the full Antigravity runbook (setup, prompt patterns, free-tier reality, troubleshooting).
The sequence is always the same:

```
brand (once) -> plan -> research -> script -> timeline -> storyboard STOP -> render -> 5 gates STOP -> publish
                                                                                       |
                                              7 days later: retention curve -> loop -> lock 1 rule, delete 1
```

Two stop signs. Everything else the agent should finish without asking you.

## Watch it before installing anything

[![the 30 second demo render](docs/demo-poster.png)](docs/demo.mp4)

`docs/demo.mp4` is a real 30-second render of `examples/demo-30s`: same timeline, same brand, same gates.
It is a shot-sheet preview, not a HyperFrames render, and it says so in the file. Regenerate it with
`make preview`; the gate run that proves it is in CI.

## Honest limits

- It does not make you funny, right, or worth watching. It makes your taste **repeatable and measurable**.
- Retention correlation is a signal, not a proof. Small samples lie; the skill refuses to propose a rule on
  fewer than two appearances for that reason.
- The audio gate skips if ffmpeg is missing, and the words gate skips without `faster-whisper`. Skips are always
  printed — a silent skip is a lie.
- Writing a shot still needs a human decision about what is on screen. Nothing here removes that.

## Self-audit

`ROADMAP.md` is an honest audit of v1.0, written the day it was tagged: a 6/10 with the exact gaps named,
and the priority order that fixes them. Read it before trusting the README.

## Credits

- [HyperFrames](https://github.com/heygen-com/hyperframes) — HTML → MP4 engine, skills, `frame.md`, block registry.
- [Matt Pocock's skills](https://github.com/mattpocock/skills) — the grilling pattern this repo's `brand` skill owes
  its question style to.
- The original `ytb-edit-kit` / `ytb-research-skills` ideas (word-anchored timing, storyboard-first, self-check)
  which this repo merges into one system.

MIT.
