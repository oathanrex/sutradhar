---
name: edit
description: Edit a video in code from the creator's voiceover - word-anchored shots, storyboard gate before any render, then render and hand over a timeline.json the gates can check. Use when they say "edit this video", "make the edit", "start editing", or drop a voiceover plus assets.
---

# edit

The engine writes HTML; you write `plan/timeline.json` and the shots file. You never hand-write the composition.

## Before anything
1. `sutra check brand` and `sutra resolve --pack <pack> --locale <locale> --format <format>`. If the brand is still
   the template, stop and offer `brand` first - a whole video in a placeholder look is wasted work.
2. Read the script and the voiceover transcript together. Then ask about **every** line whose visual you cannot
   point at a real file for. Ask with options, never guess.
3. `sutra library index` and confirm every asset the script needs has a licence row. Missing media is a stop, not a
   "I'll find something".

## Steps
1. **Word timings** from the voiceover with the locale's model (`en` -> small.en, `hi`/`hinglish` -> large-v3).
   Tighten: cut silences longer than the pack's `max_silence_ms`, even the loudness to `voice_lufs`.
2. **Write shots**, one per visual change, every shot anchored to its first spoken word. The anchor must be copied
   exactly as the transcript has it. A shot that starts on silence is a bug.
3. **Obey the numbers**: `cuts_per_min`, `avg_shot_len_s`, `max_hold_s`, `text.max_chars_per_line`, `sfx_per_min`
   and the pack's `shot_mix`. Deviating is allowed; deviating silently is not - log it in `plan/deviations.md`
   with one line of why.
4. **Emit `plan/timeline.json`** (`version, video, format, duration_s, shots[]` with `start_s, end_s, kind, text?,
   media?[], sfx?`). This file is the contract: gates, spec verify and the retention loop all read it. If the
   build script does not write it yet, write it before building.
5. **Storyboard gate.** One still per shot, stitched into one image, shown with the words under each frame.
   Wait for a go. Change only what they flag. Never render to MP4 before this approval.
6. **Build and render**, versioned (`v01`, `v02`, never overwrite). Then run the `gate` skill.
7. **Hand over** with a changelog: what changed since v01, which gates pass, which numbers are off-spec and why.

## Hard rules
- Readable text above 70% of frame height (16:9) or inside the format's safe zone. The player UI eats the rest.
- B-roll never carries text on top of it.
- Every graphic lands on its word, not before it.
- Sound effects only from `library/sfx/`, one at a time, never over a word's first consonant.
- One render = one version folder. Nothing is ever overwritten.

## Done when
- [ ] `sutra check timeline --timeline videos/<name>/plan/timeline.json` is clean
- [ ] `sutra spec verify` was run and every FAIL is either fixed or listed in `plan/deviations.md`
- [ ] storyboard was approved by the creator
- [ ] the render exists as `v##` and was checked with the `gate` skill
