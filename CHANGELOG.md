# Changelog

## 1.0.0 — 2026-11-26

First release. Merges the research and edit sides into one repo, one `brand/`, one install.

**Added**
- `sutra` CLI, standard library only: `doctor, resolve, init, pack, check, spec, gate, loop, library, stats`
- 10 category packs (tutorial, tool-review, faceless-explainer, finance, education, talking-head, story, vlog,
  comedy, gaming) — 60 pack x locale x format combinations, validated in CI
- 3 locales (en, hi, hinglish) that own the whisper model, caption width, caps policy and line height
- 2 formats (long-16x9, portrait-9x16) with post-merge pacing multipliers
- 5 publish gates: hook, pace, mobile, audio (LUFS + true peak), legal (licences)
- `sutra loop`: retention curve → shot kind → rule proposals, with a two-appearance minimum
- provenance on every resolved value (`sutra resolve` shows why each number is what it is)
- hand-written validators, so `git clone` is the entire install
- 21 tests, GitHub Actions on Python 3.10 and 3.12

**Fixed vs the repos it replaces**
- install line pointed at a repo name that does not exist
- `cp -r .claude/skills .agents/skills` failed on a fresh clone (`.agents/` missing) → `make sync`
- `final_check` used an English-only whisper model regardless of language → locale owns the model
- two repos, two `brand/` folders and two duplicated `about-me` skills → merged into one
- no tests, no CI, no releases → all three
