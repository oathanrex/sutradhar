"""Tests for v1.1: the builder, the real words gate, evidence, statistics, pixels, API parsing, CLI surface."""
import json, os, pathlib, subprocess, sys, tempfile, unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from sutra import validate, gates, evidence, analytics
from sutra.build import build, check_html, render_player, render_hyperframes
from sutra.resolve import resolve
from sutra.retention import correlate, bootstrap_ci, aggregate, decide
from sutra.visual import flash_rate

FIX = ROOT / "tests" / "fixtures" / "proj"
DEMO = ROOT / "examples" / "demo-30s" / "plan" / "timeline.json"


def load(p):
    return json.loads(pathlib.Path(p).read_text())


class TestBuild(unittest.TestCase):
    def setUp(self):
        self.R = resolve("tutorial", "en", "long-16x9")
        self.tl = load(DEMO)
        self.out = pathlib.Path(tempfile.mkdtemp())

    def test_writes_player_composition_and_receipt(self):
        rec = build(DEMO, self.out, self.R)
        for f in ("index.html", "hyperframes.html", "receipt.json"):
            self.assertTrue((self.out / f).exists(), f)
        self.assertEqual(rec["structural_problems"], [], rec["structural_problems"])
        self.assertEqual(rec["timeline"]["shots"], len(self.tl["shots"]))
        self.assertEqual(len(rec["assets"]), len({m for s in self.tl["shots"] for m in (s.get("media") or [])}))

    def test_receipt_hashes_are_content_not_mtime(self):
        a = build(DEMO, self.out, self.R)["timeline"]["sha256_16"]
        b = build(DEMO, self.out, self.R)["timeline"]["sha256_16"]
        self.assertEqual(a, b)
        self.assertRegex(a, r"^[0-9a-f]{16}$")

    def test_every_shot_is_a_timed_element(self):
        import re
        hf = render_hyperframes(self.tl, self.R, "t")
        clips = re.findall(r'data-start="([\d.]+)" data-duration', hf)
        self.assertEqual(len(clips), len(self.tl["shots"]))
        self.assertEqual([float(x) for x in clips], sorted(float(x) for x in clips))

    def test_text_is_escaped(self):
        tl = json.loads(json.dumps(self.tl))
        tl["shots"][0]["text"] = ["<script>alert(1)</script>"]
        html = render_player(tl, self.R, "t")
        self.assertNotIn("<script>alert(1)", html)
        self.assertIn("&lt;script&gt;", html)

    def test_structural_check_catches_missing_shots(self):
        html = render_hyperframes(self.tl, self.R, "t")
        self.assertNotEqual(check_html(html, 999), [])
        self.assertEqual(check_html(html, len(self.tl["shots"])), [])

    def test_portrait_builds_too(self):
        R = resolve("tutorial", "en", "portrait-9x16")
        rec = build(DEMO, self.out, R)
        self.assertEqual(rec["structural_problems"], [])
        html = (self.out / "hyperframes.html").read_text()
        self.assertIn('data-height="1920"', html)
        self.assertIn("aspect-ratio:1080/1920", (self.out / "index.html").read_text())


class TestWordsGate(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.words = self.tmp / "words.json"
        self.words.write_text(json.dumps([{"words": [
            {"w": "ye", "s": 0.0, "e": 0.2}, {"w": "video", "s": 0.3, "e": 0.6},
            {"w": "free", "s": 0.7, "e": 0.9}, {"w": "hai", "s": 1.0, "e": 1.2}]}]))
        self.render = self.tmp / "r.mp4"
        self.render.write_bytes(b"not really an mp4")

    def test_exact_transcript_passes(self):
        t = lambda: [("ye", 0.0), ("video", 0.3), ("free", 0.7), ("hai", 1.0)]
        r = gates.words(self.render, self.words, transcribe=t)
        self.assertEqual(r["status"], "PASS", r)
        self.assertIn("100.0%", r["detail"])

    def test_swallowed_word_fails_with_timestamp(self):
        t = lambda: [("ye", 0.0), ("video", 0.3), ("hai", 1.0)]
        r = gates.words(self.render, self.words, transcribe=t)
        self.assertEqual(r["status"], "FAIL")
        self.assertTrue(any("free" in o for o in r["offenders"]), r["offenders"])

    def test_broken_transcriber_is_a_skip_not_a_pass(self):
        def boom(): raise RuntimeError("model exploded")
        r = gates.words(self.render, self.words, transcribe=boom)
        self.assertEqual(r["status"], "SKIP")
        self.assertIn("model exploded", r["detail"])

    def test_missing_timings_skips(self):
        self.assertEqual(gates.words(self.render, self.tmp / "nope.json")["status"], "SKIP")


class TestEvidence(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        (self.tmp / "packs").mkdir()
        p = json.loads((ROOT / "packs" / "tutorial.json").read_text())
        p["evidence"], p["measured"] = [], False
        (self.tmp / "packs" / "tutorial.json").write_text(json.dumps(p))
        self._old = evidence.ROOT
        evidence.ROOT = self.tmp

    def tearDown(self):
        evidence.ROOT = self._old

    def test_three_rows_measures_the_pack(self):
        for i, v in enumerate([214000, 96000, 401000]):
            evidence.add("tutorial", f"https://youtu.be/v{i}", v, 48000)
        d = json.loads((self.tmp / "packs" / "tutorial.json").read_text())
        self.assertTrue(d["measured"])
        self.assertEqual(len(d["evidence"]), 3)
        self.assertEqual(d["evidence"][0]["outlier_x"], 4.46)
        self.assertEqual(validate.pack(d), [])

    def test_a_pack_cannot_claim_measured_without_evidence(self):
        p = json.loads((self.tmp / "packs" / "tutorial.json").read_text())
        p["measured"] = True
        self.assertTrue(any("measured" in e for e in validate.pack(p)))

    def test_outlier_must_match_the_division(self):
        p = json.loads((self.tmp / "packs" / "tutorial.json").read_text())
        p["evidence"] = [{"video": "v", "views": 100, "channel_median": 50, "outlier_x": 9.0,
                          "measured_on": "2026-11-26"}]
        p["measured"] = True
        self.assertTrue(any("outlier_x should be 2.0" in e for e in validate.pack(p)))

    def test_duplicate_video_is_refused(self):
        evidence.add("tutorial", "https://youtu.be/x", 1000, 100)
        with self.assertRaises(SystemExit):
            evidence.add("tutorial", "https://youtu.be/x", 1000, 100)


class TestStatistics(unittest.TestCase):
    def _tl(self, kinds):
        shots, t = [], 0.0
        for k in kinds:
            shots.append({"start_s": t, "end_s": t + 5, "kind": k}); t += 5
        return {"version": "1.0", "video": "s", "format": "long-16x9", "duration_s": t, "shots": shots}

    def test_bootstrap_is_deterministic(self):
        self.assertEqual(bootstrap_ci([1, 2, 3, 4]), bootstrap_ci([1, 2, 3, 4]))

    def test_two_uses_is_not_enough(self):
        agg = aggregate([{"kind": "gif", "delta_per_5s": -9.0}, {"kind": "gif", "delta_per_5s": -8.0}])
        props = decide(agg, min_appearances=3)
        self.assertEqual(props, [])
        self.assertIn("need 3", agg[0]["why_not"])

    def test_consistent_drop_proposes(self):
        agg = aggregate([{"kind": "gif", "delta_per_5s": x} for x in (-9.0, -8.6, -9.4)])
        props = decide(agg, min_appearances=3)
        self.assertEqual(len(props), 1)
        self.assertEqual(props[0]["verdict"], "cut or shorten")
        self.assertLess(props[0]["ci"][1], 0)

    def test_noise_does_not_propose(self):
        agg = aggregate([{"kind": "screen", "delta_per_5s": x} for x in (-6.0, 5.0, -1.0)])
        self.assertEqual(decide(agg, min_appearances=3), [])

    def test_tiny_effect_does_not_propose(self):
        agg = aggregate([{"kind": "words", "delta_per_5s": x} for x in (-0.2, -0.1, -0.3)])
        props = decide(agg, min_appearances=3)
        self.assertEqual(props, [])

    def test_report_written_with_ci_column(self):
        tmp = pathlib.Path(tempfile.mkdtemp())
        curve = tmp / "c.csv"
        vals = {}
        for i in range(0, 16):
            vals[i] = 100 - i * 4
        curve.write_text("t_s,retention\n" + "\n".join(f"{k},{v}" for k, v in vals.items()))
        tl_p = tmp / "tl.json"
        tl_p.write_text(json.dumps(self._tl(["gif"] * 3)))
        rows, props, text = correlate(curve, tl_p, tmp / "out.md")
        self.assertIn("95% CI", text)
        self.assertEqual(len(props), 1)


class TestVisual(unittest.TestCase):
    def test_flat_video_has_no_flashes(self):
        self.assertEqual(flash_rate([0.2] * 60, 30)[0], 0.0)

    def test_strobe_is_caught(self):
        lums = []
        for i in range(60):
            lums.append(0.9 if i % 2 == 0 else 0.1)
        rate, at = flash_rate(lums, 30)
        self.assertGreater(rate, 3)

    def test_slow_change_is_fine(self):
        lums = [0.2] * 30 + [0.9] * 30
        self.assertLessEqual(flash_rate(lums, 30)[0], 3)


class TestAnalytics(unittest.TestCase):
    def test_report_is_parsed_to_seconds(self):
        payload = {"columnHeaders": [{"name": "elapsedVideoTimeRatio"},
                                     {"name": "audienceWatchRatio"},
                                     {"name": "relativeRetentionPerformance"}],
                   "rows": [[0.0, 1.0, 1.0], [0.5, 0.62, 1.1], [1.0, 0.31, 0.9]]}
        rows = analytics.retention_rows(payload, 420)
        self.assertEqual(rows[0], (0.0, 100.0))
        self.assertEqual(rows[1][0], 210.0)
        self.assertAlmostEqual(rows[1][1], 62.0, places=2)

    def test_unknown_shape_raises_instead_of_guessing(self):
        with self.assertRaises(analytics.ApiError):
            analytics.retention_rows({"columnHeaders": [{"name": "views"}], "rows": [[1]]}, 60)

    def test_pull_uses_injected_transport(self):
        seen = {}

        def fake_get(url, params, token):
            seen.update(params); seen["token"] = token
            return {"columnHeaders": [{"name": "elapsedVideoTimeRatio"}, {"name": "audienceWatchRatio"}],
                    "rows": [[0.0, 5.0], [1.0, 1.0]]}

        rows = analytics.pull("vid123", 100, token="T", get=fake_get)
        self.assertEqual(seen["filters"], "video==vid123")
        self.assertEqual(seen["token"], "T")
        self.assertEqual(rows[-1], (100.0, 20.0))

    def test_csv_roundtrip(self):
        tmp = pathlib.Path(tempfile.mkdtemp())
        p = analytics.write_csv([(0.0, 100.0), (2.0, 91.5)], tmp / "a.csv")
        self.assertEqual(p.read_text().strip().splitlines()[-1], "2.0,91.5")


class TestCli(unittest.TestCase):
    """The CLI surface, end to end, in a subprocess. Exit codes are the contract."""

    def run_cli(self, *args, cwd=ROOT):
        env = {**os.environ, "PYTHONPATH": str(ROOT / "tools"), "PYTHONUTF8": "1"}
        return subprocess.run([sys.executable, "-m", "sutra", *args], cwd=cwd, env=env,
                              capture_output=True, text=True, encoding="utf-8")

    def test_version(self):
        r = self.run_cli("--version")
        self.assertEqual(r.returncode, 0)
        self.assertIn("sutra", r.stdout)

    def test_pack_list(self):
        r = self.run_cli("pack", "list")
        self.assertEqual(r.returncode, 0)
        for name in ("tutorial", "comedy", "gaming"):
            self.assertIn(name, r.stdout)

    def test_check_is_clean(self):
        r = self.run_cli("check", "--timeline", "examples/demo-30s/plan/timeline.json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_gate_returns_nonzero_on_failure(self):
        tmp = pathlib.Path(tempfile.mkdtemp())
        tl = load(DEMO)
        tl["shots"][0]["text"] = ["THIS LINE IS FAR TOO LONG FOR A PHONE SCREEN"]
        (tmp / "tl.json").write_text(json.dumps(tl))
        r = self.run_cli("gate", "--timeline", str(tmp / "tl.json"))
        self.assertEqual(r.returncode, 1)

    def test_build_runs_from_the_cli(self):
        tmp = pathlib.Path(tempfile.mkdtemp())
        r = self.run_cli("build", "examples/demo-30s/plan/timeline.json", "--out", str(tmp), "--pack", "tutorial")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((tmp / "index.html").exists())

    def test_resolve_prints_provenance(self):
        r = self.run_cli("resolve", "--pack", "comedy", "--locale", "hinglish", "--format", "portrait-9x16")
        self.assertEqual(r.returncode, 0)
        self.assertIn("format:portrait-9x16", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
