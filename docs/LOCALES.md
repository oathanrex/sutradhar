# Locales — why a language is a config, not a translation

A locale in this repo is not a word list. It owns six things that break a video when they are wrong:

| it owns | because |
|---|---|
| **whisper model** | a small English model on Hindi/Tamil/Bengali audio produces confident nonsense, and every word-anchored shot inherits the error |
| **caption width** | scripts have different information density per glyph; the same 42 characters do not fit |
| **line height** | matras above, descenders below, conjuncts that grow in both directions |
| **caps policy** | Devanagari, Tamil and Bengali have no upper case, so a caps style silently does nothing or destroys the look |
| **letter spacing** | too much breaks conjunct clusters and stretches letterforms that are not meant to stretch |
| **speed budget** | 130 wpm in Hindi is not 130 wpm in English; a reused timing budget drifts by minutes |

## The six shipped locales

| | en | hi | hinglish | mr | ta | bn |
|---|---|---|---|---|---|---|
| script | Latin | Devanagari | Devanagari + Latin | Devanagari | Tamil | Bengali |
| whisper | small.en | **large-v3** | **large-v3** | **large-v3** | **large-v3** | **large-v3** |
| chars / line (ceiling) | 42 | 28 | 30 | 30 | 24 | 26 |
| line height | 0.92 | 1.08 | 1.06 | 1.08 | 1.10 | 1.14 |
| caps | allowed | none | none | none | no case at all | no case at all |
| width vs English | 1.00 | 1.18 | 1.12 | 1.16 | **1.32** | 1.28 |
| wpm budget | 150 | 120 | 130 | 118 | 110 | 115 |
| suggested free fonts | Inter Tight, Bricolage | Baloo Bhai 2, Mukta | Baloo Bhai 2 + Latin fallback | Mukta, Tiro Marathi | Noto Sans Tamil, Mukta Malar | Noto Sans Bengali, Hind Siliguri |

The pack's own ceiling still wins: if a pack says 16 characters per line (education), a Tamil render gets
`min(16, 24) = 16`. The tighter constraint is the real one.

**These are starting defaults, not measurements.** Measure three videos in your own niche before quoting them —
same rule as the packs (`sutra evidence`).

## Fonts, per OS

```bash
# macOS
brew install --cask font-noto-sans-tamil font-noto-sans-bengali font-baloo-bhai-2 font-mukta

# Windows
# download from fonts.google.com and right-click -> Install for all users:
#   Noto Sans Tamil, Noto Sans Bengali, Baloo Bhai 2, Mukta

# Debian/Ubuntu
sudo apt install fonts-noto-core fonts-indic
```

Then set a **stack**, not a single font, so a mixed Hinglish line does not jump in size between scripts:

```json
{
  "font_title": "Baloo Bhai 2, Noto Sans Tamil, Inter Tight",
  "font_body": "Mukta, Noto Sans Bengali, Inter, sans-serif"
}
```

`sutra doctor` reads the locale files, works out which scripts this repo can produce, and tells you which ones
have no font installed on this machine.

## Why `hinglish` is its own locale

Code-switching is not "Hindi with English words". The captions have to be written exactly as spoken —
`yaar ye kaam nahi karega` stays Roman — and the font stack needs a Devanagari face *and* a Latin face at the same
optical size. Transliterating into Devanagari in the caption is a common and immediately visible mistake.

## Adding a locale (15 minutes)

1. `cp locales/hi.json locales/<code>.json`
2. Change: `id`, `name`, `whisper_lang`, `whisper_model`, `caption.max_chars_per_line`,
   `text.expansion_vs_en`, `text.line_height`, `fonts.needs_script`, `fonts.suggested_free`, and the `notes`.
3. Measure one real video in that language at 320 px wide to check the character ceiling.
4. `PYTHONPATH=tools python3 -m sutra check && PYTHONPATH=tools python3 scripts/matrix.py`
5. PR with the language, the font, the measured ceiling, and one sentence on what usually breaks.

If `fonts.needs_script` is set, `resolve()` will refuse to stay silent about a Latin-only brand font and will
force the caption case to `NATIVE`. Both of those are the point.

## Formats are the other half

| format | frame | pace multiplier | safe zone (top / bottom) |
|---|---|---|---|
| `long-16x9` | 1920×1080 | 1.00 | 8% / 70% |
| `portrait-9x16` | 1080×1920 | 0.70 | 14% / 62% |
| `vertical-4x5` | 1080×1350 | 0.80 | 10% / 68% |
| `square-1x1` | 1080×1080 | 0.85 | 10% / 74% |

The multiplier is applied after every other layer merges, so a pack never needs to know it is being rendered
vertically: `comedy` at 45 cuts/min becomes 52.9 in `square-1x1` and 64.3 in `portrait-9x16` without a single
pack edit.
