---
name: gate
description: Run the five hard publish gates - hook, pace, mobile legibility, audio loudness/true peak, legal licence - on a render, report PASS/FAIL with the exact offending timestamp, and fix nothing without permission. Use before every upload, or when they say "check this", "is it ready", "QA the render".
---

# gate

Automate the check, never the judgement. This skill reports; it does not quietly repair.

```bash
sutra gate --timeline videos/<name>/plan/timeline.json --render videos/<name>/renders/<name>_v01.mp4 \
  --pack <pack> --locale <locale> --format <format>
```

| gate | measures | fails when |
|---|---|---|
| hook | first visual change; empty opening frame; long shot inside the first 10s | change > `hook_first_change_s`, or an empty first frame |
| pace | cuts/min vs spec; shots over `max_hold` | over tolerance, or more breaches than allowed |
| mobile | chars per line, lines per card, text/background contrast | any line too long, >2 lines, contrast < 4.5:1 |
| audio | integrated LUFS, true peak | outside `voice_lufs` +/-1, true peak above `true_peak_max` |
| legal | every media path against `library/manifest.json` | asset missing, or licence/source empty |

## Steps
1. Run the gate. Paste the table **verbatim**. No summary that hides a FAIL.
2. For every FAIL, print the timestamp and the offender line. Do not propose a fix yet.
3. Add the two checks the CLI cannot do, by looking at frames:
   - **hook legibility**: extract the frame at 0.8s and 2.5s, scale to 320 px wide, judge if the headline is readable
   - **thumbnail promise**: does the 0.8s frame look like the thumbnail? If not, one of them is lying
4. Ask: "fix now, or ship with a note?" If they say ship, write the exception in `plan/deviations.md` with a date.
5. Never mark a gate PASS because the render looks fine. A gate that passes on sight is not a gate.

## Done when
- [ ] all five rows reported with state and detail
- [ ] every FAIL has a timestamp
- [ ] either zero FAILs, or `plan/deviations.md` has a dated line for each accepted exception
- [ ] the two frame checks were done and stated in words
