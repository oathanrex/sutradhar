---
name: shorts
description: Cut long-form footage into vertical shorts that actually stand alone - pick spans by audio energy and sentence completeness, re-cut the pace for 9:16, re-hook in the first second, and never just crop the long edit. Use when they say "make shorts", "repurpose this", "vertical version", "reels from this video".
---

# shorts

A short is not a crop. A short is a new video that happens to use the same footage.

## Steps
1. **Find candidates by evidence, not vibes**: per-5s audio energy (ffmpeg ebur128 windows) plus word density
   from the transcript. A candidate span is 25-45s, starts on a complete sentence and ends on a resolution.
2. **Write the 9:16 hook separately.** The long-form hook does not survive the first second of a feed. State the
   payoff in <= 8 words, on screen, before the first word is spoken.
3. **Re-scope the plan**: `sutra init <name>-short --pack <pack> --locale <locale> --format portrait-9x16`.
   The format auto-shortens `max_hold` and raises `cuts_per_min` - obey the new numbers, do not reuse the long cut.
4. **Re-frame, do not letterbox.** Every full-frame shot needs a crop decision: what is the subject, does it fit
   9:16, or does it need a new screen recording at portrait size. A face cut in half is a failed short.
5. **Safe zones**: 14% top, 62% bottom. Platform UI covers both. Captions at `caption_size_mult` 1.25 minimum.
6. **Gate every short independently** with `sutra gate --format portrait-9x16`. A short with an unlicensed asset
   or a clipped true peak gets taken down just as fast as a long video.
7. **Ship the set, not one.** 3 spans minimum, each with its own hook line and its own thumbnail frame.

## Done when
- [ ] every span is 25-45s, self-contained, and understandable with sound off
- [ ] each short has its own hook written in <= 8 words
- [ ] no shot was letterboxed - each was cropped or re-recorded
- [ ] `sutra gate --format portrait-9x16` passes for every short
- [ ] the long video's `timeline.json` was not modified to make the shorts
