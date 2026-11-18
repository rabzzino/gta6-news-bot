"""Self-check: python3 test_bot.py"""
import urllib.parse

from bot import GTA6, draft_link, parse, pick_new

for t in ["GTA 6 trailer 3 is here", "Grand Theft Auto VI review", "GTA6 sales", "gta vi map size"]:
    assert GTA6.search(t), t
for t in ["GTA 5 Online update", "GTA 60fps mod", "GTA VIP pass", "Red Dead Redemption 3"]:
    assert not GTA6.search(t), t

rss = b"""<rss><channel>
<item><title><![CDATA[Rockstar&#8217;s GTA 6 launch]]></title><link> https://a.com/1 </link></item>
<item><title>Some other game</title><link>https://a.com/2</link></item>
</channel></rss>"""
items = list(parse(rss, "A"))
assert items == [{"title": "Rockstar’s GTA 6 launch", "link": "https://a.com/1", "source": "A"}], items

seen = []
batch = items + [{"title": "Rockstar's GTA 6 launch!", "link": "https://b.com/9", "source": "B"},  # same headline, other outlet
                 {"title": "GTA 6 trailer", "link": "https://a.com/1", "source": "A"}]  # same link
assert pick_new(batch, seen) == items
assert pick_new(items, seen) == []  # already drafted on a previous run

text = urllib.parse.unquote(draft_link(items[0]).split("text=")[1])
assert text == "Rockstar’s GTA 6 launch (via A)\n\n", text
print("ok")

# clips.py
import os, tempfile
from clips import allowlist, pick

with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
    f.write("# comment\nXQC\n\n  kaicenat  # joined campaign\n")
assert allowlist(f.name) == ["xqc", "kaicenat"]
os.unlink(f.name)

clips = [{"url": "a", "view_count": 10}, {"url": "b", "view_count": 500}, {"url": "c", "view_count": None}, {"url": "d", "view_count": 900}]
games = {"a": "Grand Theft Auto VI", "b": "Grand Theft Auto VI", "c": "Grand Theft Auto VI", "d": "Just Chatting"}
assert [c["url"] for c in pick(clips, games.get)] == ["b", "a", "c"]
print("clips ok")
