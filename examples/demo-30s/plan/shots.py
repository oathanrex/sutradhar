"""The same 12 shots as plan/timeline.json, in the shape a build script consumes.
Edit here, rebuild the timeline, and every gate re-runs against the new numbers."""
VOICE = "voice_tight.wav"

SHOTS = [
    dict(at="today i tried", kind="words", lines=[["3", "TOOLS"]]),
    dict(at="the first one", kind="screen", src="broll/site.mp4", label="tool.com", mark=(820, 300, 420, 160), mark_at="pricing", sfx="whoosh"),
    dict(at="and honestly", kind="full", src="broll/desk.mp4"),
    dict(at="no setup", kind="words", lines=[["NO", "SETUP"]]),
    dict(at="so i opened", kind="screen", src="screens/app.mp4", label="app", mstart=2.0),
    dict(at="it is free", kind="chips", items=[("free", "gold", "free"), ("fast", "gold", "fast")]),
    dict(at="the catch", kind="gif", g="react", cap="the catch"),
    dict(at="ten minutes", kind="words", lines=[["10", "MINUTES"]]),
    dict(at="then this happened", kind="screen", src="screens/app.mp4", label="app", mstart=9.0),
    dict(at="that is the whole", kind="full", src="broll/desk.mp4", sfx="whoosh"),
    dict(at="go try it", kind="words", lines=[["TRY", "IT"]]),
    dict(at="see you", kind="full", src="broll/desk.mp4"),
]

GIFS = {"react": ("gifs/react.mp4", 966, 726, 2.5)}
SECTIONS = [("today i tried", "part1")]
