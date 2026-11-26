import json, os, pathlib, sys, re

ROOT = pathlib.Path(__file__).resolve().parents[2]

def jload(p, default=None):
    p = pathlib.Path(p)
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf8"))

def jdump(p, obj):
    p = pathlib.Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf8")

def die(msg, code=2):
    print(f"  x {msg}", file=sys.stderr)
    raise SystemExit(code)

def ok(msg): print(f"  + {msg}")
def warn(msg): print(f"  ! {msg}")
def fail(msg): print(f"  x {msg}")

def table(rows, headers, widths=None):
    widths = widths or [max(len(str(r[i])) for r in [headers] + rows) for i in range(len(headers))]
    line = lambda cells: "  " + "  ".join(str(c).ljust(w) for c, w in zip(cells, widths)).rstrip()
    print(line(headers)); print("  " + "  ".join("-" * w for w in widths))
    for r in rows: print(line(r))

def hex2rgb(h):
    h = h.lstrip("#")
    if len(h) == 3: h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def luminance(h):
    def ch(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = hex2rgb(h)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)

def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")
