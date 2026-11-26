# Launch day

Repo: **https://github.com/oathanrex/sutradhar** · version `v1.2.1`

## What the first push proved

| run | result | meaning |
|---|---|---|
| `v1.0.0` | green | the tag was pushed before the new CI steps existed |
| `main`, `v1.1.0`, `v1.2.0` | **red** | two real bugs, both fixed in `v1.2.1` |
| `render the preview` job | green on every run | the demo render + the render-dependent gates work on a clean runner |

**Bug 1 (all OS):** `sutra evidence` exited 1 while the packs were unmeasured, so the step "packs must declare
their evidence" failed the build. A CI gate must check the *declaration*, not demand the research.
Now: exit 0 while unmeasured, `--strict` when you do want it to fail.

**Bug 2 (Windows only):** the CLI tests ran subprocesses with a stripped environment. On Windows that removes
`SYSTEMROOT` and Python cannot start, so every CLI test failed. Now the environment is inherited and only
`PYTHONPATH` is added.

This is what a 3-OS matrix is for: two of the six jobs found a bug that Linux never would.

## Settings to paste in GitHub (2 minutes)

**Settings → General → Description**
> One thread from research to retention: research, script, edit and gate video in code. 8 agent skills, 10 category packs, 6 locales, 4 formats, 7 publish gates. Zero dependencies in the core.

**Topics** (Settings → same page)
```
video-editing, youtube, ai-agents, claude-code, antigravity, hyperframes, agent-skills,
video-workflow, retention, hinglish, tamil, bengali, python, mit-license
```

Or with the `gh` CLI:
```bash
gh repo edit oathanrex/sutradhar \
  --description "One thread from research to retention: research, script, edit and gate video in code. 8 agent skills, 10 category packs, 6 locales, 4 formats, 7 publish gates." \
  --add-topic video-editing,youtube,ai-agents,claude-code,antigravity,hyperframes,agent-skills,video-workflow,retention,hinglish,tamil,bengali,python
```

## First week checklist

- [ ] CI green on `main` (the badge in the README must not be red — that is the first thing a stranger sees)
- [ ] `docs/demo.mp4` plays from the repo page
- [ ] pin an issue: "Measured packs: 0/10" — make the honest gap public, it is the best possible first issue
- [ ] README "60 seconds of proof" block matches the actual output on a clean clone
- [ ] release `v1.2.1` on GitHub Releases with the changelog section pasted in
- [ ] reply to the first three issues within a day; the repo's tone is set by the first reply

## What NOT to do this week

Do not add features. The repo's weakest point is not code — it is that **no video made with it exists yet**.
A red badge and 0 stars are fine on day one; a repo that grows features while nothing ships is the real failure.
