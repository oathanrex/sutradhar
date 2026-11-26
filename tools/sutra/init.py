"""sutra init: scaffold one video project from pack x locale x format."""
import pathlib
from .resolve import resolve
from .util import jdump, ok, warn, table

TIMELINE_SKELETON = {"version": "1.0", "video": "", "format": "", "duration_s": 0.0, "shots": []}

def video(name, pack="tutorial", locale="en", fmt="long-16x9", base=None, brand=None):
    base = pathlib.Path(base or ".").resolve()
    R = resolve(pack, locale, fmt, brand_path=brand)
    v = base / "videos" / name
    for sub in ("audio", "assets", "plan", "renders"): (v / sub).mkdir(parents=True, exist_ok=True)
    if not (v / "plan" / "timeline.json").exists():
        jdump(v / "plan" / "timeline.json", dict(TIMELINE_SKELETON, video=name, format=fmt))
    R.vals["pack"] = pack
    jdump(v / "plan" / "resolved.json", R.as_dict())
    brief = [f"# {name}", "",
             f"Pack: `{pack}` · Locale: `{locale}` · Format: `{fmt}` "
             f"({R['format']['width']}x{R['format']['height']})", "",
             "## structure to hit", "", "| beat | from | target | job |", "|---|---|---|---|"]
    brief += [f"| {b['beat']} | {b['start_s']}s | {b['target_s']}s | {b['job']} |" for b in R.get("structure", [])]
    if R.get("retention_risks"):
        brief += ["", "## retention risks for this pack", ""] + [f"- {x}" for x in R["retention_risks"]]
    if R.get("hook_patterns"):
        brief += ["", "## hook patterns that work here", ""] + [f"- {x}" for x in R["hook_patterns"]]
    if R.get("never"):
        brief += ["", "## never", ""] + [f"- {x}" for x in R["never"]]
    brief += ["", "## numbers this video must hit", ""]
    brief += [f"- {k}: **{R.get(k)}**  _(from {R.why(k)})_" for k in
              ("pacing.cuts_per_min", "pacing.avg_shot_len_s", "pacing.max_hold_s",
               "text.max_chars_per_line", "audio.sfx_per_min", "safe.caption_size_px") if R.get(k) is not None]
    brief += ["", "## locale notes", ""] + [f"- {n}" for n in R["locale"]["notes"]]
    (v / "plan" / "brief.md").write_text("\n".join(brief) + "\n", encoding="utf8")
    for w in R.warnings: warn(w)
    ok(f"created {v}")
    ok(f"brief: {v/'plan'/'brief.md'}")
    return v
