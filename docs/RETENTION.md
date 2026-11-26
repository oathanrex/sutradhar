# The retention loop

## Why this file exists

Without this loop, `sutradhar` is a better prompt. With it, it is a system that gets measurably better every month,
using data no competitor has.

## The math

For each shot, take the retention curve at the shot's start and again 5 seconds later:

```
delta_per_5s = (retention(t+5) − retention(t)) / ((t+5 − t) / 5)      # % per 5 seconds
```

Then aggregate by **shot kind**, not by individual shot:

| kind | uses | mean delta / 5s | worst | verdict |
|---|---|---|---|---|
| gif | 4 | −3.8% | −7.1% @ 2:14 | cut or shorten |
| full | 6 | −0.4% | −1.9% @ 4:02 | neutral |
| screen | 9 | +0.6% | −0.8% @ 1:20 | keep or expand |

Verdict thresholds: `≤ −1.5` → cut or shorten · `≥ +0.3` → keep or expand · anything else → neutral.

A minute of experience tells you why this is more useful than shot-level numbers: one bad GIF is bad luck, four bad
GIFs on average is a **rule**.

## The rule that keeps it honest

> No proposal without at least **two appearances** of that kind. No rule without evidence in `brand/rules.md`.

Small samples lie, and the worst failure mode of this system is you confidently deleting your best visual format
because of one 8-second drop-off. The skill refuses to propose below two appearances, and it says "not enough data"
out loud instead of filling the gap with a guess.

## What a proposal looks like

```
- **cut or shorten `gif`** — 4 appearances, mean -3.8% per 5s, worst -7.1% at 2:14
  smallest test: cap every gif at 2.0s and re-measure next video
```

Note the "smallest test". A proposal is a hypothesis with the cheapest experiment attached, not a rewrite order.

## The part everyone skips: deletion

`brand/rules.md` has three tables: **Locked**, **Proposed**, **Deleted**.

Monthly: any rule that has survived three videos with no positive evidence moves to Deleted with a date and a
reason. This is the highest-value action in the whole system, because an unpruned rules file is how agents get
slower, vaguer and more expensive while feeling more "personalised".

A longer rules file is not a better system. A file where every line has won is.

## Caveats worth repeating

- **Correlation is not causation.** A drop during a GIF may be caused by the sentence before it. The proposal
  format forces you to test the cheapest change first, which mostly protects you from this.
- **Absolute vs relative retention.** Both work; relative is easier to eyeball. The loop normalises to the first
  sample either way.
- **Audio-only viewers, background play and chapters** all bend the curve. Compare videos of the same format and
  length, not a 4-minute short against a 40-minute essay.
- **Never chase the curve into blandness.** If the data says your one original format underperforms, the answer is
  sometimes "that format is what makes this channel worth watching". Write that down as a rule too.

## Cadence

| when | action |
|---|---|
| 7 days after publish | export the curve, run `sutra loop` |
| weekly | lock one rule, delete one rule |
| monthly | compare the same kind across videos — is the trend real? |
| quarterly | re-extract `style.spec.json` from your three best videos; the target moved because you did |
