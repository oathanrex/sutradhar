"""The whole engine is testable without HyperFrames, ffmpeg or a GPU. That is the point."""
import json, pathlib, sys, tempfile, unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from sutra import validate, gates, spec as specmod
from sutra.resolve import resolve
from sutra.retention import correlate
from sutra.library import index

FIX = pathlib.Path(__file__).parent / "fixtures" / "proj"
def load(p): return json.loads((FIX / p).read_text())

class TestValidate(unittest.TestCase):
    def test_good_design_passes(self):
        self.assertEqual(validate.design({"background": "#0E0F12", "text": "#F4F4F2", "accent": "#F2C200",
                                          "font_title": "A", "font_body": "A", "max_hold": 5}), [])
    def test_low_contrast_is_rejected(self):
        e = validate.design({"background": "#FFFFFF", "text": "#EEEEEE", "accent": "#FFFF00",
                             "font_title": "A", "font_body": "A", "max_hold": 5})
        self.assertTrue(any("contrast" in x for x in e), e)
    def test_missing_keys_are_named(self):
        e = validate.design({"background": "#000000"})
        self.assertGreaterEqual(len(e), 5)
    def test_timeline_overlap_is_caught(self):
        tl = load("plan/timeline.json"); tl["shots"][1]["start_s"] = 1.0
        self.assertTrue(any("overlaps" in x for x in validate.timeline(tl)))
    def test_media_kind_needs_media(self):
        tl = load("plan/timeline.json"); tl["shots"][1]["media"] = []
        self.assertTrue(any("needs a media file" in x for x in validate.timeline(tl)))
    def test_every_pack_validates(self):
        root = pathlib.Path(__file__).resolve().parents[1] / "packs"
        for p in sorted(root.glob("*.json")):
            self.assertEqual(validate.pack(json.loads(p.read_text())), [], p.name)

class TestResolve(unittest.TestCase):
    def test_pack_locale_format_layer_in_order(self):
        R = resolve("tutorial", "en", "long-16x9")
        self.assertEqual(R.get("pacing.cuts_per_min"), 22)
        self.assertEqual(R.why("pacing.cuts_per_min"), "pack:tutorial")
        self.assertEqual(R.get("safe.top_pct"), 8)
        self.assertEqual(R.why("safe.top_pct"), "format:long-16x9")
    def test_portrait_multiplies_pace(self):
        a = resolve("tutorial", "en", "long-16x9"); b = resolve("tutorial", "en", "portrait-9x16")
        self.assertLess(b.get("pacing.max_hold_s"), a.get("pacing.max_hold_s"))
        self.assertGreater(b.get("pacing.cuts_per_min"), a.get("pacing.cuts_per_min"))
        self.assertEqual(b.why("pacing.cuts_per_min"), "format:portrait-9x16")
    def test_hindi_blocks_caps_and_shrinks_lines(self):
        R = resolve("education", "hi", "long-16x9")
        self.assertLessEqual(R.get("text.max_chars_per_line"), 28)
        self.assertEqual(R["caption"]["case"], "NATIVE")
        self.assertTrue(any("no upper case" in w for w in R.warnings))
    def test_latin_font_warns_on_devanagari(self):
        R = resolve("education", "hinglish", "long-16x9")
        self.assertTrue(any("Devanagari" in w for w in R.warnings), R.warnings)
    def test_all_packs_all_locales_all_formats_resolve(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        for p in ["tutorial", "tool-review", "faceless-explainer", "finance", "education",
                  "talking-head", "story", "vlog", "comedy", "gaming"]:
            for loc in ["en", "hi", "hinglish"]:
                for fmt in ["long-16x9", "portrait-9x16"]:
                    R = resolve(p, loc, fmt)
                    self.assertGreater(R.get("pacing.cuts_per_min"), 0)

class TestSpec(unittest.TestCase):
    def test_demo_timeline_matches_template_spec(self):
        spec = json.loads((pathlib.Path(__file__).resolve().parents[1] / "brand" / "style.spec.json").read_text())
        rows, fails = specmod.verify(spec, load("plan/timeline.json"))
        self.assertEqual(fails, [], rows)
    def test_drift_fails(self):
        tl = load("plan/timeline.json")
        for s in tl["shots"]: s["end_s"] *= 3; s["start_s"] *= 3
        tl["duration_s"] *= 3
        _, fails = specmod.verify(json.loads((pathlib.Path(__file__).resolve().parents[1] / "brand" / "style.spec.json").read_text()), tl)
        self.assertTrue(fails)
    def test_stats(self):
        st = specmod.stats(load("plan/timeline.json"))
        self.assertAlmostEqual(st["cuts_per_min"], 22.0, delta=0.5)
        self.assertEqual(st["shots"], 12)

class TestGates(unittest.TestCase):
    def setUp(self):
        self.R = resolve("tutorial", "en", "long-16x9"); self.tl = load("plan/timeline.json")
        self.spec = json.loads((pathlib.Path(__file__).resolve().parents[1] / "brand" / "style.spec.json").read_text())
    def test_all_gates_pass_on_demo(self):
        needs_a_render = {"audio", "words", "flash"}
        for name, r in gates.run_all(self.tl, self.R, spec=self.spec, root=FIX):
            if name in needs_a_render:
                self.assertEqual(r["status"], "SKIP", f"{name}: a gate must never invent a PASS")
                continue
            self.assertEqual(r["status"], "PASS", f"{name}: {r}")
    def test_late_first_cut_fails_hook(self):
        tl = dict(self.tl); tl["shots"] = [dict(s) for s in tl["shots"]]
        tl["shots"][0]["end_s"] = 3.0; tl["shots"][1]["start_s"] = 3.0
        self.assertEqual(gates.hook(tl, self.R)["status"], "FAIL")
    def test_long_line_fails_mobile(self):
        tl = dict(self.tl); tl["shots"] = [dict(s) for s in tl["shots"]]
        tl["shots"][0]["text"] = ["THIS LINE IS FAR TOO LONG TO READ ON A PHONE"]
        r = gates.mobile(tl, self.R); self.assertEqual(r["status"], "FAIL"); self.assertTrue(r["offenders"])
    def test_unlicensed_media_fails_legal(self):
        tl = dict(self.tl); tl["shots"] = [dict(s) for s in tl["shots"]]
        tl["shots"][1]["media"] = ["broll/unknown.mp4"]
        self.assertEqual(gates.legal(tl, root=FIX)["status"], "FAIL")
    def test_audio_skips_without_render(self):
        self.assertEqual(gates.audio(None, self.R)["status"], "SKIP")

class TestRetentionLoop(unittest.TestCase):
    def test_expensive_kind_gets_proposal(self):
        tmp = pathlib.Path(tempfile.mkdtemp())
        tl = {"version": "1.0", "video": "t", "format": "long-16x9", "duration_s": 30.0, "shots": [
            {"start_s": 0, "end_s": 5, "kind": "screen"}, {"start_s": 5, "end_s": 10, "kind": "chips"},
            {"start_s": 10, "end_s": 15, "kind": "screen"}, {"start_s": 15, "end_s": 20, "kind": "chips"},
            {"start_s": 20, "end_s": 25, "kind": "screen"}, {"start_s": 25, "end_s": 30, "kind": "chips"}]}
        (tmp / "tl.json").write_text(json.dumps(tl))
        vals = {0: 100, 1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 96, 7: 92, 8: 88, 9: 84, 10: 80,
                11: 80, 12: 80, 13: 80, 14: 80, 15: 80, 16: 72, 17: 68, 18: 64, 19: 60, 20: 55,
                21: 55, 22: 55, 23: 55, 24: 55, 25: 55, 26: 48, 27: 45, 28: 42, 29: 39, 30: 36}
        (tmp / "curve.csv").write_text("t_s,retention\n" + "\n".join(f"{k},{v}" for k, v in vals.items()))
        rows, props, md = correlate(tmp / "curve.csv", tmp / "tl.json", tmp / "r.md")
        self.assertTrue((tmp / "r.md").exists())
        kinds = {r[0]: r[2] for r in rows}
        self.assertLess(kinds["chips"], kinds["screen"])
        self.assertTrue(any(p["kind"] == "chips" and p["verdict"] == "cut or shorten" for p in props), props)
        self.assertFalse(any(p["kind"] == "screen" for p in props), props)

class TestLibrary(unittest.TestCase):
    def test_licence_is_required(self):
        tmp = pathlib.Path(tempfile.mkdtemp()); (tmp / "library").mkdir()
        (tmp / "library" / "a.png").write_bytes(b"x"); (tmp / "library" / "b.mp4").write_bytes(b"y")
        (tmp / "library" / "licenses.csv").write_text("path,license,source\nlibrary/a.png,original,my own screen\n")
        added, total, unlic = index(tmp)
        self.assertEqual((added, total), (2, 2)); self.assertEqual(unlic, ["library/b.mp4"])
        man = json.loads((tmp / "library" / "manifest.json").read_text())
        self.assertEqual(next(a for a in man["assets"] if a["path"].endswith("a.png"))["license"], "original")
        self.assertIsNone(next(a for a in man["assets"] if a["path"].endswith("b.mp4"))["license"])

if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestCrossPlatform(unittest.TestCase):
    """Windows is the majority of this audience. A manifest written there must still match a timeline."""

    def test_manifest_written_on_windows_still_matches(self):
        tmp = pathlib.Path(tempfile.mkdtemp())
        (tmp / "library" / "broll").mkdir(parents=True)
        (tmp / "library" / "broll" / "desk.mp4").write_bytes(b"x")
        added, total, unlic = index(tmp)
        self.assertEqual(added, 1)
        man = json.loads((tmp / "library" / "manifest.json").read_text())
        path = man["assets"][0]["path"]
        self.assertNotIn("\\", path, "manifest paths must use forward slashes on every OS")
        self.assertEqual(path, "library/broll/desk.mp4")
        # a manifest authored on Windows (backslashes) must still satisfy the legal gate
        man["assets"][0]["path"] = "library\\broll\\desk.mp4"
        man["assets"][0]["license"] = "original"
        man["assets"][0]["source"] = "own camera"
        (tmp / "library" / "manifest.json").write_text(json.dumps(man))
        tl = {"version": "1.0", "video": "t", "format": "long-16x9", "duration_s": 4.0,
              "shots": [{"start_s": 0, "end_s": 4, "kind": "full", "media": ["broll/desk.mp4"]}]}
        self.assertEqual(gates.legal(tl, root=tmp)["status"], "PASS")
