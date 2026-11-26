export PYTHONPATH := tools
S := python3 -m sutra
VIDEO ?= demo-30s

.PHONY: help test check demo gates spec doctor sync matrix clean
help:
	@echo "sutradhar"
	@echo "  make test     run the suite (no network, no GPU, no ffmpeg needed)"
	@echo "  make check    validate brand, all packs, the spec, the demo timeline"
	@echo "  make demo     print the resolved config for the demo video"
	@echo "  make gates    run the five publish gates on the demo timeline"
	@echo "  make spec     verify the demo timeline against brand/style.spec.json"
	@echo "  make matrix   resolve every pack x locale x format combination"
	@echo "  make doctor   what is missing on this machine, and the fix"
	@echo "  make sync     mirror .claude/skills into .agents/skills (Antigravity / Gemini)"

test:
	@python3 -m unittest discover -s tests -v 2>&1 | tail -5

check:
	@$(S) check --timeline examples/$(VIDEO)/plan/timeline.json

demo:
	@$(S) resolve --pack tutorial --locale en --format long-16x9 | head -40
	@echo "... provenance for the rest: sutra resolve --pack tutorial | grep -A200 provenance"

gates:
	@$(S) gate --timeline examples/$(VIDEO)/plan/timeline.json --pack tutorial

spec:
	@$(S) spec verify examples/$(VIDEO)/plan/timeline.json

matrix:
	@python3 scripts/matrix.py

doctor:
	@$(S) doctor || true

sync:
	@bash scripts/sync_agents.sh

clean:
	@find . -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null; echo cleaned
