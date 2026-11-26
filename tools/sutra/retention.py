"""The moat: turn your own retention curve into rules. Shot kind in -> retention out."""
import csv, pathlib
from .util import jload, jdump, ok, warn, table

def _load_curve(path):
    rows = []
    with open(path, newline="", encoding="utf8") as f:
        rd = csv.DictReader(f)
        for r in rd:
            t = float(r.get("t_s") or r.get("time_s") or r.get("elapsed"))
            v = float(r.get("retention") or r.get("viewers") or r.get("audience"))
            rows.append((t, v))
    rows.sort()
    if not rows: raise SystemExit("retention csv is empty")
    top = rows[0][1] or 1.0
    return [(t, v / top * 100.0) for t, v in rows]

def _at(curve, t):
    if t <= curve[0][0]: return curve[0][1]
    if t >= curve[-1][0]: return curve[-1][1]
    for (t0, v0), (t1, v1) in zip(curve, curve[1:]):
        if t0 <= t <= t1:
            f = 0 if t1 == t0 else (t - t0) / (t1 - t0)
            return v0 + (v1 - v0) * f
    return curve[-1][1]

def correlate(curve_path, timeline_path, out_md=None, min_appearances=2):
    curve = _load_curve(curve_path); tl = jload(timeline_path)
    shots = tl["shots"]; per = []
    for s in shots:
        t0, t1 = float(s["start_s"]), min(float(s["start_s"]) + 5.0, float(s["end_s"]))
        if t1 - t0 < 0.5: t1 = float(s["end_s"]); t0 = max(0.0, t1 - 0.5)
        r0, r1 = _at(curve, t0), _at(curve, t1)
        per5 = (r1 - r0) / max((t1 - t0) / 5.0, 0.1)
        per.append({"t": round(t0, 1), "kind": s["kind"], "delta_per_5s": round(per5, 2)})
    agg = {}
    for p in per:
        a = agg.setdefault(p["kind"], {"n": 0, "sum": 0.0, "worst": 0.0, "worst_t": 0})
        a["n"] += 1; a["sum"] += p["delta_per_5s"]
        if p["delta_per_5s"] < a["worst"]: a["worst"], a["worst_t"] = p["delta_per_5s"], p["t"]
    rows, proposals = [], []
    for kind, a in sorted(agg.items(), key=lambda kv: kv[1]["sum"] / kv[1]["n"]):
        mean = round(a["sum"] / a["n"], 2)
        verdict = "neutral"
        if mean <= -1.5: verdict = "cut or shorten"
        elif mean >= 0.3: verdict = "keep or expand"
        rows.append((kind, a["n"], mean, f"{a['worst']} @ {a['worst_t']}s", verdict))
        if a["n"] >= min_appearances and verdict != "neutral":
            proposals.append({"kind": kind, "appearances": a["n"], "mean_delta_per_5s": mean,
                              "verdict": verdict, "evidence": f"{a['n']} appearances, mean {mean}% per 5s"})
    md = [f"# Retention loop: {tl.get('video','')}", "",
          f"Curve: `{pathlib.Path(curve_path).name}` · timeline: `{pathlib.Path(timeline_path).name}` · "
          f"{len(shots)} shots · {len(agg)} kinds", "",
          "| kind | appearances | mean delta / 5s | worst | verdict |", "|---|---|---|---|---|"]
    md += [f"| {k} | {n} | {m}% | {w} | {v} |" for k, n, m, w, v in rows]
    md += ["", "## proposed rule changes", ""]
    if proposals:
        for p in proposals:
            md.append(f"- **{p['verdict']} `{p['kind']}`** — {p['evidence']}")
    else:
        md.append("- none: no kind has enough appearances with a clear signal. Keep recording, do not guess.")
    md += ["", "Rules only enter `brand/rules.md` when you say **lock it**. Anything without evidence gets deleted, not defended.", ""]
    if out_md:
        pathlib.Path(out_md).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(out_md).write_text("\n".join(md), encoding="utf8")
    jdump(pathlib.Path(out_md).with_suffix(".json") if out_md else None or pathlib.Path("loop.json"),
          {"video": tl.get("video"), "rows": rows, "proposals": proposals}) if out_md else None
    return rows, proposals, "\n".join(md)
