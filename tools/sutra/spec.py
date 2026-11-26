"""Measure a timeline, then check it against brand/style.spec.json.
The point: 'copy this style' becomes a number you can pass or fail."""
from . import kinds as K
from .util import table

MEASURABLE = {
    "pacing.cuts_per_min": ("pacing", "cuts_per_min", 0.25, "abs"),
    "pacing.avg_shot_len_s": ("pacing", "avg_shot_len_s", 0.25, "abs"),
    "pacing.max_hold_s": ("pacing", "max_hold_s", 0.0, "max"),
    "text.max_chars_per_line": ("text", "max_chars_per_line", 0.0, "max"),
    "audio.sfx_per_min": ("audio", "sfx_per_min", 0.40, "abs"),
}

def _text_words(shot):
    return [w for line in (shot.get("text") or []) for w in str(line).split()]

def stats(tl):
    shots = tl["shots"]; dur = float(tl["duration_s"]); n = len(shots)
    lengths = [s["end_s"] - s["start_s"] for s in shots]
    with_text = [s for s in shots if s.get("text")]
    sfx = [s for s in shots if s.get("sfx")]
    mix = {}
    for s in shots: mix[s["kind"]] = mix.get(s["kind"], 0) + 1
    return {
        "shots": n,
        "duration_s": round(dur, 2),
        "cuts_per_min": round((n - 1) / dur * 60, 1) if dur else 0,
        "avg_shot_len_s": round(dur / n, 2) if n else 0,
        "max_hold_s": round(max(lengths), 2) if lengths else 0,
        "first_cut_s": round(shots[0]["end_s"], 2) if n > 1 else round(dur, 2),
        "sfx_per_min": round(len(sfx) / dur * 60, 1) if dur else 0,
        "text_shots_pct": round(len(with_text) / n * 100, 1) if n else 0,
        "words_on_screen_per_shot": round(sum(len(_text_words(s)) for s in with_text) / len(with_text), 2) if with_text else 0,
        "max_chars_per_line": max([max((len(str(l)) for l in s.get("text") or [""]), default=0) for s in shots] or [0]),
        "shot_mix": {k: round(v / n, 3) for k, v in sorted(mix.items(), key=lambda x: -x[1])},
    }

def verify(spec, tl):
    """Returns (rows, failures). rows = (metric, spec_value, measured, verdict)."""
    if not spec:
        return [], ["no brand/style.spec.json: nothing to verify against. Run 'sutra spec extract' first."]
    st = stats(tl); rows = []; fails = []
    ev = spec.get("evidence", {})
    for path, (sec, key, tol, mode) in MEASURABLE.items():
        want = (spec.get(sec) or {}).get(key)
        if want is None: continue
        got = st.get(key, 0)
        if mode == "max":
            passed = got <= want * (1 + 0.02)
            delta = f"{'+' if got > want else ''}{round(got - want, 2)}"
        else:
            passed = abs(got - want) <= max(want * tol, 0.01)
            delta = f"{'+' if got >= want else ''}{round((got - want) / (want or 1) * 100, 1)}%"
        verdict = "PASS" if passed else "FAIL"
        if not passed: fails.append(f"{path}: spec {want} vs measured {got} ({delta})")
        rows.append((path, want, got, delta, verdict, "cited" if path in ev else "NO EVIDENCE"))
    return rows, fails

def extract_from_playlist(paths, brand_spec=None):
    """Build style.spec.json from measured timelines of reference videos.
    Video files are never redistributed: only counts are stored."""
    import statistics as st
    acc = {"cuts": [], "avg": [], "max": [], "sfx": [], "chars": []}
    for p in paths:
        from .util import jload
        tl = jload(p)
        s = stats(tl)
        acc["cuts"].append(s["cuts_per_min"]); acc["avg"].append(s["avg_shot_len_s"])
        acc["max"].append(s["max_hold_s"]); acc["sfx"].append(s["sfx_per_min"])
        acc["chars"].append(s["max_chars_per_line"])
    med = lambda xs: round(st.median(xs), 2) if xs else 0
    return {
        "version": "1.0",
        "measured_from": [str(p) for p in paths],
        "evidence": {f"pacing.cuts_per_min": f"median of {len(paths)} timelines",
                     f"audio.sfx_per_min": f"median of {len(paths)} timelines"},
        "pacing": {"cuts_per_min": med(acc["cuts"]), "avg_shot_len_s": med(acc["avg"]), "max_hold_s": med(acc["max"])},
        "text": {"max_chars_per_line": int(med(acc["chars"]) or 18)},
        "audio": {"sfx_per_min": med(acc["sfx"])},
    }
