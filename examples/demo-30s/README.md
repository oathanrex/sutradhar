# demo-30s — the smallest complete example

```bash
make check     # brand + packs + spec + this timeline
make spec      # measured numbers vs spec, PASS/FAIL per metric
make gates     # 4 PASS, audio SKIP because there is no render in the repo
make stats
```

`plan/timeline.json` is a real, hand-written 30-second edit plan: 12 shots, 22 cuts per minute, first cut at 1.30s,
largest hold 3.5s, no line over 20 characters. It exists so you can inspect **the contract** without downloading
footage or rendering anything.

Media paths point at `library/` (`broll/`, `screens/`, `gifs/`) which ships with licence rows but no binaries —
the originals are the creator's. Add your own files there, run `sutra library index`, and the `legal` gate will
switch from "asset missing" to "asset licensed".

To start your own:

```bash
PYTHONPATH=tools python -m sutra init my-video --pack tool-review --locale hinglish --format portrait-9x16
# then read videos/my-video/plan/brief.md
```
