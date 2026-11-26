# library/

Every file the edit can put on screen. One rule: **no licence, no entry.** `sutra library index` refuses to
mark a file usable until `licenses.csv` has a row for it, and the `legal` gate fails the render if any shot
points at something that is not in here.

```
library/
  manifest.json     # generated: path, kind, duration, w/h, sha1, tags, license, source
  licenses.csv      # you write this: path,license,source  (original | CC0 | CC-BY | licensed | brand)
  broll/  screens/  gifs/  sfx/  music/
```

Paths in `plan/timeline.json` are relative to `library/`, e.g. `broll/desk.mp4`.

`sutra library index` adds new files and lists anything still missing a licence. Re-run it whenever you add media.
