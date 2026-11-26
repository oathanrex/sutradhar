#!/usr/bin/env python3
"""Render a real MP4 preview of a timeline - no browser, no HyperFrames needed.

This is NOT a HyperFrames render. It is a deterministic preview of the shot sheet (kind, text,
timing, brand colours) so a human can watch the pacing before paying for a render. Honest label,
useful artifact: `sutra gate --render docs/demo.mp4` can then check loudness and flash for real.

    python3 scripts/make_demo.py examples/demo-30s/plan/timeline.json docs/demo.mp4

Needs: Pillow, numpy, and any ffmpeg binary (imageio-ffmpeg ships one: pip install imageio-ffmpeg).
"""
import json, math, pathlib, struct, subprocess, sys, tempfile, wave

W, H, FPS = 1280, 720, 25
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
BOLD, MONO = f"{FONT_DIR}/DejaVuSans-Bold.ttf", f"{FONT_DIR}/DejaVuSansMono.ttf"


def ffmpeg_exe():
    import shutil
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        raise SystemExit("no ffmpeg: pip install imageio-ffmpeg")


def shot_image(s, brand, w=W, h=H):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fg, accent = brand["text"], brand["accent"]
    text = s.get("text") or []
    kind = s["kind"]
    cx, cy = w // 2, h // 2

    def fit(line, max_w, size, path=BOLD):
        while size > 14:
            f = ImageFont.truetype(path, size)
            if d.textlength(line, font=f) <= max_w:
                return f
            size -= 4
        return ImageFont.truetype(path, 14)

    if kind in ("words", "chips", "chapter") and text:
        if kind == "chapter":
            no = text[0]
            name = " ".join(text[1:]) or (s.get("beat") or "").upper()
            f1 = ImageFont.truetype(MONO, 34)
            d.text((cx, cy - 60), f"/{no}", font=f1, fill=accent, anchor="mm")
            f2 = fit(name, int(w * .8), 96)
            d.text((cx, cy + 10), name.upper(), font=f2, fill=fg, anchor="mm")
        elif kind == "chips":
            labels = text
            fs = [ImageFont.truetype(BOLD, 44) for _ in labels]
            widths = [d.textlength(l, font=f) + 56 for l, f in zip(labels, fs)]
            x = cx - sum(widths) // 2
            for l, f, wd in zip(labels, fs, widths):
                d.rounded_rectangle([x, cy - 34, x + wd, cy + 34], radius=34, outline=accent, width=3)
                d.text((x + wd // 2, cy), l, font=f, fill=accent, anchor="mm")
                x += wd + 18
        else:
            lines = [" ".join(line) for line in text]
            y = cy - (len(lines) - 1) * 60
            for i, line in enumerate(lines):
                f = fit(line, int(w * .86), 150)
                d.text((cx, y), line.upper(), font=f, fill=accent if i == 0 else fg, anchor="mm")
                y += 150
    else:
        label = (s.get("media") or ["no media planned"])[0]
        box = [int(w * .08), int(h * .14), int(w * .92), int(h * .76)]
        d.rounded_rectangle(box, radius=14, outline=(255, 255, 255, 40), width=2, fill=(15, 17, 22, 255))
        f = ImageFont.truetype(MONO, 26)
        d.text((cx, cy - 14), label, font=f, fill=(138, 143, 152), anchor="mm")
        fn = ImageFont.truetype(MONO, 20)
        d.text((cx, cy + 26), (s.get("beat") or kind).upper(), font=fn, fill=accent, anchor="mm")
    return img


def audio_wav(shots, dur, path):
    """A quiet tone bed plus a short burst on sfx shots, so the loudness gate has something real to read."""
    import numpy as np
    sr = 48000
    n = int(sr * dur)
    t = np.arange(n) / sr
    sig = 0.02 * np.sin(2 * math.pi * 110 * t) + 0.01 * np.sin(2 * math.pi * 220 * t)
    rng = np.random.default_rng(7)
    for s in shots:
        if not s.get("sfx"):
            continue
        i0 = int(s["start_s"] * sr)
        ln = int(0.09 * sr)
        env = np.exp(-np.arange(ln) / (ln * 0.25))
        burst = rng.standard_normal(ln) * env * 0.12
        end = min(n, i0 + ln)
        sig[i0:end] += burst[:end - i0]
    pcm = (np.clip(sig, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())


def main(timeline_path, out_path):
    from PIL import Image
    tl = json.loads(pathlib.Path(timeline_path).read_text())
    brand_file = pathlib.Path("brand/design.json")
    brand = json.loads(brand_file.read_text()) if brand_file.exists() else {
        "background": "#0E0F12", "text": "#F4F4F2", "accent": "#F2C200"}
    bg = tuple(int(brand["background"].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    shots = tl["shots"]
    dur = float(tl["duration_s"])
    cache = {}
    tmp = pathlib.Path(tempfile.mkdtemp())
    wav = tmp / "a.wav"
    audio_wav(shots, dur, wav)

    pathlib.Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    frames = int(round(dur * FPS))
    ff = ffmpeg_exe()
    cmd = [ff, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", str(wav),
           "-af", "loudnorm=I=-14:TP=-2.0:LRA=11,alimiter=limit=0.9:level=false", "-c:v", "libx264", "-preset", "veryfast",
           "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", str(out_path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    base = Image.new("RGBA", (W, H), bg + (255,))
    si = 0
    try:
        for f in range(frames):
            t = f / FPS
            while si < len(shots) - 1 and t >= shots[si]["end_s"]:
                si += 1
            s = shots[si]
            if s["i"] not in cache:
                cache[s["i"]] = shot_image(s, brand)
            img = cache[s["i"]]
            local = t - s["start_s"]
            a = min(1.0, local / 0.38) if local >= 0 else 0.0
            a = a * a * (3 - 2 * a)                      # smoothstep
            if a < 1.0:
                img2 = img.copy()
                img2.putalpha(img.split()[3].point(lambda v: int(v * a)))
                off = int(26 * (1 - a))
                frame = Image.new("RGBA", (W, H), bg + (255,))
                frame.alpha_composite(img2, (0, off))
            else:
                frame = Image.alpha_composite(base, img)
            proc.stdin.write(frame.convert("RGB").tobytes())
    finally:
        proc.stdin.close()
        proc.wait()
    print(f"  wrote {out_path} ({frames} frames, {dur}s, {W}x{H}@{FPS})")
    print("  note: this is a shot-sheet preview, not a HyperFrames render")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "examples/demo-30s/plan/timeline.json",
         sys.argv[2] if len(sys.argv) > 2 else "docs/demo.mp4")
