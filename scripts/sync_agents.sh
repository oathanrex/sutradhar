#!/usr/bin/env bash
# Mirror .claude/skills into .agents/skills for Antigravity / Gemini CLI.
# The old one-line `cp -r .claude/skills .agents/skills` fails on a fresh clone because .agents/ does not
# exist yet. This creates it first, then mirrors, and reports what it did.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$root/.agents/skills"
cp -R "$root/.claude/skills/." "$root/.agents/skills/"
n=$(find "$root/.agents/skills" -name SKILL.md | wc -l | tr -d ' ')
echo "mirrored $n skills -> .agents/skills"
echo "now tell the agent: read AGENTS.md first"
