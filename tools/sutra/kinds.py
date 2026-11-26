"""Canonical shot kinds. A pack's shot_mix may only use these names."""
TEXT = {"words", "chips", "strike2", "chapter", "pick2", "bars2", "gauge", "meter", "tries", "prompts"}
DIAGRAM = {"flow", "nodes", "hub", "card", "map", "sketch"}
SCREEN = {"screen", "split", "chat", "term", "file", "ytwall"}
FOOTAGE = {"full", "film", "gif", "rec"}
ALL = TEXT | DIAGRAM | SCREEN | FOOTAGE
# kinds that must carry a media file, and kinds that must not
NEEDS_MEDIA = {"screen", "full", "film", "gif", "rec", "split"}
NO_MEDIA = {"words", "chips", "strike2", "chapter", "pick2", "bars2", "gauge", "meter",
            "tries", "flow", "nodes", "hub", "card", "map", "sketch", "prompts", "chat", "term", "file", "ytwall"}

def check(kinds):
    bad = [k for k in kinds if k not in ALL]
    return bad
