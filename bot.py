#!/usr/bin/env python3
"""GTA 6 news drafter: finds new GTA 6 stories and drafts X posts you finish and post by hand.

Run locally: python3 bot.py  (prints drafts)
On GitHub Actions it opens one issue per run with the new stories instead.
"""
import html
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

FEEDS = {
    "IGN": "https://feeds.feedburner.com/ign/games-all",
    "GameSpot": "https://www.gamespot.com/feeds/game-news/",
    "PC Gamer": "https://www.pcgamer.com/rss/",
    "Eurogamer": "https://www.eurogamer.net/feed",
    "VGC": "https://www.videogameschronicle.com/feed/",
    "Kotaku": "https://kotaku.com/rss",
    "Polygon": "https://www.polygon.com/rss/index.xml",
    "Insider Gaming": "https://insider-gaming.com/feed/",
    "Gematsu": "https://www.gematsu.com/feed",
    "Push Square": "https://www.pushsquare.com/feeds/latest",
}
GTA6 = re.compile(r"\b(gta|grand theft auto)\s?(6|vi)\b", re.I)
STATE = "seen.json"
KEEP = 2000  # remembered links/titles; older ones roll off
MAX_SHOWN = 30  # per issue; keeps it readable and under GitHub's 65,536-char body limit


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (gta6-news-drafter)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def parse(xml_bytes, source):
    for item in ET.fromstring(xml_bytes).iter("item"):
        title = html.unescape((item.findtext("title") or "").strip())  # WordPress feeds double-encode, e.g. &#8217;
        link = (item.findtext("link") or "").strip()
        if title and link and GTA6.search(title):
            yield {"title": title, "link": link, "source": source}


def title_key(title):
    return re.sub(r"\W+", " ", title.lower()).strip()


def pick_new(stories, seen):
    """Stories whose link and title haven't been drafted before. Adds them to `seen`."""
    known, new = set(seen), []
    for s in stories:
        keys = (s["link"], title_key(s["title"]))  # same headline syndicated by two outlets counts once
        if known.isdisjoint(keys):
            known.update(keys)
            seen.extend(keys)
            new.append(s)
    return new


def draft_link(s):
    return "https://x.com/intent/post?text=" + urllib.parse.quote(f"{s['title']} (via {s['source']})\n\n")


def main():
    seen = json.load(open(STATE)) if os.path.exists(STATE) else []
    stories, failed = [], 0
    for source, url in FEEDS.items():
        try:
            stories += parse(fetch(url), source)
        except Exception as e:  # one dead feed shouldn't stop the rest
            failed += 1
            print(f"skipped {source}: {e}", file=sys.stderr)
    if failed == len(FEEDS):
        sys.exit("every feed failed; check the network or SSL certificates")  # fails the Actions run so GitHub emails you

    new = pick_new(stories, seen)
    if new:
        body = "\n\n".join(
            f"**{s['title']}** ({s['source']})\n[Read]({s['link']}) · [Draft post on X]({draft_link(s)})"
            for s in new[:MAX_SHOWN]
        )
        if len(new) > MAX_SHOWN:  # e.g. the first run's backlog; the extras are marked seen, not resent
            body += f"\n\n_{len(new) - MAX_SHOWN} more not shown._"
        if os.environ.get("GITHUB_ACTIONS"):
            subprocess.run(
                ["gh", "issue", "create", "--title", f"GTA 6 news: {len(new)} new",
                 "--body", body, "--assignee", os.environ["GITHUB_REPOSITORY_OWNER"]],
                check=True,
            )
        else:
            print(body)
    print(f"{len(new)} new of {len(stories)} GTA 6 stories", file=sys.stderr)

    # saved only after delivery, so a failed issue doesn't silently drop stories
    with open(STATE, "w") as f:
        json.dump(seen[-KEEP:], f, indent=0)


if __name__ == "__main__":
    main()
