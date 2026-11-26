"""timeline.json -> a real, openable video project.

Two outputs, on purpose:

  index.html        our own deterministic shot-sheet player. No dependencies, no engine, works offline:
                    this is the storyboard you can scrub, and the fastest way to check pacing by eye.
  hyperframes.html  the composition HyperFrames renders. Timing attributes follow HyperFrames'
                    documented composition shape; the shape is version-sensitive, so always run
                    `npx hyperframes check` before a render. Never claim it renders without that check.

Every build also writes a receipt: content hashes of the timeline, the assets and the resolved config,
so "which inputs produced this MP4" is a lookup, not an archaeology dig.
"""
import hashlib, html, json, pathlib
from . import kinds as K
from .util import jload, jdump, ok, warn, contrast

CSS = """
:root{--bg:%(bg)s;--fg:%(fg)s;--accent:%(accent)s;--mono:%(mono)s;--sans:%(sans)s}
*{box-sizing:border-box;margin:0;padding:0}
body{background:#08090b;color:var(--fg);font-family:var(--sans),system-ui,sans-serif;display:flex;
flex-direction:column;align-items:center;gap:18px;padding:22px}
#wrap{width:min(96vw,1100px)}
#stage{position:relative;width:100%%;aspect-ratio:%(w)d/%(h)d;background:var(--bg);overflow:hidden;
border-radius:10px;box-shadow:0 20px 60px #0009}
.shot{position:absolute;inset:0;display:none;align-items:center;justify-content:center;padding:5%%}
.shot.on{display:flex}
.rise{animation:rise .38s cubic-bezier(.2,.8,.2,1) both}
@keyframes rise{from{opacity:0;transform:translateY(26px)}to{opacity:1;transform:none}}
.words{font-weight:800;letter-spacing:-.02em;line-height:.9;text-align:center;text-transform:uppercase;
font-size:calc(var(--u)*1px)}
.accent{color:var(--accent)}
.chips{display:flex;gap:.5em;flex-wrap:wrap;justify-content:center}
.chip{border:2px solid var(--accent);border-radius:999px;padding:.28em .7em;color:var(--accent);
font-weight:700;font-size:calc(var(--u)*.9px)}
.chapter{text-align:center}
.chapter .no{font-family:var(--mono);font-size:calc(var(--u)*.9px);color:var(--accent);letter-spacing:.2em}
.chapter .nm{font-weight:800;font-size:calc(var(--u)*1.6px);text-transform:uppercase;line-height:.92}
.media{display:flex;flex-direction:column;gap:.6em;align-items:center;width:100%%;height:100%%;
justify-content:center}
.frame{width:88%%;height:74%%;border:2px solid #ffffff22;border-radius:8px;background:#0f1116;
display:flex;align-items:center;justify-content:center;font-family:var(--mono);font-size:calc(var(--u)*.38px);
color:#8a8f98}
.cap{font-family:var(--mono);font-size:calc(var(--u)*.34px);color:var(--accent)}
#bar{display:flex;align-items:center;gap:14px;width:100%%;font-family:var(--mono);font-size:13px;color:#8a8f98}
#track{flex:1;height:6px;background:#1b1e24;border-radius:3px;overflow:hidden}
#fill{height:100%%;width:0;background:var(--accent)}
button{background:#14161b;color:var(--fg);border:1px solid #262a32;border-radius:7px;padding:8px 14px;
font-family:inherit;font-size:13px;cursor:pointer}
#meta{width:100%%;font-family:var(--mono);font-size:12px;color:#6b7280;display:flex;justify-content:space-between}
"""

def js_block(shots, dur):
    data = json.dumps(shots)
    return f"""
const SHOTS = {data};
const DUR = {dur};
const stage = document.getElementById('stage');
const fill = document.getElementById('fill');
const now = document.getElementById('now');
let t0 = 0, playing = false, raf = null;
function shotAt(t) {{ for (let i = 0; i < SHOTS.length; i++) {{ if (t >= SHOTS[i].start_s && t < SHOTS[i].end_s) return i; }} return SHOTS.length - 1; }}
function paint() {{
  const t = ((performance.now() - t0) / 1000) % DUR;
  const i = shotAt(t);
  SHOTS.forEach((s, j) => {{
    const el = document.getElementById('s' + j);
    if (!el) return;
    if (j === i) {{ if (!el.classList.contains('on')) {{ el.classList.remove('rise'); void el.offsetWidth; el.classList.add('on', 'rise'); }} }}
    else {{ el.classList.remove('on', 'rise'); }}
  }});
  fill.style.width = (t / DUR * 100) + '%';
  now.textContent = t.toFixed(1) + 's / ' + DUR + 's';
  if (playing) raf = requestAnimationFrame(paint);
}}
function toggle() {{
  playing = !playing;
  if (playing) {{ t0 = performance.now() - (rafStart || 0); paint(); }} else cancelAnimationFrame(raf);
}}
let rafStart = 0;
document.addEventListener('keydown', e => {{ if (e.code === 'Space') {{ e.preventDefault(); toggle(); }} }});
t0 = performance.now();
paint();
"""


def _esc(x):
    return html.escape(str(x), quote=True)


def _unit(timeline, R):
    """Type size in stage px, derived from the frame height so 16:9 and 9:16 both work."""
    return max(18, int(R["format"]["height"] * 0.11))


def shot_markup(s, R, unit):
    kind, text = s["kind"], s.get("text") or []
    if kind == "words":
        body = f'<div class="words" style="--u:{unit}">' + "<br>".join(
            " ".join(f'<span class="accent">{_esc(w)}</span>' if w.isupper() and len(w) <= 6 and i == 0 else _esc(w)
                     for i, w in enumerate(line.split())) for line in text) + "</div>"
    elif kind == "chips":
        body = '<div class="chips">' + "".join(
            f'<span class="chip" style="--u:{unit}">{_esc(c)}</span>' for c in text) + "</div>"
    elif kind == "chapter":
        no = text[0] if text else "00"
        rest = " ".join(text[1:]) if len(text) > 1 else (s.get("beat") or "").upper()
        body = (f'<div class="chapter"><div class="no">/{_esc(no)}</div>'
                f'<div class="nm" style="--u:{unit}">{_esc(rest)}</div></div>')
    else:
        media = (s.get("media") or [None])[0]
        label = media or "no media planned"
        show = " ".join(text) if text else (s.get("beat") or "").upper()
        body = (f'<div class="media"><div class="frame">{_esc(label)}</div>'
                f'<div class="cap">{_esc(show)}</div></div>')
    return (f'<div class="shot" id="s{s["i"]}" data-kind="{_esc(kind)}" '
            f'data-start="{s["start_s"]}" data-end="{s["end_s"]}">{body}</div>')


def render_player(timeline, R, title):
    unit = _unit(timeline, R)
    shots = [{"start_s": s["start_s"], "end_s": s["end_s"]} for s in timeline["shots"]]
    css = CSS % {"bg": R["colour"]["background"], "fg": R["colour"]["text"], "accent": R["colour"]["accent"],
                 "mono": R["font"].get("mono", "monospace"), "sans": R["font"].get("body", "sans-serif"),
                 "w": R["format"]["width"], "h": R["format"]["height"]}
    body = "\n".join(shot_markup(s, R, unit) for s in timeline["shots"])
    shots = [{"start_s": s["start_s"], "end_s": s["end_s"]} for s in timeline["shots"]]
    script = js_block(shots, timeline["duration_s"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{_esc(title)} - shot sheet</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>{css}</style></head><body>
<div id="wrap">
<div id="stage">{body}</div>
<div id="bar"><button onclick="toggle()">play / pause</button>
<div id="track"><div id="fill"></div></div><span id="now"></span></div>
<div id="meta"><span>{_esc(title)}</span><span>{len(timeline['shots'])} shots &#183; {timeline['duration_s']}s &#183;
{R['format']['width']}x{R['format']['height']} &#183; space = play/pause</span></div>
</div>
<script>{script}</script>
</body></html>"""


def render_hyperframes(timeline, R, title):
    """HyperFrames composition. Timing lives in data-start / data-duration per shot."""
    w, h = R["format"]["width"], R["format"]["height"]
    unit = _unit(timeline, R)
    parts = []
    for s in timeline["shots"]:
        dur = round(s["end_s"] - s["start_s"], 3)
        inner = shot_markup(s, R, unit).replace('class="shot"', 'class="shot on"', 1)
        parts.append(
            f'  <div class="clip" data-start="{s["start_s"]}" data-duration="{dur}" '
            f'data-track="shots">{inner}</div>')
    css = CSS % {"bg": R["colour"]["background"], "fg": R["colour"]["text"], "accent": R["colour"]["accent"],
                 "mono": R["font"].get("mono", "monospace"), "sans": R["font"].get("body", "sans-serif"),
                 "w": w, "h": h}
    return f"""<!doctype html>
<!-- Generated by `sutra build`. Timing attributes follow the HyperFrames composition shape.
     HyperFrames changes often: run `npx hyperframes check` before rendering, and pin the version. -->
<html lang="en"><head><meta charset="utf-8"><title>{_esc(title)}</title>
<style>{css}
html,body{{background:transparent}}
.shot{{display:flex}}
.clip{{position:absolute;inset:0}}
</style></head><body>
<div id="stage" data-composition-id="{_esc(timeline['video'])}" data-start="0"
     data-width="{w}" data-height="{h}" style="position:relative;width:{w}px;height:{h}px;
     background:{R['colour']['background']};overflow:hidden">
{chr(10).join(parts)}
  <audio id="voice" data-start="0" data-track="audio" src="audio/voice_tight.wav"></audio>
</div>
</body></html>"""


def check_html(text, expected_shots, timed="data-duration"):
    """Structural self-check: one timed element per shot, ascending starts, no unescaped markup.

    `timed` is the attribute that marks a shot element: data-duration in the composition,
    data-end in the shot-sheet player. The stage and the audio track are deliberately not counted."""
    from html.parser import HTMLParser

    class P(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.starts = []

        def handle_starttag(self, tag, attrs):
            d = dict(attrs)
            if timed in d and "data-start" in d:
                self.starts.append(float(d["data-start"]))

    p = P(); p.feed(text)
    problems = []
    if len(p.starts) != expected_shots:
        problems.append(f"{len(p.starts)} timed elements, expected {expected_shots}")
    if p.starts != sorted(p.starts):
        problems.append("data-start values are not in ascending order")
    if "<script>alert" in text:
        problems.append("unescaped script in text content")
    return problems


def sha(path):
    p = pathlib.Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p.exists() else None


def build(timeline_path, out_dir, R, brand_root=None, quiet=False):
    tl = jload(timeline_path) or raise_("timeline not found: " + str(timeline_path))
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    title = tl.get("video", "video")
    player = render_player(tl, R, title)
    hf = render_hyperframes(tl, R, title)
    (out / "index.html").write_text(player, encoding="utf8")
    (out / "hyperframes.html").write_text(hf, encoding="utf8")
    problems = (check_html(hf, len(tl["shots"]), timed="data-duration")
                + check_html(player, len(tl["shots"]), timed="data-end"))
    receipt = {
        "engine": "sutradhar",
        "timeline": {"path": str(timeline_path), "sha256_16": sha(timeline_path), "shots": len(tl["shots"]),
                     "duration_s": tl["duration_s"]},
        "config": {"pack": R.sources.get("pack"), "locale": R.sources.get("locale"),
                   "format": R.sources.get("format"), "resolved_sha256_16":
                   hashlib.sha256(json.dumps(R.as_dict(), sort_keys=True).encode()).hexdigest()[:16]},
        "assets": [{"path": m, "sha256_16": sha((pathlib.Path(brand_root or ".") / "library" / m))}
                   for m in sorted({x for s in tl["shots"] for x in (s.get("media") or [])})],
        "html": {"player_sha256_16": hashlib.sha256(player.encode()).hexdigest()[:16],
                 "hyperframes_sha256_16": hashlib.sha256(hf.encode()).hexdigest()[:16]},
        "structural_problems": problems,
    }
    jdump(out / "receipt.json", receipt)
    if not quiet:
        ok(f"wrote {out/'index.html'}  (open it: scrub the timeline in a browser, no engine needed)")
        ok(f"wrote {out/'hyperframes.html'} + {out/'receipt.json'}")
        for p in problems:
            warn("structure: " + p)
        for a in receipt["assets"]:
            if a["sha256_16"] is None:
                warn(f"asset missing: library/{a['path']}")
    return receipt


def raise_(msg):
    from .util import die
    die(msg)
