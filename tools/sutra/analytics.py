"""Retention intake without a CSV export.

Two real API calls, no third-party client:
  - OAuth 2.0 device flow (works on a headless box, no localhost redirect)
  - YouTube Analytics v2 audienceRetention

Everything network-touching goes through `post_json` / `get_json` so the logic is testable offline.
The token is read from the environment (SUTRA_TOKEN) or tools/.env, never committed.
"""
import json, os, pathlib, time, urllib.error, urllib.parse, urllib.request

DEVICE_CODE = "https://oauth2.googleapis.com/device/code"
TOKEN = "https://oauth2.googleapis.com/token"
REPORTS = "https://youtubeanalytics.googleapis.com/v2/reports"
SCOPE = "https://www.googleapis.com/auth/yt-analytics.readonly"


class ApiError(RuntimeError):
    pass


def post_json(url, data, headers=None):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise ApiError(f"{e.code}: {e.read().decode()[:300]}") from None


def get_json(url, params, token):
    q = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{url}?{q}", headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise ApiError(f"{e.code}: {e.read().decode()[:300]}") from None


def token_from_env(root=None):
    tok = os.environ.get("SUTRA_TOKEN")
    if tok:
        return tok
    env = (pathlib.Path(root or ".") / "tools" / ".env")
    if env.exists():
        for line in env.read_text().splitlines():
            if line.strip().startswith("SUTRA_TOKEN="):
                return line.split("=", 1)[1].strip()
    return None


def device_login(client_id, post=post_json, sleep=time.sleep, prompt=print, max_polls=60):
    """OAuth device flow. Prints a code, you type it once in the browser, token comes back."""
    d = json.load if False else None  # keep import surface minimal
    start = post(DEVICE_CODE, {"client_id": client_id, "scope": SCOPE})
    prompt(f"\n  Open {start['verification_url']} and enter: {start['user_code']}\n")
    interval = int(start.get("interval", 5))
    for _ in range(max_polls):
        sleep(interval)
        try:
            tok = post(TOKEN, {"client_id": client_id, "device_code": start["device_code"],
                               "grant_type": "urn:ietf:params:oauth:grant-type:device_code"})
            return tok["access_token"]
        except ApiError as e:
            if "authorization_pending" in str(e) or "slow_down" in str(e):
                continue
            raise
    raise ApiError("timed out waiting for approval")


def retention_rows(payload, duration_s):
    """Parse an audienceRetention report into [(t_s, retention_pct)] normalised to 100.

    The API returns 100 buckets of elapsedVideoTimeRatio; multiply by duration to get seconds."""
    heads = [h["name"] for h in (payload.get("columnHeaders") or [])]
    if "elapsedVideoTimeRatio" not in heads or not payload.get("rows"):
        raise ApiError("unexpected report shape: " + ", ".join(heads))
    ir = heads.index("elapsedVideoTimeRatio")
    iv = heads.index("audienceWatchRatio") if "audienceWatchRatio" in heads else heads.index("relativeRetentionPerformance")
    rows = sorted((float(r[ir]), float(r[iv])) for r in payload["rows"])
    top = rows[0][1] or 1.0
    return [(round(ratio * float(duration_s), 1), round(v / top * 100.0, 2)) for ratio, v in rows]


def pull(video_id, duration_s, token=None, get=get_json, ids="channel==MINE",
         start="2020-01-01", end=None):
    token = token or token_from_env()
    if not token:
        raise ApiError("no token: run `sutra analytics login --client-id <id>` or set SUTRA_TOKEN")
    import datetime
    payload = get(REPORTS, {
        "ids": ids, "metrics": "audienceWatchRatio,relativeRetentionPerformance",
        "dimensions": "elapsedVideoTimeRatio", "filters": f"video=={video_id}",
        "startDate": start, "endDate": end or datetime.date.today().isoformat(),
    }, token)
    return retention_rows(payload, duration_s)


def write_csv(rows, path):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("t_s,retention\n" + "\n".join(f"{t},{v}" for t, v in rows) + "\n", encoding="utf8")
    return p
