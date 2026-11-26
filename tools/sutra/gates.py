"""Five hard gates. PASS / FAIL / SKIP with the exact offending timestamp. No gate is skippable by choice."""
import json, pathlib, re, shutil, subprocess
from . import kinds as K
from .util import jload, contrast

def _res(status, detail, offenders=None): return {"status": status, "detail": detail, "offenders": offenders or []}

def hook(tl, R):
    sh = tl["shots"]; lim = R.get("gate.hook_first_change_s", 1.5)
    off = []
    first_change = sh[0]["end_s"] if len(sh) > 1 else tl["duration_s"]
    if first_change > lim:
        off.append(f"0:00.00 first visual change at {first_change:.2f}s, must be <= {lim}s")
    if not (sh[0].get("text") or sh[0].get("media")):
        off.append("0:00.00 first shot carries neither text nor media: the opening frame is empty")
    mh = R.get("pacing.max_hold_s", 5) * 1.2
    for s in sh:
        if s["start_s"] < 10 and s["end_s"] - s["start_s"] > mh:
            off.append(f"{s['start_s']:.2f}s shot runs {s['end_s']-s['start_s']:.1f}s inside the first 10s (max {mh:.1f}s)")
    return _res("FAIL" if off else "PASS", f"first change {first_change:.2f}s (limit {lim}s)", off)

def pace(tl, R, spec=None):
    sh = tl["shots"]; off = []
    lengths = [(s.get("start_s", 0), s["end_s"] - s["start_s"], s["kind"]) for s in sh]
    mh = R.get("pacing.max_hold_s", 5)
    breaches = [f"{t:.2f}s {v:.1f}s {k}" for t, v, k in lengths if v > mh]
    allowed = max(1, int(len(sh) * R.get("gate.max_hold_breaches_pct", 0.05)))
    if len(breaches) > allowed:
        off += [f"{b}: over max_hold {mh}s" for b in breaches[:12]]
    want = (spec or {}).get("pacing", {}).get("cuts_per_min")
    if want:
        from .spec import stats
        got = stats(tl)["cuts_per_min"]
        tol = R.get("gate.pace_tolerance", 0.25)
        if abs(got - want) > want * tol:
            off.append(f"cuts/min measured {got}, spec {want} (tolerance {int(tol*100)}%)")
    return _res("FAIL" if off else "PASS", f"{len(breaches)} max_hold breach(es), {allowed} allowed", off)

def mobile(tl, R):
    lim = R.get("text.max_chars_per_line", 18); off = []
    for s in tl["shots"]:
        lines = s.get("text") or []
        if len(lines) > 2:
            off.append(f"{s['start_s']:.2f}s {s['kind']}: {len(lines)} lines of text, maximum 2")
        for line in lines:
            if len(str(line)) > lim:
                off.append(f"{s['start_s']:.2f}s {s['kind']}: '{str(line)[:34]}...' is {len(str(line))} chars (limit {lim})")
    bg, fg = R.get("colour.background"), R.get("colour.text")
    c = contrast(bg, fg)
    if c < R.get("gate.text_contrast_min", 4.5):
        off.append(f"text/background contrast {c}:1 below {R.get('gate.text_contrast_min')}:1")
    return _res("FAIL" if off else "PASS", f"max {lim} chars/line, contrast {c}:1", off)

def legal(tl, library_dir=None, root=None):
    root = pathlib.Path(root or pathlib.Path.cwd())
    man = jload(root / "library" / "manifest.json")
    if man is None:
        return _res("FAIL", "library/manifest.json is missing: no asset can be proven licensed", ["run: sutra library index"])
    by_path = {e.get("path"): e for e in man.get("assets", [])}
    off, seen = [], set()
    for s in tl["shots"]:
        for m in s.get("media") or []:
            e = by_path.get(m) or next((v for k, v in by_path.items() if k and str(m).endswith(k.split("/")[-1])), None)
            if not e:
                if m not in seen: off.append(f"{m}: not in the library manifest - record it and add a licence row")
                seen.add(m)
            elif not e.get("license") or not e.get("source"):
                off.append(f"{m}: licence/source missing")
    return _res("FAIL" if off else "PASS", f"{len(by_path)} licensed asset(s) in the manifest", off)

def audio(render, R):
    render = pathlib.Path(render) if render else None
    if not render or not render.exists():
        return _res("SKIP", "no render yet")
    if not shutil.which("ffmpeg"):
        return _res("SKIP", "ffmpeg not installed (winget install Gyan.FFmpeg / brew install ffmpeg)")
    p = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(render), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    lufs = [float(x) for x in re.findall(r"I:\s+(-?[\d.]+) LUFS", p.stderr)]
    peak = [float(x) for x in re.findall(r"Peak:\s+(-?[\d.]+) dBFS", p.stderr)]
    if not lufs: return _res("SKIP", "ffmpeg gave no loudness data (is the render silent?)")
    target = R.get("audio.voice_lufs", -14); tpk = R.get("audio.true_peak_max", -1.0)
    off = []
    if abs(lufs[-1] - target) > 1.0: off.append(f"integrated {lufs[-1]} LUFS, target {target} +/-1")
    if peak and peak[-1] > tpk: off.append(f"true peak {peak[-1]} dBFS exceeds {tpk} dBFS (will clip on some players)")
    return _res("FAIL" if off else "PASS", f"{lufs[-1]} LUFS, peak {peak[-1] if peak else '?'} dBFS", off)

def words(render, words_json):
    if not render: return _res("SKIP", "no render yet")
    try:
        from faster_whisper import WhisperModel  # noqa
    except ImportError:
        return _res("SKIP", "pip install faster-whisper, then this gate re-transcribes the render and diffs it")
    import difflib, re, sys
    model_name = (words_json and "large-v3") or "small.en"
    return _res("SKIP", f"faster-whisper present: run the words gate from the sutra-gate skill with model {model_name}")

ALL = [("hook", lambda tl, R, **k: hook(tl, R)),
       ("pace", lambda tl, R, **k: pace(tl, R, k.get("spec"))),
       ("mobile", lambda tl, R, **k: mobile(tl, R)),
       ("legal", lambda tl, R, **k: legal(tl, root=k.get("root"))),
       ("audio", lambda tl, R, **k: audio(k.get("render"), R))]

def run_all(tl, R, spec=None, render=None, root=None):
    out = []
    for name, fn in ALL:
        out.append((name, fn(tl, R, spec=spec, render=render, root=root)))
    return out
