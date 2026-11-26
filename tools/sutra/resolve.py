"""Resolve one production config: defaults -> brand -> category pack -> locale -> format.
Every leaf value remembers where it came from, so 'why is my caption 28 chars' has an answer."""
import copy, pathlib
from .util import ROOT, jload, contrast, die

DEFAULTS = {
    "pacing": {"cuts_per_min": 20, "avg_shot_len_s": 3.0, "max_hold_s": 5.0, "motion_per_shot": 1},
    "text": {"max_chars_per_line": 18, "words_on_screen_per_shot": 3.4, "letter_spacing_px": 0, "line_height": 0.95},
    "audio": {"voice_lufs": -14, "true_peak_max": -1.0, "music_lufs": -24, "duck_db": -18,
              "sfx_per_min": 6, "max_silence_ms": 600},
    "safe": {"top_pct": 8, "bottom_pct": 70, "side_pct": 6, "caption_size_px": 56},
    "gate": {"word_coverage_min": 0.98, "hook_first_change_s": 1.5, "pace_tolerance": 0.25,
             "max_hold_breaches_pct": 0.05, "text_contrast_min": 4.5, "sfx_per_min_max": 99},
    "colour": {"background": "#0E0F12", "text": "#F4F4F2", "accent": "#F2C200"},
    "font": {"title": "Inter Tight", "body": "Inter Tight", "mono": "JetBrains Mono"},
}

PACKS = ROOT / "packs"; LOCALES = ROOT / "locales"; FORMATS = ROOT / "formats"

def _merge(dst, src, source, prov, prefix=""):
    for k, v in src.items():
        path = f"{prefix}{k}"
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _merge(dst[k], v, source, prov, path + ".")
        elif isinstance(v, dict):
            dst[k] = copy.deepcopy(v)
            for kk in v: prov[f"{path}.{kk}"] = source
        else:
            dst[k] = v
            prov[path] = source

class Resolved:
    def __init__(self, vals, prov, sources, warnings):
        self.vals, self.prov, self.sources, self.warnings = vals, prov, sources, warnings
    def __getitem__(self, k): return self.vals[k]
    def get(self, path, default=None):
        cur = self.vals
        for part in path.split("."):
            if not isinstance(cur, dict) or part not in cur: return default
            cur = cur[part]
        return cur
    def why(self, path): return self.prov.get(path, "defaults")
    def as_dict(self): return {"values": self.vals, "provenance": self.prov, "sources": self.sources, "warnings": self.warnings}

def resolve(pack_id=None, locale_id="en", format_id="long-16x9", brand_path=None):
    brand_path = pathlib.Path(brand_path or (ROOT / "brand" / "design.json"))
    vals = copy.deepcopy(DEFAULTS); prov = {}; warnings = []; sources = {}
    brand = jload(brand_path)
    if brand:
        sources["brand"] = str(brand_path)
        mapped = {
            "colour.background": brand.get("background"), "colour.text": brand.get("text"),
            "colour.accent": brand.get("accent"),
            "font.title": brand.get("font_title"), "font.body": brand.get("font_body"),
            "font.mono": brand.get("font_mono"),
            "pacing.max_hold_s": brand.get("max_hold"),
            "safe.caption_size_px": brand.get("caption_size"),
        }
        for path, v in mapped.items():
            if v in (None, ""): continue
            sec, key = path.split(".")
            vals[sec][key] = v; prov[path] = "brand"
        if brand.get("sfx"):
            vals["audio"]["sfx_per_min"] = vals["audio"]["sfx_per_min"]; prov["audio.sfx_per_min"] = "brand"
    else:
        warnings.append("no brand/design.json yet: running on neutral defaults. Say 'build my brand' first.")

    pack = None
    if pack_id:
        p = PACKS / f"{pack_id}.json"
        if not p.exists():
            die(f"unknown pack '{pack_id}'. Available: {', '.join(sorted(x.stem for x in PACKS.glob('*.json')))}")
        pack = jload(p); sources["pack"] = pack_id
        _merge(vals, pack.get("spec_patch", {}), f"pack:{pack_id}", prov)
        _merge(vals, pack.get("gate", {}), f"pack:{pack_id}", prov)
        if pack.get("never"): vals["never"] = pack["never"]
        if pack.get("hook_patterns"): vals["hook_patterns"] = pack["hook_patterns"]
        if pack.get("structure"): vals["structure"] = pack["structure"]
        if pack.get("shot_mix"): vals["shot_mix"] = pack["shot_mix"]
        if pack.get("retention_risks"): vals["retention_risks"] = pack["retention_risks"]

    loc = jload(LOCALES / f"{locale_id}.json") or die(f"unknown locale '{locale_id}'")
    sources["locale"] = locale_id
    script = (loc.get("fonts") or {}).get("needs_script") or (
        "devanagari" if (loc.get("fonts") or {}).get("needs_devanagari") else None)
    vals["locale"] = {"id": loc["id"], "name": loc["name"], "whisper_lang": loc["whisper_lang"],
                      "whisper_model": loc["whisper_model"], "needs_script": script,
                      "notes": loc.get("notes", [])}
    _merge(vals, {"text": {"letter_spacing_px": loc["text"]["letter_spacing_px"],
                           "line_height": loc["text"]["line_height"]}}, f"locale:{locale_id}", prov)
    if "caption" in loc:
        vals["text"]["max_chars_per_line"] = min(vals["text"]["max_chars_per_line"], loc["caption"]["max_chars_per_line"])
        prov["text.max_chars_per_line"] = f"locale:{locale_id}"
        vals["caption"] = loc["caption"]

    fmt = jload(FORMATS / f"{format_id}.json") or die(f"unknown format '{format_id}'")
    sources["format"] = format_id
    vals["format"] = {"id": fmt["id"], "width": fmt["width"], "height": fmt["height"], "fps": fmt.get("fps", 30)}
    _merge(vals, {"safe": fmt["safe"]}, f"format:{format_id}", prov)
    mult = fmt.get("pacing_mult", 1.0)
    if mult != 1.0:   # mult = shot-duration multiplier: 0.7 means every shot is 30% shorter
        vals["pacing"]["cuts_per_min"] = round(vals["pacing"]["cuts_per_min"] / mult, 1)
        vals["pacing"]["avg_shot_len_s"] = round(vals["pacing"]["avg_shot_len_s"] * mult, 2)
        vals["pacing"]["max_hold_s"] = round(vals["pacing"]["max_hold_s"] * mult, 2)
        for k in ("cuts_per_min", "avg_shot_len_s", "max_hold_s"): prov[f"pacing.{k}"] = f"format:{format_id}"
        vals["pacing"]["format_mult"] = mult

    # --- consistency checks: the things that silently ruin an export
    body, bg = vals["font"]["body"], vals["colour"]["background"]
    if contrast(bg, vals["colour"]["text"]) < 4.5:
        warnings.append(f"text/background contrast {contrast(bg, vals['colour']['text'])}:1 is below 4.5:1")
    lat = {"inter tight", "inter", "archivo black", "bricolage grotesque", "jetbrains mono", "helvetica",
           "arial", "roboto", "montserrat", "poppins"}
    if script and str(body).lower() in lat:
        warnings.append(f"locale {locale_id} needs {script} script but the brand font is Latin-only ({body}). "
                        f"Add a fallback: {', '.join(loc['fonts'].get('suggested_free', []))}")
    brand_case = (brand or {}).get("caption_case")
    if brand_case:
        vals["caption"]["case"] = brand_case; prov["caption.case"] = "brand"
    if script and vals["caption"].get("case") == "UPPER":
        warnings.append(f"locale {locale_id}: {script} script has no upper case. "
                        f"Caption case forced UPPER -> NATIVE")
        vals["caption"]["case"] = "NATIVE"; prov["caption.case"] = f"locale:{locale_id}"
    if vals["pacing"]["max_hold_s"] <= vals["pacing"]["avg_shot_len_s"]:
        warnings.append("max_hold_s <= avg_shot_len_s: the pace target is impossible to hit")
    return Resolved(vals, prov, sources, warnings)
