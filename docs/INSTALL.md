# Install

## 1. Core (required, 2 minutes)

```bash
git clone https://github.com/<you>/sutradhar && cd sutradhar
python3 --version      # 3.10 or newer
make test              # 21 tests should pass
make doctor            # what is missing, and the fix
```

Nothing else is required to plan, research, script, validate, gate on the timeline, or run the retention loop.

## 2. Rendering (needed for MP4)

| tool | why | install |
|---|---|---|
| Node 22+ | HyperFrames runtime | https://nodejs.org |
| HyperFrames | HTML → MP4 | `npx hyperframes init` in your video project, per [its repo](https://github.com/heygen-com/hyperframes) |
| ffmpeg | loudness gate, contact sheets, probes | Windows `winget install Gyan.FFmpeg` · Mac `brew install ffmpeg` · Linux `apt install ffmpeg` |

Pin the HyperFrames version in `examples/demo-30s/project/package.json`. It ships weekly; an unpinned engine is a
time bomb in a 300-line build script.

## 3. Optional extras

```bash
pip install -r requirements-optional.txt      # faster-whisper (word timings, words gate), Pillow (contact sheets)
```

`faster-whisper` model per locale: `small.en` for English, **`large-v3` for `hi` and `hinglish`**. Using a small
English model on Hindi audio produces confident garbage — the locale config exists to prevent exactly this.

## 4. Per agent

**Claude Code** — open the folder. It reads `CLAUDE.md`. Say `build my brand`.

**Antigravity / Gemini CLI**
```bash
make sync          # mkdir -p .agents/skills && mirror .claude/skills  (the plain cp fails on a fresh clone)
```
Then tell it: *"read AGENTS.md first, then run the brand skill"*.

**Codex / Cursor** — point it at `AGENTS.md`; the skills folder is plain markdown.

## 5. Devanagari (for `hi` / `hinglish`)

Install **Baloo Bhai 2** or **Mukta** (Google Fonts, free), then set the font stack in `brand/design.json`:

```json
{"font_title": "Baloo Bhai 2", "font_body": "Mukta, Inter, sans-serif"}
```

Two rules the config enforces for you: caps are disabled (Devanagari has no upper case) and line height goes to
1.06–1.08 so top matras do not clip. `sutra doctor` checks that a Devanagari font is actually installed.

## Troubleshooting

| symptom | cause | fix |
|---|---|---|
| `cp: cannot stat '.agents/skills'` | the plain `cp -r .claude/skills .agents/skills` from every other repo | `make sync` |
| captions are gibberish | wrong whisper model for the language | `--locale hi` (uses large-v3) |
| text is unreadable on a phone | line too long for the frame | lower `text.max_chars_per_line`; `sutra check` |
| legal gate fails | asset not in `library/manifest.json` or missing a licence row | add a row to `library/licenses.csv`, `sutra library index` |
| audio gate SKIP | no ffmpeg | see step 2 |
| `sutra: command not found` | PYTHONPATH missing | `export PYTHONPATH=tools` or use `make` |
| a render broke after an update | HyperFrames moved | pin the version; the timeline still validates, so a re-render is cheap |

Every error message in the CLI names the command that fixes it. If one does not, that is a bug — open an issue.
