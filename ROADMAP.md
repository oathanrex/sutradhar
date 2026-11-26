# ROADMAP — an honest self-audit of v1.0

*Written 2026-11-26, the day v1.0 was tagged. Every claim below was checked against the code, not remembered.*

## Verdict: 6 / 10

| dimension | score | why |
|---|---|---|
| Architecture / layering | **8.5** | config → contract → gates is right, and it is why everything is testable without a renderer |
| Config model (packs × locales × formats) | **8.5** | 60 combinations, provenance on every number, multipliers applied post-merge |
| Test + CI discipline | **7.5** | 22 tests, CI on two Python versions, zero-dep guarantee enforced by grep — but only for pure functions |
| Gate honesty | **7.0** | 3 real and tested, 1 needs ffmpeg, 1 needs a render, **1 is a stub** |
| Actual production capability | **4.0** | it validates a plan; it cannot produce a frame. There is no composition builder in the repo |
| Evidence discipline | **4.0** | the exact sin I criticised in other repos: **10/10 packs cite no source videos** |
| Distribution / trust | **3.0** | `git clone` only, no demo render, no install one-liner, no release automation |
| **weighted** | **6.0** | a very good skeleton with a hole in the middle |

**One line:** it is a *QA harness around a plan file*, not yet an editor. Everything it measures is honest;
too much of what it should produce is missing.

---

## What the audit actually found

| # | finding | evidence | severity |
|---|---|---|---|
| 1 | **No renderer bridge.** `sutra` never emits HTML or a composition; the step from `timeline.json` to an MP4 lives outside the repo. | `grep -rln html tools/` → 0 files | **blocker** |
| 2 | **The words gate is a stub.** It prints a hint and returns SKIP, always. "5 gates" is really 3 real + 2 conditional. | `gates.words()` returns SKIP on every path | **high** — it is the headline claim |
| 3 | **Packs have no evidence.** I demanded dated evidence from every rule, then shipped 10 packs of hand-typed numbers with no source. | 10/10 packs lack an `evidence` field | **high** — credibility |
| 4 | **The retention loop needs a manual CSV export.** Zero API integration, while the older `yt.py` had one. A regression against the repo this replaces. | `grep -c 'oauth\|googleapiclient' tools/sutra/` → 0 | **high** — the moat is manual |
| 5 | **Windows was untested** (and it is the majority of this audience). Manifest paths used the OS separator, so a manifest written on Windows only matched a timeline by accident. | found, **fixed and covered by a test** in `c468dd2` | medium |
| 6 | `doctor`, `init`, `util` have no tests. No CLI-surface tests (subprocess), no golden snapshot, no macOS/Windows CI runner. | module coverage table | medium |
| 7 | `style.spec.json` measures a **planned** timeline (durations estimated from 130 wpm), not the real audio. Word-anchoring is designed for but not exercised. | `plan/timeline.json` is plan-level | medium |

---

## Status — v1.1.0 closes P0 and most of P1

| item | status |
|---|---|
| 1. composition builder | **done** (`sutra build`: player + composition + receipt) |
| 2. words gate for real | **done**, tested with an injected transcriber |
| 3. evidence in every pack | **machinery done, data not**: 0/10 measured on purpose, see `docs/EVIDENCE.md` |
| 4. automated retention intake | **done** (`sutra analytics`, device flow + reports API) |
| 5. statistics instead of heuristics | **done** (min 3 uses, bootstrap CI, MAD, materiality threshold) |
| 6. visual gates | **partly**: flash done and tested; legibility is still a heuristic (`visual.frame_spread`) |
| 7. cross-platform CI + CLI tests | **done** (3 OS x 2 Python, 7 CLI subprocess tests) |
| 8. content-hash receipts | **done** (`renders.../receipt.json`) |
| 9-12 (install, demo, locales, Hindi) | open; the demo MP4 landed early (`docs/demo.mp4`) |

**Score after v1.1: 7.5 / 10.** What moved it: the tool can now produce an artifact, the headline gate is real,
and the numbers can no longer be faked. What still holds it back: no pack is measured, HyperFrames compatibility
is asserted rather than verified in CI, and no published video with a retention curve exists yet.

## P0 — this week (turns it into a tool, ~2 days)

**1. The composition builder.** `tools/sutra/build.py` → `timeline.json` → HyperFrames project (one composition
per section, start/end from the timeline, `data-start`/`data-duration` set from the JSON).
- Accept: `sutra build <video> && npx hyperframes render` produces an MP4 with no other glue.
- Accept: the 30s demo renders in CI as an artifact (job is allowed to take 10 minutes).
- This is the single change that moves the score from 6 to 8.

**2. The words gate, for real.** Port the diff logic (re-transcribe the render, `SequenceMatcher` against the
word timings, report each lost word with a timestamp) and make the language come from the locale.
- Accept: a deliberately muted word makes the gate FAIL at the right timestamp, in a test.

**3. Evidence in every pack.** Add `evidence: [{video, views, outlier_x, measured_on}]` and make
`sutra check packs` warn loudly on any pack without it. Mine the 10 categories for 3 videos each = 30 rows.
- Accept: no pack can be added without `evidence`, enforced by a test.

## P1 — this month (makes it a moat, ~1 week)

**4. Automated retention intake.** `sutra auth` (OAuth device flow) + `sutra analytics pull` for
`audienceRetention` and `averageViewDuration`. No CSV pasting. Tokens in `tools/.env`, never committed.
**5. Statistics in the loop, not heuristics.** Replace "2 appearances" with a measured rule: propose only if
`|mean| > 2 × MAD` across appearances and `n ≥ 3`; print the interval. Show "not enough data" more often than
proposals — that is the feature.
**6. Visual gates.** Hook legibility measured in pixels (render the frame at 320 px, measure stroke contrast),
caption overflow measured on the rendered text box, not on character counts, and a flash/3 Hz check for
photosensitivity. All need Pillow + ffmpeg, all degrade to SKIP with the install command.
**7. Cross-platform CI** on `ubuntu / macos / windows` × Python 3.10/3.12, plus a subprocess test for every CLI
command (exit codes, `--json` output).
**8. Content-hash receipts.** Every render writes `renders/<v##>.receipt.json`: timeline hash, asset hashes,
engine version, resolved config hash. "Which inputs produced this MP4" becomes a lookup, not an archaeology dig.

## P2 — this quarter (makes it a product, not a repo)

**9. One-line install.** Publish to PyPI (`uvx sutra`) and a skills registry so `npx skills add <org>/sutradhar`
works. Today it is `git clone` plus three commands — that single friction point loses most non-programmers.
**10. A demo MP4 in the README.** No stranger trusts a 1,000-line engine with zero shipped output. 30 seconds,
rendered by CI, embedded. This is the highest trust-per-minute artifact available.
**11. Two more locales** (Tamil, Bengali) and one more format (1:1 / 4:5 for feed posts). The locale machinery
already exists — this is data, not code.
**12. Hindi quickstart.** The tool is English; the audience that needs it most is not.

---

## What "top 1%" would actually mean here (measurable)

A stranger, on Windows, with no Python knowledge:

- [ ] installs and sees a rendered frame in **under 10 minutes** (today: 40+, and no frame)
- [ ] gets their first full video through **all 5 gates** without messaging anyone
- [ ] can point at **one number in the README that changed because of their own retention data**
- [ ] the repo can prove every pack number came from a named video
- [ ] `make test` covers every decision the CLI makes, on all three OSes
- [ ] a published video exists that was made with it, with a retention curve attached

Six checkboxes. Today: **1.5 of 6.**

## The uncomfortable part

The remaining gap is not code. Two creators can run this identical repo and get wildly different results,
because the tool constrains the editing and cannot supply the taste — what is worth saying, what to cut,
where the joke lands. The engineering ceiling here is roughly "top 5% tooling". The last 5% is earned by
publishing video #1 and showing three retention curves that prove the loop moved a number.

So the order is: **builder → demo MP4 → publish → three curves → then more code.** Building more features before
one published video is the most expensive mistake available right now.
