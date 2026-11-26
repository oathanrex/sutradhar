---
name: plan
description: Turn a video idea into a production plan - pick category pack, locale and format, scaffold the video folder, print the beat structure, the numbers it must hit and the retention risks for that category. Use when they say "new video", "plan this video", "I want to make a video about X", or before any script or edit work.
---

# plan

One video = one folder = one `plan/` that both the script and the edit obey.

## Steps
1. **Pick the pack.** Run `sutra pack list`, propose 1-2 packs with a reason, let them choose. Never silently
   default: the pack sets pace, shot mix, hook patterns and the gate thresholds.
2. **Locale + format.** `en | hi | hinglish` and `long-16x9 | portrait-9x16`. State the consequence in one line
   (e.g. "hinglish forces whisper large-v3 and 30 chars per caption line").
3. **Scaffold.**
   ```bash
   sutra init "<video-name>" --pack <pack> --locale <locale> --format <format>
   ```
   This writes `videos/<name>/plan/{brief.md,resolved.json,timeline.json}`.
4. **Read `brief.md` out loud to them**: beat table, retention risks, hook patterns, the Never list, and the
   numbers (`cuts_per_min`, `max_hold`, `chars_per_line`, `sfx_per_min`). Each line shows which layer chose it.
5. **Write the one-line promise.** `plan/promise.md`: "By the end, the viewer can ______." If they cannot finish
   that sentence, the video is not ready - say so.
6. **Fix the asset list now, not at render time.** List every screen, b-roll, gif and sound the voiceover will
   probably need, then check `library/manifest.json`. Anything missing goes into `plan/assets_needed.md` with a
   search term and the licence it needs. This is where 80% of failed edits are lost.
7. **Only then** hand over to `script`.

## Done when
- [ ] `videos/<name>/plan/brief.md` exists and was shown
- [ ] `promise.md` has one sentence with a concrete capability
- [ ] every pack retention risk has either a planned shot or a written "accepting this risk" line
- [ ] `assets_needed.md` exists, even if empty
