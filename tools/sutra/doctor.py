"""sutra doctor: say exactly what is missing and the command that fixes it."""
import importlib.util, json, pathlib, platform, shutil, subprocess, sys
from .util import ROOT, table, ffmpeg_exe


def _ff():
    e = ffmpeg_exe()
    return ("imageio-ffmpeg wheel" if e and "site-packages" in e else e) if e else None

def _ver(cmd, args=("--version",)):
    if not shutil.which(cmd): return None
    try:
        r = subprocess.run([cmd, *args], capture_output=True, text=True, timeout=20)
        return (r.stdout or r.stderr).strip().splitlines()[0][:48]
    except Exception: return "installed"

def _scripts_needed():
    out = set()
    for f in (ROOT / "locales").glob("*.json"):
        try:
            s = json.loads(f.read_text())
        except Exception:
            continue
        sc = (s.get("fonts") or {}).get("needs_script")
        if sc:
            out.add(sc)
    return sorted(out)

_LANG = {"devanagari": "hi", "tamil": "ta", "bengali": "bn", "telugu": "te", "gujarati": "gu",
         "kannada": "kn", "malayalam": "ml", "gurmukhi": "pa", "odia": "or", "arabic": "ar"}

def _indic_found():
    """Which of the scripts this repo ships locales for actually have a font installed."""
    if not shutil.which("fc-list"):
        return None                                  # macOS/Windows: cannot tell, do not guess
    found = []
    for sc in _scripts_needed():
        code = _LANG.get(sc, sc[:2])
        r = subprocess.run(["fc-list", f":lang={code}", "family"], capture_output=True, text=True)
        if r.stdout.strip():
            found.append(sc)
    return found

def _has_indic():
    f = _indic_found()
    return True if f is None else len(f) == len(_scripts_needed())

def _indic_detail():
    f = _indic_found()
    if f is None:
        return "cannot check here (no fc-list)"
    if not f:
        return "none found"
    return ", ".join(f)[:48]

CHECKS = [
    ("python", lambda: (sys.version.split()[0] >= "3.10"), sys.version.split()[0], "install Python 3.10+"),
    ("ffmpeg", lambda: bool(_ff()), _ff() or "missing",
     "winget install Gyan.FFmpeg  |  brew install ffmpeg  |  pip install imageio-ffmpeg"),
    ("ffprobe", lambda: bool(shutil.which("ffprobe")), _ver("ffprobe", ("-version",)) or "missing",
     "ships with ffmpeg"),
    ("node 22+", lambda: bool(shutil.which("node")), _ver("node") or "missing", "https://nodejs.org"),
    ("hyperframes", lambda: bool(shutil.which("npx")), _ver("npx") or "missing",
     "npx hyperframes init  (pinned version lives in examples/demo-30s/project/package.json)"),
    ("faster-whisper", lambda: importlib.util.find_spec("faster_whisper") is not None,
     "installed" if importlib.util.find_spec("faster_whisper") else "missing", "pip install faster-whisper"),
    ("Pillow", lambda: importlib.util.find_spec("PIL") is not None,
     "installed" if importlib.util.find_spec("PIL") else "missing", "pip install Pillow"),
    ("brand/design.json", lambda: (ROOT / "brand" / "design.json").exists(),
     "found" if (ROOT / "brand" / "design.json").exists() else "missing", "say: build my brand"),
    ("style.spec.json", lambda: (ROOT / "brand" / "style.spec.json").exists(),
     "found" if (ROOT / "brand" / "style.spec.json").exists() else "missing", "sutra spec extract"),
    ("library manifest", lambda: (ROOT / "library" / "manifest.json").exists(),
     "found" if (ROOT / "library" / "manifest.json").exists() else "missing", "sutra library index"),
    ("indic fonts", _has_indic, _indic_detail(),
     "install a font per script you publish in (Google Fonts: Baloo Bhai 2, Noto Sans Tamil/Bengali)"),
]

def run():
    rows = []; bad = 0
    for name, fn, detail, fix in CHECKS:
        try: passed = bool(fn())
        except Exception: passed = False
        rows.append((name, "ok" if passed else "MISSING", detail, "" if passed else fix))
        bad += 0 if passed else 1
    table(rows, ["check", "state", "detail", "fix"], [16, 8, 50, 46])
    print()
    print(f"  {len(CHECKS)-bad}/{len(CHECKS)} ready." + (" Run the fixes above, then: sutra doctor" if bad else " You can render."))
    return bad
