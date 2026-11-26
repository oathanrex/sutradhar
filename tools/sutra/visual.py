"""Pixel-level checks. Pure functions where possible so they are testable without ffmpeg."""
import subprocess


def luminance_series(render, fps=30, w=160, h=90):
    """Per-frame mean luminance (0..1), sampled from the render at a low resolution."""
    from .util import ffmpeg_exe
    ff = ffmpeg_exe()
    if not ff:
        raise RuntimeError("ffmpeg not installed")
    raw = subprocess.run([
        ff, "-v", "error", "-i", str(render), "-vf", f"fps={fps},scale={w}:{h},format=gray",
        "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    frame = w * h
    return [sum(raw[i:i + frame]) / frame / 255.0 for i in range(0, len(raw) - frame + 1, frame)]


def flash_rate(lums, fps=30, amp=0.18):
    """Photosensitivity heuristic: count luminance swings above `amp`, report the worst 1-second window.

    Returns (max_flashes_per_second, timestamp_s). WCAG 2.3.1 guidance is <= 3 per second."""
    if not lums:
        return 0.0, 0.0
    swings = []
    for i in range(1, len(lums)):
        up = lums[i] - lums[i - 1]
        if abs(up) >= amp:
            if not swings or (swings[-1][1] > 0) != (up > 0) or abs(swings[-1][1]) < amp:
                swings.append((i, up))
    if len(swings) < 2:
        return 0.0, 0.0
    window = max(1, int(fps))
    best, at = 0.0, 0.0
    times = [i for i, _ in swings]
    for j, t in enumerate(times):
        n = sum(1 for x in times[j:] if x - t < window)
        if n > best:
            best, at = n, t / fps
    return float(best), round(at, 2)


def frame_spread(render, t=0.8, out_png=None):
    """Heuristic hook check: luminance spread of the frame at time t.

    A headline on a flat background gives a wide spread (dark bg + bright type). A washed-out frame
    gives a narrow one. This is a heuristic, not OCR: report it as a hint, never as a verdict.
    Returns (spread, path) or raises."""
    import pathlib
    from .util import ffmpeg_exe
    out = pathlib.Path(out_png or "/tmp/hook_frame.png")
    subprocess.run([ffmpeg_exe() or "ffmpeg", "-v", "error", "-ss", str(t), "-i", str(render), "-frames:v", "1",
                    "-y", str(out)], check=True, capture_output=True)
    try:
        from PIL import Image
    except ImportError:
        return None, out
    im = Image.open(out).convert("L").resize((160, 90))
    px = sorted(im.getdata())
    n = len(px)
    p10, p90 = px[int(n * .10)], px[int(n * .90)]
    return round((p90 - p10) / 255.0, 3), out
