# Running sutradhar on Google Antigravity

Antigravity is Google's agentic IDE (free tier, macOS/Windows/Linux, Gemini 4 models, plugins and MCP apps).
It reads `.agents/skills` and an agent instruction file. This page is the whole setup.

## 1. One-time setup

```bash
# Antigravity itself
open https://antigravity.google           # download, sign in with a Google account, free tier is enough

# What Antigravity does not ship
winget install Gyan.FFmpeg                 # Windows   (macOS: brew install ffmpeg)
winget install OpenJS.NodeJS               # Node 22+  (macOS: brew install node)

# The repo
cd ~/sutradhar
make sync                                  # .claude/skills -> .agents/skills (creates .agents first)
make test                                  # 21 tests, no network
make doctor                                # what is still missing, and the command that fixes it
```

`make sync` exists because the one-line `cp -r .claude/skills .agents/skills` that most repos print fails on a
fresh clone — `.agents/` does not exist yet.

## 2. Open the right folder

Open **`~/sutradhar`**, not a subfolder. Antigravity's agent works inside the folder you open; if you open
`tools/`, it cannot see `brand/` and every skill will ask you the same questions again.

First message in the chat:

> `read AGENTS.md first, then list the 8 skills you can see in .agents/skills and one line on what each produces.
> Do not read tests/ or docs/. Do not change any file.`

That single message fixes 90% of "the agent is ignoring my rules".

## 3. The three instruction files

| file | who reads it |
|---|---|
| `AGENTS.md` | the canonical source — edit only this one |
| `CLAUDE.md`, `GEMINI.md` | mirrors for Claude Code / Gemini CLI, CI fails if they drift |

They are byte-identical on purpose. `diff AGENTS.md CLAUDE.md` must be empty.

## 4. Prompt patterns that work in Antigravity

**Give it the read list, not the whole repo.** Context is the expensive resource.

> `Read only: AGENTS.md, brand/design.json, brand/style.spec.json, and plan/brief.md. Then answer.`

**Ask for the command, then run it yourself if you prefer.** Every skill ends in a verification command, so
"trust me" is never required:

> `Before you claim it works, run it and paste the raw output. If the command fails, say so — do not summarise.`

**One skill per message.** Antigravity is good at a scripted sequence and bad at "do everything at once".
The 8 prompts in `video-kit/01-prompts.txt` are ordered for this reason.

**Stop points are explicit.** Say "show me X and stop" for the storyboard and for the gate table. An agent that
renders before you approve the storyboard is an agent you cannot correct cheaply.

## 5. Free tier reality

- Antigravity: usable free, with rate limits. Long agentic loops hit the limit; the skills are written to be
  short and verifiable so a limit costs you a retry, not a session.
- HyperFrames CLI: free (Apache-2.0). Its Studio Pro plan ($25/mo) only matters for hosted rendering and
  premium models — the pipeline here renders locally with `npx hyperframes`.
- ffmpeg, whisper (`faster-whisper`), Python: free.
- The real cost is your time: two hours for the first video, ~40 minutes after that.

## 6. Plugins

Antigravity has a plugin ecosystem and MCP app support. Two are worth it:
**Canva** (the research skill can write the ideas table and breakdown docs there) and any MCP server that gives
the agent ears (e.g. `earshot`) — it turns "inferred from cut points" into a real measurement.

## 7. Troubleshooting

| symptom | cause | fix |
|---|---|---|
| skills are not visible | `.agents/skills` missing or stale | `make sync` |
| agent re-asks questions it already answered | it did not read `brand/` | quote the read list above |
| agent wants to install HyperFrames for you | it should not | skills say: point the creator at the source and pin the version |
| "cannot write file" | workspace permission | keep the project inside the opened folder |
| rate limit | free tier | wait 1-2 min, or split the skill into two messages |
| garbled Hindi transcript | wrong model | `--locale hi` → `whisper large-v3`; never `small.en` on Hindi audio |
| render fails | HyperFrames moved | `npx hyperframes check`, then pin the version in `package.json` |

## 8. The full sequence, in one line each

```
1  read AGENTS.md, list the skills
2  brand skill, verify-only           -> brand/design.json validated, warnings paid off
3  plan skill for the video           -> videos/<name>/plan/brief.md
4  research skill on 3 reference vids -> proposed rules with evidence
5  script skill                       -> videos/<name>/script.md
6  edit skill: voiceover -> timeline  -> plan/timeline.json (the contract)
7  edit skill: storyboard  ✋ STOP    -> storyboard.jpg, approved by you
8  render v01, then gate skill  ✋    -> 5 PASS, or the exact timestamp of each FAIL
9  loop skill, 7 days later           -> one rule locked, one rule deleted
```
