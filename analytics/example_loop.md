# Retention loop: demo-30s

Curve: `example_retention.csv` · timeline: `timeline.json` · 12 shots · 5 kinds

| kind | appearances | mean delta / 5s | worst | verdict |
|---|---|---|---|---|
| gif | 1 | -20.1% | -20.1 @ 14.0s | cut or shorten |
| chips | 1 | -9.5% | -9.5 @ 11.5s | cut or shorten |
| full | 3 | -3.64% | -7.71 @ 26.5s | cut or shorten |
| screen | 3 | -1.91% | -3.9 @ 9.0s | cut or shorten |
| words | 4 | -0.9% | -2.6 @ 24.0s | neutral |

## proposed rule changes

- **cut or shorten `full`** — 3 appearances, mean -3.64% per 5s
- **cut or shorten `screen`** — 3 appearances, mean -1.91% per 5s

Rules only enter `brand/rules.md` when you say **lock it**. Anything without evidence gets deleted, not defended.
