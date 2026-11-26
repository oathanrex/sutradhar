"""CI proof: every pack x locale x format resolves and validates. 60 combinations, no network."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from sutra.resolve import resolve
from sutra import validate
import json

ROOT = pathlib.Path(__file__).resolve().parents[1]
packs = sorted(p.stem for p in (ROOT / "packs").glob("*.json"))
locales = sorted(p.stem for p in (ROOT / "locales").glob("*.json"))
formats = sorted(p.stem for p in (ROOT / "formats").glob("*.json"))
bad = 0; n = 0
for pack in packs:
    for loc in locales:
        for fmt in formats:
            n += 1
            try:
                R = resolve(pack, loc, fmt)
                assert R.get("pacing.cuts_per_min") > 0
                assert R.get("pacing.max_hold_s") > 0
                assert 8 <= R.get("text.max_chars_per_line") <= 60
                assert R.get("safe.top_pct") < R.get("safe.bottom_pct")
                json.dumps(R.as_dict())  # must serialise for the build step
            except Exception as e:
                bad += 1; print(f"  FAIL {pack}/{loc}/{fmt}: {e}")
for p in sorted((ROOT / "packs").glob("*.json")):
    errs = validate.pack(json.loads(p.read_text()))
    if errs: bad += len(errs); [print(f"  FAIL {p.name}: {e}") for e in errs]
print(f"  {n} pack x locale x format combinations resolved, {len(packs)} packs validated, {bad} problem(s)")
sys.exit(1 if bad else 0)
