import argparse, json, pathlib, sys
from . import __version__
from .util import ROOT, jload, jdump, ok, warn, fail, table

def _R(a):
    from .resolve import resolve
    return resolve(a.pack, a.locale, a.format, brand_path=a.brand)

def main(argv=None):
    ap = argparse.ArgumentParser("sutra", description="the thread from research to retention")
    ap.add_argument("--version", action="version", version=f"sutra {__version__}")
    sub = ap.add_subparsers(dest="cmd")

    def add_common(p):
        p.add_argument("--pack"); p.add_argument("--locale", default="en"); p.add_argument("--format", default="long-16x9")
        p.add_argument("--brand", default=None)

    p = sub.add_parser("doctor", help="check the toolchain"); p.set_defaults(fn=cmd_doctor)
    p = sub.add_parser("resolve", help="print the merged config and where each value came from"); add_common(p); p.set_defaults(fn=cmd_resolve)
    p = sub.add_parser("init", help="scaffold a video project"); p.add_argument("name"); add_common(p); p.set_defaults(fn=cmd_init)
    p = sub.add_parser("pack", help="list / show category packs"); p.add_argument("action", nargs="?", default="list"); p.add_argument("id", nargs="?")
    p.add_argument("--locale", default="en"); p.add_argument("--format", default="long-16x9"); p.set_defaults(fn=cmd_pack)
    p = sub.add_parser("check", help="validate brand, spec, packs, timeline"); p.add_argument("what", nargs="?", default="all")
    p.add_argument("--timeline"); p.add_argument("--brand", default=None); p.set_defaults(fn=cmd_check)
    p = sub.add_parser("spec", help="extract or verify the style spec"); p.add_argument("action", choices=["extract", "verify"])
    p.add_argument("timeline", nargs="?"); p.add_argument("--from", nargs="*", default=[]); p.add_argument("--out"); p.set_defaults(fn=cmd_spec)
    p = sub.add_parser("gate", help="run the five gates"); p.add_argument("gate", nargs="?", default="all")
    p.add_argument("--timeline", default="plan/timeline.json"); p.add_argument("--render"); add_common(p); p.set_defaults(fn=cmd_gate)
    p = sub.add_parser("loop", help="retention curve -> shot kind -> rule proposals")
    p.add_argument("curve"); p.add_argument("--timeline", default="plan/timeline.json"); p.add_argument("--out", default="analytics/loop_report.md")
    p.set_defaults(fn=cmd_loop)
    p = sub.add_parser("library", help="index media with licences"); p.add_argument("action", nargs="?", default="index")
    p.add_argument("--root", default="."); p.set_defaults(fn=cmd_library)
    p = sub.add_parser("stats", help="measured numbers for a timeline"); p.add_argument("--timeline", default="plan/timeline.json")
    p.set_defaults(fn=cmd_stats)

    a = ap.parse_args(argv)
    if not getattr(a, "fn", None):
        ap.print_help(); return 0
    return a.fn(a)

def cmd_doctor(a):
    from .doctor import run; sys.exit(1 if run() else 0)

def cmd_resolve(a):
    R = _R(a)
    print(json.dumps(R.as_dict(), indent=2)); return 0

def cmd_init(a):
    from .init import video
    video(a.name, a.pack or "tutorial", a.locale, a.format, brand=a.brand); return 0

def cmd_pack(a):
    from .util import jload
    packs = sorted((ROOT / "packs").glob("*.json"))
    if a.action == "list" or not a.id:
        rows = [(p.stem, jload(p)["name"], len(jload(p)["structure"]), len(jload(p)["retention_risks"])) for p in packs]
        table(rows, ["pack", "category", "beats", "risks"], [20, 34, 6, 6]); return 0
    R = _R(a)
    print(json.dumps({k: R.get(k) for k in ("structure", "shot_mix", "retention_risks", "hook_patterns", "never")}, indent=2))
    return 0

def cmd_check(a):
    from . import validate
    from .util import jload
    bad = 0
    checks = {"all": ["design", "packs", "spec", "timeline"], "brand": ["design"], "packs": ["packs"],
              "spec": ["spec"], "timeline": ["timeline"]}[a.what if a.what in ("brand", "packs", "spec", "timeline") else "all"]
    if "design" in checks:
        d = jload((pathlib.Path(a.brand) if a.brand else ROOT / "brand" / "design.json"))
        errs = validate.design(d) if d else ["brand/design.json missing: say 'build my brand'"]
        print(f"  brand      {'ok' if not errs else 'FAIL'}"); [fail(e) for e in errs]; bad += len(errs)
    if "spec" in checks:
        s = jload(ROOT / "brand" / "style.spec.json")
        errs = validate.spec(s) if s else []
        if not s: print("  spec       (none yet - optional until you extract one)")
        else: print(f"  spec       {'ok' if not errs else 'FAIL'}"); [fail(e) for e in errs]; bad += len(errs)
    if "packs" in checks:
        errs = []
        for p in sorted((ROOT / "packs").glob("*.json")): errs += validate.pack(jload(p))
        print(f"  packs      {'ok' if not errs else 'FAIL'} ({len(list((ROOT/'packs').glob('*.json')))} packs)")
        [fail(e) for e in errs]; bad += len(errs)
    if "timeline" in checks and a.timeline:
        t = jload(a.timeline); errs = validate.timeline(t) if t else [f"{a.timeline} not found"]
        print(f"  timeline   {'ok' if not errs else 'FAIL'}"); [fail(e) for e in errs]; bad += len(errs)
    print(); print("  all clear" if not bad else f"  {bad} problem(s)")
    return 1 if bad else 0

def cmd_spec(a):
    from . import spec as S
    if a.action == "extract":
        out = a.out or str(ROOT / "brand" / "style.spec.json")
        jdump(out, S.extract_from_playlist(a.__dict__.get("from") or []))
        ok(f"wrote {out} - now replace every number with your own measured value"); return 0
    rows, fails = S.verify(jload(ROOT / "brand" / "style.spec.json"), jload(a.timeline or "plan/timeline.json"))
    if not rows: fail(fails[0] if fails else "nothing to verify"); return 1
    table([(m, w, g, d, v, e) for m, w, g, d, v, e in rows], ["metric", "spec", "measured", "delta", "verdict", "evidence"], [26, 8, 10, 10, 8, 12])
    for f in fails: fail(f)
    return 1 if fails else 0

def cmd_gate(a):
    from . import gates
    R = _R(a); tl = jload(a.timeline)
    if not tl: fail(f"{a.timeline} not found"); return 2
    spec = jload(ROOT / "brand" / "style.spec.json")
    out = gates.run_all(tl, R, spec=spec, render=a.render, root=ROOT)
    table([(n, r["status"], r["detail"]) for n, r in out], ["gate", "state", "detail"], [8, 6, 72])
    bad = 0
    for n, r in out:
        if r["status"] == "FAIL":
            bad += 1
            for o in r["offenders"][:8]: fail(f"{n}: {o}")
    print(); print("  all gates pass" if not bad else f"  {bad} gate(s) failing - fix before publishing")
    return 1 if bad else 0

def cmd_loop(a):
    from .retention import correlate
    rows, props, md = correlate(a.curve, a.timeline, a.out)
    table(rows, ["kind", "uses", "mean %/5s", "worst", "verdict"], [18, 6, 12, 16, 16])
    ok(f"report: {a.out} ({len(props)} rule proposal(s))"); return 0

def cmd_library(a):
    from .library import index
    added, total, unlic = index(a.root)
    ok(f"{added} new asset(s), {total} total")
    for u in unlic[:20]: warn(f"no licence: {u}  -> add a row to library/licenses.csv")
    return 0

def cmd_stats(a):
    from .spec import stats
    s = stats(jload(a.timeline)); table([(k, v) for k, v in s.items() if k != "shot_mix"], ["metric", "value"], [26, 20])
    print(); print("  shot mix:"); [print(f"    {k:<16} {v}") for k, v in s["shot_mix"].items()]; return 0

if __name__ == "__main__":
    sys.exit(main())
