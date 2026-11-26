# analytics/

One CSV per published video. `sutra loop` turns them into rule proposals.

```
analytics/2026-11-20-antigravity.csv    t_s,retention   (or t_s,viewers - it normalises)
```

Export from YouTube Studio → Analytics → Audience retention → show `t_s,retention` every 2 seconds. Seven days
after publish is enough signal; three videos is enough to trust a pattern.

```bash
sutra loop analytics/2026-11-20-*.csv --timeline videos/<name>/plan/timeline.json --out analytics/<name>_loop.md
```

`analytics/*.csv` is gitignored except the example, because your retention curve is your data, not the repo's.
