---
name: loop
description: Close the loop between published videos and future edits - pull the retention curve, attribute every drop-off to the shot kind that caused it, propose rule changes, and delete rules that never earned evidence. Use weekly, or when they say "what is working", "why do people leave", "audit my retention", "should I keep using X".
---

# loop

This is the only skill that makes the system better over time. Everything else makes one video.

## Steps
1. **Get the curve.** Export `analytics/<video>.csv` with `t_s,retention` (or `t_s,viewers`) from YouTube
   Analytics (Audience retention, absolute or relative - relative is easier). One file per video.
2. **Correlate.**
   ```bash
   sutra loop analytics/<video>.csv --timeline videos/<name>/plan/timeline.json --out analytics/<name>_loop.md
   ```
3. **Read the report as a table, not a story.** Kinds are ranked worst to best by mean retention delta per 5s.
   Ignore any kind with fewer than 2 appearances - that is noise, and say so.
4. **Propose, do not decide.** For each proposal, state: kind, uses, mean delta, the worst timestamp, and the
   smallest edit that would test the hypothesis (not the biggest rewrite).
5. **Only after "lock it"**: move the rule into `brand/rules.md` Locked with the date and the evidence row.
6. **Delete losers.** A rule that has survived 3 videos with no positive evidence goes to the Deleted table with a
   date and a reason. Deleting a rule is the highest-value action in this skill.
7. **Report one number per video**: percent of retention lost to kinds that could have been avoided. Trend that.

## Done when
- [ ] every drop-off > 5% in 5s is attributed to a shot kind and a timestamp
- [ ] proposals cite appearance counts, not adjectives
- [ ] the Deleted table was reviewed - something was removed, or a reason was written for why not
- [ ] `analytics/<name>_loop.md` exists and is linked from the video's row in `research/ideas.md`
