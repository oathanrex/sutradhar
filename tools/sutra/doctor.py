"""sutra doctor: say exactly what is missing and the command that fixes it."""
import importlib.util, pathlib, platform, shutil, subprocess, sys
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

def _has_devanagari():
    if not shutil.which("fc-list"): return sys.platform.startswith("darwin") or sys.platform.startswith("win")
    return bool(subprocess.run(["fc-list", ":lang=hi"], capture_output=True, text=True).stdout.strip())

def _devanagari_detail():
    try:
        out = subprocess.run(["fc-list", ":lang=hi", "family"], capture_output=True, text=True).stdout.strip()
        return (out.splitlines()[0][:48] if out else "none found")
    except Exception:
        return "fc-list unavailable"

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
    ("devanagari font", _has_devanagari, _devanagari_detail(),
     "for hi/hinglish: install Baloo Bhai 2 or Mukta from Google Fonts"),
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
