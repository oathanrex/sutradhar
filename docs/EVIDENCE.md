# Evidence — how a pack number earns the right to exist

The whole point of this repo is that numbers come from somewhere. That rule now applies to the repo itself:
**all 10 packs ship with `"measured": false` and an empty `evidence` list.** They are starting defaults chosen
from each category's conventions, and they say so in their own `note` field.

Filling them is a 10-minute job per category, and the tooling refuses to fake it.

## The protocol

For each category, pick **3 videos that over-performed for their own channel** (not 3 famous videos — famous
channels are not evidence), then measure:

| number | how |
|---|---|
| **cuts per minute** | count visible cuts in the first 3 minutes, divide by the minutes |
| **longest shot** | the longest hold that still felt fine |
| **characters on screen** | the widest line readable at 320 px wide |
| **sound effects per minute** | count them; do not estimate |

Then attach the three videos:

```bash
sutra evidence add --pack tool-review --video https://youtu.be/XXXX --views 214000 --median 48000
# -> "tutorial: 4.46x outlier from https://youtu.be/XXXX (1/3 rows)"
```

`channel_median` is the median views of that channel's last ~30 uploads. `outlier_x = views / median` is computed,
never typed. At 3 rows the pack flips to `"measured": true`.

## Then change the numbers

`sutra pack show tool-review` prints the current numbers. If your measurement disagrees with them, edit
`packs/<id>.json` and put the source in `note`:

```json
"note": "cuts/min 26 measured on 3 tool reviews, Nov 2026; sfx/min raised from 8 to 11 after counting."
```

## Why this is enforced, not suggested

`validate.pack` fails on:
- a pack with no `evidence` key at all
- an evidence row missing `video`, `views`, `channel_median`, `outlier_x` or `measured_on`
- an `outlier_x` that does not equal `views / channel_median`
- `"measured": true` with an empty evidence list

CI runs `sutra evidence` on every push, so an unmeasured pack is visible in the build log, never quietly assumed.

## Current state (be honest in your own fork)

| pack | state |
|---|---|
| all 10 | **UNMEASURED** — 0/3 rows |

That is the honest position on the day this file was written. `sutra evidence` is the scoreboard, and it should
never be green because someone edited a JSON file by hand.
