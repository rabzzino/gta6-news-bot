# GTA 6 News Drafter

Every 30 minutes this bot checks 10 gaming news sites for GTA 6 stories. New ones go into a GitHub issue assigned to you, and the GitHub app sends you a push notification. Each story has a **Draft post on X** link that opens X with the headline filled in. You add your take and post it yourself.

The bot never posts to X on its own. That's deliberate: X won't pay out on content that is posted automatically or only aggregates other outlets' news (see "Getting paid" below).

Costs: $0. The repo is public, and GitHub Actions runs free with no minute limit on public repos. Python uses only its standard library, so there's nothing to install.

## Setup (about 5 minutes)

1. Create a **public** GitHub repo and push these files to it.
2. Open the repo's **Actions** tab and enable workflows if GitHub asks.
3. Click **GTA 6 news → Run workflow** once. The first run opens one issue with the first 30 stories it finds, which come from the top sites in `FEEDS`. It notes how many more it skipped and marks all of them as seen.
4. In the GitHub mobile app, turn on push notifications for **Assigned** issues (Settings → Notifications).

After that it runs on its own. GitHub can start scheduled runs a few minutes late, and it pauses schedules on public repos after 60 days with no activity. The bot's own commits to `seen.json` should count as activity, but if the runs ever stop, click **Run workflow** again.

## Daily flow

1. You get a notification: "GTA 6 news: 4 new".
2. Open the issue and tap **Draft post on X** on a story worth posting.
3. X opens with `Headline (via IGN)` filled in. Write your take under it: what it means, what's missing, what you think. That take is the part X pays for.
4. Post it, then close the issue.

## Getting paid on X (rules checked 2026-11-18)

X's [Original Content Rewards](https://help.x.com/en/using-x/original-content-rewards) replaced Creator Revenue Sharing. Revenue Sharing stopped taking new members on Aug 7, 2026. To get into Original Content Rewards you need:

- An X Premium (or higher) subscription
- 500 verified followers
- 500,000 Home Timeline impressions from verified users in the last 90 days (replies don't count)
- Approval from X, which isn't guaranteed once you qualify

Payouts are based on impressions from Premium users, paid every two weeks with a $30 minimum.

The following don't earn anything, and can get you removed from the program:
- Posts "created or posted using automated means". This is why you post by hand.
- Copied or barely changed headlines, and aggregated news with no perspective of your own. A post that's just the headline earns nothing, so always add your take.
- Downloaded and reuploaded trailers or clips. Link to them, or quote-post Rockstar's own post.
- Asking people to like, repost or follow.

## Keeping the account safe

- Make the name and bio clearly say it's an unofficial fan account, and don't use Rockstar's logo.
- Don't post leaked footage. Take-Two files takedowns quickly.
- Never script the X website to post or follow. X's [automation rules](https://help.x.com/en/rules-and-policies/x-automation) ban that outright, and the draft links are only there so you can post by hand.

## Run it locally

```bash
python3 bot.py        # prints new drafts and writes seen.json in the current folder
python3 test_bot.py   # self-check
```

If you're using the python.org build of Python on a Mac and every feed fails with `CERTIFICATE_VERIFY_FAILED`, run `Install Certificates.command` from your Python folder in Applications. Run locally from a different folder than the repo, so your local `seen.json` doesn't get committed.

## Changing sources

Edit `FEEDS` in `bot.py`; any RSS feed works. The `GTA6` pattern decides which headlines count. The bot commits `seen.json` on every run, so run `git pull` before you push a change of your own.

## Clips (runs on your Mac)

`clips.py` finds the day's top GTA 6 Twitch clips from streamers you're allowed to clip. It then turns the ones you pick into vertical videos with word-by-word captions, the style clipping accounts use.

**Get permission first.** Join a streamer's clipping campaign (for example on Content Rewards or Whop), or get their OK directly. Then add their Twitch name to `streamers.txt`. `clips.py` refuses to download clips from anyone who isn't on that list. Campaigns pay per view. The clipping sites' own figures put most rates around $0.50–$1.50 per 1,000 views, but treat that as a rough guide, not a promise. Each campaign's rules decide which platforms count and how you have to post.

**One-time setup:** about 2 GB. Remotion's packages, then whisper.cpp and its speech model.

```bash
cd captions && npm install && node sub.mjs && cd ..
```

**Daily use:**

```bash
python3 clips.py                    # top GTA 6 clips from your streamers, last 24 hours, most viewed first
python3 clips.py make <clip url>    # writes captions/out/<streamer>-<id>.mp4 and prints a caption to post
```

Making a clip takes about 4 minutes for a 60-second clip. If whisper hears music in a clip, it warns you. Rendering uses your installed Google Chrome in a throwaway profile, because Remotion's bundled Chrome crashes on macOS 26 (see `captions/remotion.config.ts`). To change the caption look, edit `captions/src/CaptionedVideo/Page.tsx` for font size, colours and position. To preview it live, run `npx remotion studio` in `captions/`.

**Before you post a clip:**
- Post it by hand on the platforms the campaign pays on, and credit the streamer. The printed caption already includes their link.
- Keep clips off the news account. X doesn't count reuploads from another platform, or clips with captions added, as original content, and that can hurt the news account's application to Original Content Rewards.
- Skip clips with in-game radio or other music. The streamer's permission doesn't cover the music.
- Skip story cutscenes and spoilers, which Rockstar takes down. Also watch for 18+ moments, since the campaign's platforms have their own rules.

The `captions/` folder is Remotion's [TikTok template](https://github.com/remotion-dev/template-tiktok) with a few local changes: the blurred vertical layout, the caption filter and music warning, and the Chrome setting. It stays on this Mac and out of the repo, because the template has no license. That keeps every clip, transcript and render out too. The GitHub workflow only runs the news bot. Remotion is free for individuals and companies of up to 3 people ([license](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md)).
