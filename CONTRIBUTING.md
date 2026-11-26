# Contributing

The bar is the same for every change: **could CI prove it?**

## Ground rules
1. **No third-party imports in `tools/sutra/`.** The core stays stdlib. Optional extras live behind a try/except and
   must degrade to a `SKIP` with the install command printed.
2. **Every new check needs two tests** — one that passes, one that fails. A gate without a failing test is a wish.
3. **Every new number needs evidence.** If a pack claims 26 cuts per minute, the PR links three real videos.
4. **English, short sentences, no marketing.** The reader is a tired editor at 1am.
5. **Never edit `CLAUDE.md` or `GEMINI.md` directly** — they are mirrors of `AGENTS.md`. CI diffs them.

## Adding a category pack
Four measured numbers from three videos in that category: cuts/min, longest comfortable shot, max characters on
screen readable at 320px, sound effects per minute. Plus: who it is for, beats with target seconds, retention risks,
three hook patterns, the Never list, a `shot_mix` that sums to 1.0.

```bash
cp packs/tutorial.json packs/<new>.json
PYTHONPATH=tools python -m sutra check          # must be clean
PYTHONPATH=tools python scripts/matrix.py       # 60 -> 63 combinations still resolve
```

## Before opening a PR
```bash
make test && make check && make matrix && make gates
```
All four green, or the PR explains which one cannot be and why.

## Commit messages
`area: what changed and why` — e.g. `gates: fail the legal gate when licence is empty`. The "why" is the part that
gets read in two years.
