# AGENTS.md - read this first

You are working in **sutradhar**: one thread from research to retention. All procedure lives in the skills; this
file is the routing table and the non-negotiables.

## Read order
1. `brand/about_me/` - who the creator is
2. `brand/design.json` + `brand/style.spec.json` - what every frame must look like and hit
3. `brand/rules.md` - dated rules; every visual decision must cite one
4. `packs/<chosen>.json` - pace, shot mix, hook patterns, retention risks for this category
5. `locales/<chosen>.json` - script, caption width, whisper model, font requirements
   (`en · hi · hinglish · mr · ta · bn`; Indian scripts force caption case to NATIVE and demand a font fallback)
6. `formats/<chosen>.json` - resolution, safe zones, pacing multiplier

## Which skill when
| the creator says | skill |
|---|---|
| "build my brand", "set up my design system" | `brand` |
| "new video", "plan this", "make a video about X" | `plan` |
| a link, "why did this blow up", "what is working" | `research` |
| "write the script", "is this hook good" | `script` |
| "edit this", voiceover dropped in | `edit` |
| "is it ready", "check this", "QA" | `gate` |
| "why do people leave", "what is working", weekly review | `loop` |
| "make shorts", "reels", "vertical" | `shorts` |

## Non-negotiables
- **Zero dependencies for the core.** `sutra` runs on the standard library. ffmpeg / whisper / node are optional,
  and a missing one is reported with the exact command that fixes it - never a silent fallback.
- **Ask, do not guess.** One unclear line, one missing file, one ambiguous licence: ask, with options.
- **Numbers over adjectives.** Any claim about pace, contrast, loudness or retention comes from a measurement.
- **Two human gates.** Storyboard approval before render, gate review before publish. Nothing else needs a human.
- **Never overwrite a render.** Version folders only (`v01`, `v02`).
- **Licence or it does not go on screen.** No exceptions, not even for a thumbnail.
- **Delete rules that do not earn evidence.** A longer rules file is not a better system.
- **Verify before claiming.** `sutra check`, `sutra spec verify`, `sutra gate`. A skill is done when its own
  checklist passes, not when the prose sounds confident.

## Commands
```bash
sutra doctor                                                 # what is missing, and the fix
sutra pack list                                              # 10 creator categories
sutra resolve --pack X --locale hi --format portrait-9x16    # merged config + where each value came from
sutra init <name> --pack X                                   # scaffold videos/<name>/plan/
sutra check --timeline <file>                                # validate brand, packs, spec, timeline
sutra spec verify <timeline>                                 # the numbers vs the spec
sutra build <timeline> --out <dir>                           # shot-sheet player + composition + receipt
sutra gate --timeline <file> --render <mp4>                  # the seven publish gates
sutra evidence                                               # which packs have real videos behind their numbers
sutra analytics pull --video <id> --duration <s>             # retention without a CSV export
sutra loop <curve.csv> --timeline <file>                     # retention curve -> rule proposals
sutra library index                                          # no licence, no entry
make test                                                    # 57 tests, no network, no GPU
make preview                                                 # render docs/demo.mp4 and gate it
```

## Definition of done for any video
`plan/brief.md` approved -> `script.md` approved -> `plan/timeline.json` validates -> storyboard approved ->
render `v##` exists -> `sutra gate` all PASS or exceptions written in `plan/deviations.md` -> retention curve
pulled after 7 days -> `sutra loop` run -> one rule locked or one rule deleted.
