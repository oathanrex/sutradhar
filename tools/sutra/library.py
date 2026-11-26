"""Index media into library/manifest.json. A file without a licence cannot enter the library."""
import csv, hashlib, json, pathlib, shutil, subprocess
from .util import jload, jdump, ok, warn, table

EXT = {".mp4", ".mov", ".webm", ".mkv", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".wav", ".mp3", ".m4a", ".aiff", ".flac"}

def _probe(p):
    if not shutil.which("ffprobe"): return {}
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height:format=duration", "-of", "json", str(p)], capture_output=True, text=True)
    try: d = json.loads(r.stdout)
    except Exception: return {}
    st = (d.get("streams") or [{}])[0]
    return {"w": st.get("width"), "h": st.get("height"),
            "duration_s": round(float(d.get("format", {}).get("duration", 0) or 0), 2)}

def _licences(root):
    p = root / "library" / "licenses.csv"; out = {}
    if not p.exists(): return out
    with open(p, newline="", encoding="utf8") as f:
        for r in csv.DictReader(f):
            k = (r.get("path") or "").strip()
            if k: out[k] = {"license": (r.get("license") or "").strip(), "source": (r.get("source") or "").strip()}
    return out

def index(root=".", write=True):
    root = pathlib.Path(root).resolve()
    man_p = root / "library" / "manifest.json"
    man = jload(man_p) or {"version": "1.0", "assets": []}
    known = {a["path"] for a in man["assets"]}
    lic = _licences(root); added, unlicensed = 0, []
    for p in sorted((root / "library").rglob("*")):
        if not p.is_file() or p.suffix.lower() not in EXT: continue
        rel = str(p.relative_to(root))
        if rel in known: continue
        e = {"path": rel, "kind": "audio" if p.suffix.lower() in {".wav", ".mp3", ".m4a", ".aiff", ".flac"} else "visual",
             "bytes": p.stat().st_size, "sha1": hashlib.sha1(p.read_bytes()).hexdigest()[:12],
             "tags": [p.parent.name], "license": None, "source": None}
        e.update({k: v for k, v in _probe(p).items() if v})
        if rel in lic: e.update(lic[rel])
        if not e["license"]: unlicensed.append(rel)
        man["assets"].append(e); added += 1
    if write: jdump(man_p, man)
    return added, len(man["assets"]), unlicensed
