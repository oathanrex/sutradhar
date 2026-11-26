"""Hand-written validators. No jsonschema dependency, so `git clone` is the only install step."""
from . import kinds as K
from .util import contrast

def _req(obj, keys, where, errors):
    for k in keys:
        if k not in obj or obj[k] in (None, ""):
            errors.append(f"{where}: missing required key '{k}'")

def design(d):
    e = []
    _req(d, ["background", "text", "accent", "font_title", "font_body", "max_hold"], "design.json", e)
    if e: return e
    for k in ("background", "text", "accent"):
        if not str(d[k]).startswith("#"):
            e.append(f"design.json: '{k}' must be a hex colour like #111111")
    if not e:
        c = contrast(d["background"], d["text"])
        if c < 4.5:
            e.append(f"design.json: text/background contrast is {c}:1, needs 4.5:1 minimum")
    a = contrast(d["background"], d["accent"])
    if a < 3.0:
        e.append(f"design.json: accent/background contrast is {a}:1, needs 3:1 for on-screen type")
    if not isinstance(d.get("max_hold"), (int, float)) or not (1.0 <= d["max_hold"] <= 12.0):
        e.append("design.json: max_hold must be a number between 1 and 12 seconds")
    return e

def spec(s):
    e = []
    for sec, keys in {
        "pacing": ["cuts_per_min", "avg_shot_len_s", "max_hold_s"],
        "text": ["max_chars_per_line"],
        "audio": ["sfx_per_min"],
    }.items():
        if sec not in s: e.append(f"style.spec.json: missing section '{sec}'"); continue
        _req(s[sec], keys, f"style.spec.json > {sec}", e)
    if "evidence" not in s:
        e.append("style.spec.json: missing 'evidence' - every number must cite the observation it came from")
    if not e:
        p = s["pacing"]
        if p["avg_shot_len_s"] > p["max_hold_s"]:
            e.append("style.spec.json: avg_shot_len_s cannot exceed max_hold_s")
        if not (5 <= p["cuts_per_min"] <= 90):
            e.append("style.spec.json: cuts_per_min outside 5..90, measure again")
    return e

def pack(p):
    e = []
    _req(p, ["id", "name", "spec_patch", "structure", "shot_mix", "gate"], "pack", e)
    if e: return e
    bad = K.check(p["shot_mix"].keys())
    if bad: e.append(f"pack {p['id']}: unknown shot kinds {bad}")
    tot = sum(p["shot_mix"].values())
    if abs(tot - 1.0) > 0.06:
        e.append(f"pack {p['id']}: shot_mix sums to {round(tot,3)}, must be ~1.0")
    if not p["structure"]:
        e.append(f"pack {p['id']}: structure is empty")
    for b in p["structure"]:
        _req(b, ["beat", "start_s", "target_s", "job"], f"pack {p['id']} structure", e)
    return e

def timeline(t):
    e = []
    _req(t, ["video", "format", "duration_s", "shots"], "timeline.json", e)
    if e: return e
    shots = t["shots"]
    if not shots: return ["timeline.json: no shots"]
    prev_end = 0.0
    for i, s in enumerate(shots):
        _req(s, ["start_s", "end_s", "kind"], f"timeline.json shot {i}", e)
        if e: break
        if s["kind"] not in K.ALL:
            e.append(f"timeline.json shot {i}: unknown kind '{s['kind']}'")
        if s["end_s"] <= s["start_s"]:
            e.append(f"timeline.json shot {i}: end_s must be after start_s")
        if s["start_s"] < prev_end - 0.01:
            e.append(f"timeline.json shot {i}: overlaps the previous shot (starts {s['start_s']}, previous ends {prev_end})")
        if s["kind"] in K.NEEDS_MEDIA and not s.get("media"):
            e.append(f"timeline.json shot {i} ({s['kind']}): needs a media file")
        prev_end = s["end_s"]
    if shots and shots[-1]["end_s"] > t["duration_s"] + 0.5:
        e.append(f"timeline.json: last shot ends at {shots[-1]['end_s']}s but duration_s is {t['duration_s']}s")
    return e
