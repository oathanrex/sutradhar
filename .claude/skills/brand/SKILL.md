---
name: brand
description: Build or update the creator's brand system by grilling them one decision at a time - colours, fonts, captions, sound, pace, never-list - then write brand/design.json, brand/style.spec.json, brand/rules.md and brand/about_me/. Use on first setup, when they say "build my brand", "set up my design system", "make it mine", or when a second channel needs its own look.
---

# brand

Output is four files, not a conversation. If the files are not written and validating, this skill failed.

| file | holds | who reads it |
|---|---|---|
| `brand/design.json` | colours, fonts, max_hold, caption case, sfx list | every tool |
| `brand/style.spec.json` | the numbers a render must hit | `sutra spec verify` |
| `brand/rules.md` | dated rules with evidence, the Never list | every skill |
| `brand/about_me/*.md` | who they are, how they work, voice samples | research, script |

## 0. Import before you ask
Read `brand/design.json`, `brand/rules.md`, `brand/about_me/`, `README.md`, any `CLAUDE.md`/`AGENTS.md`, any
`design.md` or style guide anywhere in the project, and any HyperFrames `frame.md`. If a brand already exists,
show what you found as a table and ask only for corrections. **Never ask a question the repo already answers.**

## 1. Ask, one decision at a time, with options
Ask with a question tool where available so they click, not type. Every question has 3-4 concrete options and
your recommended one first. Stop the round when the frontier is empty, not when it feels long.

1. **Category** - which pack? Run `sutra pack list`. Their answer sets every default after this.
   (`tutorial, tool-review, faceless-explainer, finance, education, talking-head, story, vlog, comedy, gaming`)
2. **Locale** - `en`, `hi`, `hinglish`. This is not cosmetic: it changes the whisper model, caption width,
   line height and whether caps are legal at all. `hinglish` means captions are written as spoken, Roman stays Roman.
3. **Format(s)** - long-form, shorts, or both.
4. **Background** - dark, light, paper/texture. Show three swatches with their real channel name on each.
5. **Accent** - one colour, four options, on their background. Ask if a second colour is ever allowed, and when.
6. **Text colour** - state the measured contrast ratio. Below 4.5:1, refuse and offer the two nearest passing values.
7. **Fonts** - max 3 (title, body, mono). Free only unless they hold a licence. If `hi`/`hinglish`, the title font
   MUST have Devanagari coverage with a fallback stack, and you say which file to install.
8. **Big text style** - flat, gradient, outline, glow. Show each on their accent.
9. **Captions** - on/off, one or two lines, word highlight or static, position. Caps only if the locale allows it.
10. **Sound** - which effects, and the loudness rule. List `library/sfx/` and name what is missing. Do not download
    anything for them; give the exact search term and licence they need.
11. **Pace** - how often something new appears on screen. Save it as `max_hold`. Refuse unsafe pairs
    ("calm channel" + "cut every 0.8s") and make them choose.
12. **Never list** - flashing, glitch transitions, stock-photo people, more than one thing moving, anything else.
13. **Who they are** - run `about_me` in the same session: goals with numbers, one ideal viewer, 2-3 of their own
    old scripts pasted into `voice.md` as evidence.

## 2. Write
- `design.json` - only real measured values. Add `caption_case` (UPPER / NATIVE / sentence).
- `style.spec.json` - copy the schema from `brand/style.spec.json`; every number in `evidence` cites either a count
  from a reference video or the creator's explicit answer. **No invented numbers. Unmeasurable -> omit the key.**
- `rules.md` - one dated line per decision with one line of why, then the Never list.
- `about_me/*.md` - under 60 lines each, dated.

## 3. Verify, then show
```bash
sutra check brand          # contrast, required keys, hex format
sutra resolve --pack <pack> --locale <locale> --format <format>
```
`resolve` prints where every value came from. Paste the warnings verbatim - especially the Devanagari ones.
Then render a one-page style guide as an HTML artifact: swatches, font sample at real size, a sample caption
frame, a sample thumbnail, the Never list.

## Done when
- [ ] `sutra check brand` is clean
- [ ] `sutra resolve` warnings are either fixed or explicitly accepted by the creator
- [ ] every sfx named in `design.json` has a file in `library/sfx/`, or is removed
- [ ] `about_me/voice.md` contains at least two of their own sentences
- [ ] the style guide artifact was shown, not described

## Refuse
Running a render while `design.json` still holds template values. Saying "looks great" without a contrast number.
Writing a rule that has no evidence line.
