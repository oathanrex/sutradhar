# FIXES.md — the pain log

Every time you get stuck for more than 5 minutes, write one line here. This file is not documentation; it is the
raw material for your next video, your next README fix, and the reason v1.1 exists.

Format: `YYYY-MM-DD · where · what happened · what actually fixed it · was it my fault or the tool's?`

## Open

| date | where | symptom | real fix | whose fault |
|---|---|---|---|---|
| | | | | |

## Fixed in the repo already (kept for the record)

| date | symptom | fix |
|---|---|---|
| 2026-11-26 | `cp -r .claude/skills .agents/skills` failed on a fresh clone | `make sync` creates `.agents/` first |
| 2026-11-26 | install line pointed at a repo name that does not exist | corrected clone URL |
| 2026-11-26 | Hindi audio transcribed with an English-only model | locale owns the whisper model (large-v3) |
| 2026-11-26 | two repos, two `brand/` folders, duplicated `about-me` skill | merged into one repo, one brand |

## Rules
1. A fix that is not written here did not happen — you will hit it again next video.
2. If the same fix is needed twice, it becomes a gate or a test, not a note.
3. If a whole category of pain shows up (e.g. "machine can't find fonts"), it becomes a `sutra doctor` check.
