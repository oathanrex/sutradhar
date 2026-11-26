# Every creator, every category

Two axes decide a config. Both are one command:

```bash
sutra resolve --pack <category> --locale <en|hi|hinglish> --format <long-16x9|portrait-9x16>
```

**Axis 1 — what you make** (10 packs). **Axis 2 — who you are** (6 profiles). Axis 1 changes the numbers;
axis 2 changes the cadence and what you are allowed to ignore for now.

---

## Axis 1 — the 10 categories

| pack | who it is for | cuts/min | max hold | hook must land | #1 killer | the counter-move baked into the pack |
|---|---|---|---|---|---|---|
| `tutorial` | teaching a task someone will do today | 22 | 5.0s | the finished result, on screen | setup too long | `hook` beat = result first, `pitfall` beat forced |
| `tool-review` | tools, apps, AI, hardware | 26 | 4.5s | the price or the surprising claim | reviewing without using it | `proof` beat before `compare`; `require_price_or_free_on_screen` |
| `faceless-explainer` | voiceover essays, no face | 30 | 4.0s | a number or a contradiction | static b-roll under a paragraph | shot mix caps `full` at 16%, forces `flow`/`nodes` |
| `finance` | money, markets, business | 20 | 5.0s | the amount, the loss or the risk | numbers spoken faster than understood | 14 chars/line, `require_disclaimer`, contrast 7:1 |
| `education` | teaching a subject, exam prep | 18 | 6.0s | the exam question | talking over a 40-word slide | `map` beat first, `recall` beat before the summary |
| `talking-head` | opinion, commentary, podcast | 16 | 6.5s | the most arguable true sentence | b-roll covering the face | `objection` beat: state the counter-argument better than the audience could |
| `story` | documentary, narrative, true crime | 14 | 8.0s | the dramatic moment, out of order | too many names and dates up front | `coldopen` beat + one unresolved question per act |
| `vlog` | lifestyle, travel, behind the scenes | 24 | 5.0s | the payoff frame | grocery-list chronology | `turn` beat (something goes wrong) is mandatory |
| `comedy` | sketch, meme, reaction | 45 | 2.2s | the first half of the joke | explaining the joke | `max_silence_ms` 400, 12 chars/line, no setup lines |
| `gaming` | gameplay, esports, highlights | 38 | 3.0s | the play without the outcome | highlight with no stakes | `context` beat forces rank/timer/prize on screen |

Each pack also carries `retention_risks`, `hook_patterns`, `never`, a beat table with target seconds, and a
`shot_mix` that must sum to 1.0 (validated in CI). `sutra pack show <id>` prints all of it.

### Overlays

**Locales** — `en` · `hi` · `hinglish` · `mr` · `ta` · `bn` (full detail and fonts: [LOCALES.md](LOCALES.md))

| | en | hi | hinglish | mr | ta | bn |
|---|---|---|---|---|---|---|
| whisper model | small.en | large-v3 | large-v3 | large-v3 | large-v3 | large-v3 |
| chars / caption line | 42 | 28 | 30 | 30 | 24 | 26 |
| caps allowed | yes | no | no | no | no case | no case |
| line height | 0.92 | 1.08 | 1.06 | 1.08 | 1.10 | 1.14 |
| width budget | 1.0× | 1.18× | 1.12× | 1.16× | 1.32× | 1.28× |

`hinglish` rule that matters: captions are written **exactly as spoken**. `yaar ye kaam nahi karega` stays Roman.
Never transliterate, never translate a product name. Using `small.en` on Hindi audio produces confident garbage —
that is why the locale owns the model name, not the script.

**Formats** — `long-16x9` · `portrait-9x16` · `vertical-4x5` · `square-1x1`. The multiplier applies after every
other layer merges, so a pack never learns it is being rendered vertically: portrait ×0.7 (every shot 30% shorter),
4:5 ×0.8, 1:1 ×0.85, each with its own safe zones and caption size.

---

## Axis 2 — the 6 creator profiles

Pick yours, follow the row, ignore everything else for the first month.

### 1. Beginner solo (first 50 videos)
- **Start**: `tutorial` or `vlog`, `en`, `long-16x9`. One pack, one format, no exceptions.
- **Do now**: `brand` (30 min) → one video end to end through all 5 gates.
- **Ignore for now**: the retention loop (you need ~10 videos first), `shorts`, style spec extraction.
- **Cadence**: 1 video/week. Log every failure in `FIXES.md` — that file is your real product.

### 2. Faceless / voiceover creator
- **Start**: `faceless-explainer`, `long-16x9`. Shot mix caps `full` at 16% — the pack fights static b-roll for you.
- **Do now**: build the `library/` first (screens, gifs, charts). Your bottleneck is media, not code.
- **Ignore**: `rec` placeholders; if you have no footage, plan around screens and diagrams.
- **Cadence**: 2 videos/week is realistic because the edit is 80% template.

### 3. Hindi / Hinglish / Tamil / Bengali creator
- **Start**: any pack, `--locale hi | hinglish | mr | ta | bn`, then `make sync`.
- **Do now**: install a Devanagari font (Baloo Bhai 2 or Mukta), set the font stack with a Latin fallback,
  upgrade the whisper model to `large-v3`. `sutra doctor` checks the font for you.
- **Why this is an advantage**: captions, line heights and transcription are wrong in almost every English-built
  pipeline. Getting them right is immediately visible to the audience — and to clients.
- **Cadence**: same, but budget +20% recording time: Hindi at 120 wpm needs more words for the same duration.

### 4. Brand / company channel
- **Start**: `tool-review` or `tutorial`, brand tokens imported from your existing `design.md`.
- **Do now**: `brand` in import mode (it reads an existing style guide instead of grilling you), then the `legal`
  gate is non-negotiable — every asset needs a licence row, no exceptions.
- **Ignore**: the personal voice work in `about_me/voice.md`; replace with a house style sheet.
- **Cadence**: a shot library is shared across videos; one `library/` at repo root, no per-video assets.

### 5. Editor-for-hire / agency
- **Start**: one repo **per client**, one `brand/` per client, `--pack` per series.
- **Do now**: make the gates your delivery report. Hand the client the gate table — that is the invoice's evidence.
- **Ignore**: nothing. You are the one who cannot afford an unlicensed asset or a clipped true peak.
- **Cadence**: the `loop` skill becomes a billable monthly retention report per client. That is the up-sell.

### 6. Educator / teacher
- **Start**: `education`, `hi` or `en`, both formats (lesson + short revision clip).
- **Do now**: 16 chars/line, 6s max hold, and the `recall` beat — a self-test question before the summary.
- **Ignore**: trend-chasing hook patterns. For exam audiences, the promise of marks beats cleverness.
- **Cadence**: 1 lesson + 3 revision shorts per topic; `shorts` skill reuses the same timeline.

---

## The maturity ladder (what "top 1%" actually means)

| level | you have | verifiable proof | time |
|---|---|---|---|
| **L0 — Template** | brand answers written down | `sutra check brand` clean | 30 min |
| **L1 — Repeatable** | one pack, one format, 2 human gates | 3 videos where `sutra gate` passed first try | 1 week |
| **L2 — Measured** | a real `style.spec.json` extracted from 3 reference videos | `sutra spec verify` PASS on 3 consecutive renders | 2 weeks |
| **L3 — Closed loop** | retention curves flowing into rule changes | a rule locked **and** a rule deleted, both dated with evidence | 1 month |
| **L4 — Compounded** | category-specific numbers per series, shorts automated | the same shot kind measurably improved quarter over quarter | 1 quarter |

Most "AI video editing" content sits at L0 and calls it a workflow. The distance from L0 to L3 is not more
tooling — it is **three numbers and one deletion**.

---

## Adding a category in 10 minutes

```bash
cp packs/tutorial.json packs/<new>.json     # then edit
PYTHONPATH=tools python -m sutra check      # pack must validate (shot_mix sums to 1.0, beats have targets)
PYTHONPATH=tools python -m sutra pack show <new>
```

You need exactly four numbers from **three real videos** in that category — measure, do not estimate:

1. **cuts per minute** (count visible cuts, divide by minutes)
2. **longest shot** (the max hold that still felt fine)
3. **characters on screen** (widest line you can read at 320px wide)
4. **sound effects per minute** (count them)

Then write: who it is for, the six-ish beats with target seconds, the retention risks, three hook patterns, the
Never list, and a one-line `who`. Open a PR with the numbers and the three video ids as evidence.

---

## Anti-patterns (these are what make AI edits look AI)

| pattern | why it fails | what the pack does instead |
|---|---|---|
| one style for all categories | comedy at 16 cuts/min dies, a story at 45 cuts/min is unwatchable | pace belongs to the pack |
| "make it punchy" | not measurable | `cuts_per_min` + `max_hold_s` |
| captions from the wrong model | confident garbage on hi/hinglish audio | locale owns the whisper model |
| b-roll with text on top | two focal points, neither readable | `full` kind forbids text |
| every effect on every cut | no contrast means no emphasis | `sfx_per_min` + one effect at a time |
| cropping for shorts | half a face, no hook | `shorts` re-hooks and re-frames |
| rules that only ever grow | the agent gets slower and vaguer | the `loop` skill deletes losers |
| rendering before the storyboard | 20 minutes wasted per fix | storyboard gate is mandatory |

---

## Weekly operating rhythm

| when | what | command |
|---|---|---|
| every video | plan → script → edit → gate | `sutra init`, `sutra gate` |
| every publish | gate table archived next to the render | `sutra gate > renders/<v>/gates.txt` |
| 7 days after publish | retention curve pulled | export csv, `sutra loop` |
| weekly | one rule locked, one rule deleted | `brand/rules.md` |
| monthly | re-extract the spec from your 3 best videos | `sutra spec extract --from ...` |
| quarterly | re-measure the pack numbers for your niche | see "adding a category" |
