"""A pack number is only allowed to exist if a named video produced it.

`sutra evidence add --pack tutorial --video <url> --views 214000 --median 48000`
appends a row, computes outlier x = views / channel median, and flips `measured` at 3 rows.
No numbers are ever invented here: you supply the video, the views and the median.
"""
import datetime, pathlib
from .util import ROOT, jload, jdump, ok, warn, table

REQUIRED = ("video", "views", "channel_median", "outlier_x", "measured_on")


def pack_path(pack_id):
    p = ROOT / "packs" / f"{pack_id}.json"
    if not p.exists():
        raise SystemExit(f"unknown pack '{pack_id}'")
    return p


def add(pack_id, video, views, median, date=None):
    p = pack_path(pack_id); d = jload(p)
    if median <= 0:
        raise SystemExit("channel_median must be > 0 (median views of that channel's recent uploads)")
    row = {"video": video, "views": int(views), "channel_median": int(median),
           "outlier_x": round(views / median, 2),
           "measured_on": date or datetime.date.today().isoformat()}
    d.setdefault("evidence", [])
    if any(r["video"] == video for r in d["evidence"]):
        raise SystemExit(f"{video} is already in the evidence for {pack_id}")
    d["evidence"].append(row)
    d["measured"] = bool(d["evidence"])
    jdump(p, d)
    ok(f"{pack_id}: {row['outlier_x']}x outlier from {video} ({len(d['evidence'])}/3 rows)")
    if len(d["evidence"]) < 3:
        warn(f"{3 - len(d['evidence'])} more row(s) before the numbers count as measured")
    return d


def report():
    rows = []
    for f in sorted((ROOT / "packs").glob("*.json")):
        d = jload(f)
        ev = d.get("evidence") or []
        best = max((r["outlier_x"] for r in ev), default=0)
        rows.append((f.stem, "measured" if d.get("measured") else "UNMEASURED", len(ev), best))
    table(rows, ["pack", "state", "rows", "best outlier"], [20, 12, 6, 12])
    bad = sum(1 for r in rows if r[1] != "measured")
    print()
    print(f"  {len(rows) - bad}/{len(rows)} packs measured. Fill the rest: sutra evidence add --pack <id> ...")
    return bad
