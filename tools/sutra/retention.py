"""The moat: turn your own retention curve into rules, with statistics instead of hunches.

Per shot: retention at the shot's start vs 5 seconds later, normalised to % per 5 seconds.
Per kind: mean, median, MAD, and a bootstrapped 95% interval of the mean.

A proposal is only made when all three hold:
  1. at least `min_appearances` uses of that kind (default 3) - two is noise
  2. the 95% interval excludes zero - the direction is not luck
  3. |mean| >= 0.5% per 5s - the effect is big enough to matter

Everything else prints as "not enough data". Refusing to propose is the feature.
"""
import csv, pathlib, random, statistics as st
from .util import jload, jdump

THRESHOLD = 0.5          # % per 5s, below this an effect is not worth a rule


def _load_curve(path):
    rows = []
    with open(path, newline="", encoding="utf8") as f:
        for r in csv.DictReader(f):
            t = float(r.get("t_s") or r.get("time_s") or r.get("elapsed") or 0)
            v = float(r.get("retention") or r.get("viewers") or r.get("audience") or 0)
            rows.append((t, v))
    rows.sort()
    if not rows:
        raise SystemExit("retention csv is empty")
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


def bootstrap_ci(values, iters=2000, seed=7, alpha=0.05):
    """Percentile bootstrap of the mean. Deterministic seed so the same data gives the same report."""
    if len(values) < 2:
        return None, None
    rnd = random.Random(seed)
    means = []
    n = len(values)
    for _ in range(iters):
        means.append(sum(values[rnd.randrange(n)] for _ in range(n)) / n)
    means.sort()
    return round(means[int(iters * alpha / 2)], 2), round(means[int(iters * (1 - alpha / 2)) - 1], 2)


def per_shot(curve, shots):
    out = []
    for s in shots:
        t0 = float(s["start_s"])
        t1 = min(t0 + 5.0, float(s["end_s"]))
        if t1 - t0 < 0.5:
            t1 = float(s["end_s"]); t0 = max(0.0, t1 - 0.5)
        r0, r1 = _at(curve, t0), _at(curve, t1)
        out.append({"t": round(t0, 1), "kind": s["kind"],
                    "delta_per_5s": round((r1 - r0) / max((t1 - t0) / 5.0, 0.1), 2)})
    return out


def aggregate(rows):
    kinds = {}
    for r in rows:
        kinds.setdefault(r["kind"], []).append(r["delta_per_5s"])
    out = []
    for kind, vals in kinds.items():
        lo, hi = bootstrap_ci(vals)
        out.append({"kind": kind, "uses": len(vals),
                    "mean": round(sum(vals) / len(vals), 2),
                    "median": round(st.median(vals), 2),
                    "mad": round(st.median([abs(v - st.median(vals)) for v in vals]), 2),
                    "ci_low": lo, "ci_high": hi,
                    "worst": min(vals), "values": vals})
    out.sort(key=lambda x: x["mean"])
    return out


def decide(agg, min_appearances=3):
    props = []
    for a in agg:
        reason = None
        if a["uses"] < min_appearances:
            reason = f"only {a['uses']} use(s), need {min_appearances}"
        elif a["ci_low"] is not None and a["ci_low"] > 0:
            reason = None
        elif a["ci_high"] is not None and a["ci_high"] < 0:
            reason = None
        else:
            reason = f"95% interval [{a['ci_low']}, {a['ci_high']}] includes zero"
        if reason is None and abs(a["mean"]) < THRESHOLD:
            reason = f"effect {a['mean']}%/5s is below the {THRESHOLD}%/5s threshold"
        if reason:
            a["verdict"], a["why_not"] = "neutral", reason
            continue
        a["verdict"] = "keep or expand" if a["mean"] > 0 else "cut or shorten"
        a["why_not"] = None
        props.append({"kind": a["kind"], "uses": a["uses"], "mean_delta_per_5s": a["mean"],
                      "ci": [a["ci_low"], a["ci_high"]], "verdict": a["verdict"],
                      "evidence": f"{a['uses']} uses, mean {a['mean']}% per 5s, "
                                  f"95% CI [{a['ci_low']}, {a['ci_high']}], MAD {a['mad']}"})
    return props


def correlate(curve_path, timeline_path, out_md=None, min_appearances=3):
    curve = _load_curve(curve_path)
    tl = jload(timeline_path)
    rows = per_shot(curve, tl["shots"])
    agg = aggregate(rows)
    props = decide(agg, min_appearances)

    md = [f"# Retention loop: {tl.get('video', '')}", "",
          f"Curve `{pathlib.Path(curve_path).name}` · timeline `{pathlib.Path(timeline_path).name}` · "
          f"{len(tl['shots'])} shots · {len(agg)} kinds · min {min_appearances} uses per proposal", "",
          "| kind | uses | mean %/5s | 95% CI | MAD | worst | verdict | why not |",
          "|---|---|---|---|---|---|---|---|"]
    for a in agg:
        md.append(f"| {a['kind']} | {a['uses']} | {a['mean']}% | "
                  f"[{a['ci_low']}, {a['ci_high']}] | {a['mad']} | {a['worst']} | {a['verdict']} | "
                  f"{a['why_not'] or '—'} |")
    md += ["", "## proposed rule changes", ""]
    if props:
        for p in props:
            md.append(f"- **{p['verdict']} `{p['kind']}`** — {p['evidence']}")
            md.append(f"  smallest test: change one thing about `{p['kind']}` next video and re-measure")
    else:
        md.append("- **none.** No kind has enough uses with an interval that excludes zero. "
                  "Keep publishing; do not guess a rule from this.")
    md += ["", "Rules only enter `brand/rules.md` when you say **lock it**. "
               "Anything without evidence gets deleted, not defended.", ""]
    text = "\n".join(md)
    if out_md:
        p = pathlib.Path(out_md)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf8")
        jdump(p.with_suffix(".json"), {"video": tl.get("video"), "rows": agg, "proposals": props})
    table_rows = [(a["kind"], a["uses"], f"{a['mean']}%", f"[{a['ci_low']},{a['ci_high']}]",
                   a["verdict"]) for a in agg]
    return table_rows, props, text
