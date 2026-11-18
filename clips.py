#!/usr/bin/env python3
"""GTA 6 Twitch clips from the streamers in streamers.txt (the ones you're allowed to clip).

python3 clips.py                  # list the last 24 hours' top GTA 6 clips (no video downloaded)
python3 clips.py make <clip url>  # make a vertical captioned version in captions/out/

Either command takes another allowlist file as its last argument. Needs yt-dlp on PATH.
"""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

GAME = "Grand Theft Auto VI"
PER_STREAMER = 8  # top clips checked per streamer; each check is one request to Twitch
CAPTIONS = Path(__file__).resolve().parent / "captions"


def ytdlp_json(*args):
    out = subprocess.run(["yt-dlp", "--socket-timeout", "30", "-J", *args], capture_output=True, text=True)
    if out.returncode:
        raise RuntimeError(out.stderr.strip().splitlines()[-1] if out.stderr.strip() else "yt-dlp failed")
    return json.loads(out.stdout)


def allowlist(path):
    """Channel names, one per line; blank lines and # comments ignored."""
    with open(path) as f:
        return [s for s in (line.split("#")[0].strip().lower() for line in f) if s]


def top_clips(streamer):
    url = f"https://www.twitch.tv/{streamer}/clips?filter=clips&range=24hr"
    entries = ytdlp_json("--flat-playlist", "--playlist-end", str(PER_STREAMER), url).get("entries") or []
    return [dict(e, streamer=streamer) for e in entries]


def game_of(url):
    return (ytdlp_json("--skip-download", url).get("categories") or [None])[0]


def pick(entries, game_of):
    """GTA 6 clips only, most viewed first."""
    games = list(ThreadPoolExecutor(8).map(lambda e: game_of(e["url"]), entries))
    return sorted((e for e, g in zip(entries, games) if g == GAME), key=lambda e: e.get("view_count") or 0, reverse=True)


def make(url, allow_path):
    info = ytdlp_json("--skip-download", url)
    channel = (info.get("channel") or "").lower()
    if channel not in allowlist(allow_path):  # the permission gate: never download a clip you can't post
        sys.exit(f"{channel or 'This channel'} isn't in {allow_path}. Only clip streamers who gave you permission.")
    name = f"{channel}-{info['id']}.mp4"
    run = lambda *cmd: subprocess.run(cmd, cwd=CAPTIONS, check=True)
    run("yt-dlp", "--socket-timeout", "30", "-f", "1080/720/480/best", "-o", f"public/{name}", url)  # landscape; the render reframes it
    run("node", "sub.mjs", f"public/{name}")  # word-timed transcript -> public/<name>.json
    run("npx", "remotion", "render", "CaptionedVideo", f"out/{name}", "--props", json.dumps({"file": name}))
    print(f"\nReady: {CAPTIONS / 'out' / name}\nCaption: {info.get('title')} (via twitch.tv/{channel})")


def main():
    if sys.argv[1:2] == ["make"]:
        if len(sys.argv) < 3:
            sys.exit("usage: python3 clips.py make <clip url> [allowlist]")
        return make(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "streamers.txt")
    streamers = allowlist(sys.argv[1] if len(sys.argv) > 1 else "streamers.txt")
    if not streamers:
        sys.exit("streamers.txt is empty. Add streamers whose clipping campaign you've joined or who said you can clip them.")
    entries = []
    for s in streamers:
        try:
            entries += top_clips(s)
        except Exception as e:  # an offline or renamed channel shouldn't stop the rest
            print(f"skipped {s}: {e}", file=sys.stderr)
    for e in pick(entries, game_of):
        print(f"{e.get('view_count') or 0:>8,} views  {int(e.get('duration') or 0):>3}s  {e['streamer']:<16} {e['title']}\n{'':>27}{e['url']}")


if __name__ == "__main__":
    main()
