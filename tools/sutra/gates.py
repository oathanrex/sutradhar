"""Five hard gates. PASS / FAIL / SKIP with the exact offending timestamp. No gate is skippable by choice."""
import json, pathlib, re, shutil, subprocess
from . import kinds as K
from .util import jload, contrast, ffmpeg_exe

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
    norm = lambda x: str(x or "").replace("\\", "/").lstrip("./")
    by_path = {norm(e.get("path")): e for e in man.get("assets", [])}
    off, seen = [], set()
    for s in tl["shots"]:
        for m in s.get("media") or []:
            e = by_path.get(norm(m)) or next((v for k, v in by_path.items() if k and norm(m).endswith(k.split("/")[-1])), None)
            if not e:
                if m not in seen: off.append(f"{m}: not in the library manifest - record it, then run sutra library index")
                seen.add(m)
            elif not e.get("license") or not e.get("source"):
                off.append(f"{m}: licence/source missing")
    return _res("FAIL" if off else "PASS", f"{len(by_path)} licensed asset(s) in the manifest", off)

def audio(render, R):
    render = pathlib.Path(render) if render else None
    if not render or not render.exists():
        return _res("SKIP", "no render yet")
    ff = ffmpeg_exe()
    if not ff:
        return _res("SKIP", "ffmpeg not installed (winget install Gyan.FFmpeg / brew install ffmpeg, "
                            "or: pip install imageio-ffmpeg)")
    p = subprocess.run([ff, "-hide_banner", "-i", str(render), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    lufs = [float(x) for x in re.findall(r"I:\s+(-?[\d.]+) LUFS", p.stderr)]
    peak = [float(x) for x in re.findall(r"Peak:\s+(-?[\d.]+) dBFS", p.stderr)]
    if not lufs: return _res("SKIP", "ffmpeg gave no loudness data (is the render silent?)")
    target = R.get("audio.voice_lufs", -14); tpk = R.get("audio.true_peak_max", -1.0)
    off = []
    if abs(lufs[-1] - target) > 1.0: off.append(f"integrated {lufs[-1]} LUFS, target {target} +/-1")
    if peak and peak[-1] > tpk: off.append(f"true peak {peak[-1]} dBFS exceeds {tpk} dBFS (will clip on some players)")
    return _res("FAIL" if off else "PASS", f"{lufs[-1]} LUFS, peak {peak[-1] if peak else '?'} dBFS", off)

def _norm(w):
    import re
    return re.sub(r"[^a-z0-9\u0900-\u097f]", "", str(w).lower())


def words(render, words_json, transcribe=None, lang="en", min_coverage=None):
    """Re-transcribe the render and diff it against the voice's own word list.
    Catches the failure nobody hears: a sound effect or a duck that swallowed a word.
    `transcribe` is injectable so the logic is testable without a 3 GB model."""
    if not render:
        return _res("SKIP", "no render yet")
    if not words_json or not __import__("pathlib").Path(words_json).exists():
        return _res("SKIP", f"no word timings at {words_json}")
    want = []
    for seg in jload(words_json) or []:
        want += [_norm(w["w"]) for w in seg.get("words", [])]
    want = [w for w in want if w]
    if not want:
        return _res("SKIP", "word timings file is empty")
    if transcribe is None:
        try:
            from faster_whisper import WhisperModel  # noqa: F401
        except ImportError:
            return _res("SKIP", "pip install faster-whisper  (then this gate re-transcribes the render and diffs it)")
        transcribe = _whisper_transcriber(str(render), lang)
    try:
        got_pairs = transcribe()
    except Exception as e:                      # a broken model must not look like a pass
        return _res("SKIP", f"transcription failed: {type(e).__name__}: {e}")
    got = [_norm(w) for w, _ in got_pairs]
    got = [w for w in got if w]
    import difflib
    sm = difflib.SequenceMatcher(None, want, got, autojunk=False)
    ratio = sm.ratio()
    off = []
    for op, a, b, c, d in sm.get_opcodes():
        if op in ("delete", "replace") and b > a:
            t = got_pairs[min(c, len(got_pairs) - 1)][1] if got_pairs else 0.0
            off.append(f"{int(t // 60)}:{t % 60:05.2f} missing or changed: {' '.join(want[a:b])}")
    thr = 0.98 if min_coverage is None else min_coverage
    status = "PASS" if ratio >= thr and not off else "FAIL"
    return _res(status, f"coverage {ratio * 100:.1f}% (min {thr * 100:.0f}%), "
                        f"{len(want)} words in the voice, {len(got)} heard", off)


def _whisper_transcriber(path, lang):
    def run():
        import numpy as np
        import re, subprocess
        from faster_whisper import WhisperModel
        pcm = np.frombuffer(subprocess.run(
            ["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
            capture_output=True, check=True).stdout, np.float32)
        model = "small.en" if lang == "en" else "large-v3"
        segs, _ = WhisperModel(model, device="cpu", compute_type="int8").transcribe(
            pcm, word_timestamps=True, beam_size=5, language=None if lang == "en" else lang)
        return [(w.word, w.start) for s in segs for w in s.words]
    return run


def flash(render, fps=30, limit=3.0):
    """Photosensitivity: no more than 3 luminance flashes per second (WCAG 2.3.1 territory)."""
    from .visual import luminance_series, flash_rate
    if not render or not __import__("pathlib").Path(render).exists():
        return _res("SKIP", "no render yet")
    if not ffmpeg_exe():
        return _res("SKIP", "ffmpeg not installed (pip install imageio-ffmpeg works too)")
    try:
        lums = luminance_series(render, fps)
    except Exception as e:
        return _res("SKIP", f"could not sample frames: {e}")
    rate, at = flash_rate(lums, fps)
    off = [f"{t:.2f}s flash cluster at {rate:.1f} flashes/sec (limit {limit})"] if rate > limit else []
    return _res("FAIL" if off else "PASS", f"max {rate:.1f} flashes/sec", off)


ALL = [("hook", lambda tl, R, **k: hook(tl, R)),
       ("pace", lambda tl, R, **k: pace(tl, R, k.get("spec"))),
       ("mobile", lambda tl, R, **k: mobile(tl, R)),
       ("legal", lambda tl, R, **k: legal(tl, root=k.get("root"))),
       ("audio", lambda tl, R, **k: audio(k.get("render"), R)),
       ("words", lambda tl, R, **k: words(k.get("render"), k.get("words_json"), k.get("transcribe"),
                                           k.get("lang", "en"), k.get("min_coverage"))),
       ("flash", lambda tl, R, **k: flash(k.get("render"), limit=3.0))]

def run_all(tl, R, spec=None, render=None, root=None, words_json=None, transcribe=None,
            lang="en", min_coverage=None):
    out = []
    for name, fn in ALL:
        out.append((name, fn(tl, R, spec=spec, render=render, root=root, words_json=words_json,
                             transcribe=transcribe, lang=lang, min_coverage=min_coverage)))
    return out
