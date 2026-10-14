# Tinder auto-swipe

Likes every profile in your Tinder feed by driving tinder.com in a real browser.

## Setup

```sh
pip install -r requirements.txt
playwright install chromium
```

## Use

1. In the Tinder app or on tinder.com, set **Settings → Discovery → Maximum Distance** to **50 mi**.
   The feed only shows people inside that radius, so that's what limits the bot to 50 miles.
2. Run:
   ```sh
   python autoswipe.py
   ```
3. A Chromium window opens. Log in by hand the first time. The session is saved in
   `.tinder-profile/` (git-ignored), so later runs skip this step.
4. The bot checks the distance setting, then likes profiles until Tinder runs out of
   profiles or likes, or you press Ctrl+C.

Options:

| Flag | Default | Meaning |
|---|---|---|
| `--max-likes N` | 0 (no limit) | Stop after N likes |
| `--min-delay` / `--max-delay` | 1.5 / 4.0 | Random pause between likes, in seconds |
| `--check-distance MILES` | 50 | Distance to confirm before starting; 0 skips the check |

## Things to know

- **This breaks Tinder's Terms of Use**, which ban bots and automated swiping. Tinder can
  shadowban or ban accounts that like everyone quickly. Keep the delays, and expect the risk.
- **Free accounts get a limited number of likes** (roughly 50–100 every 12 hours). The bot
  stops when Tinder shows the out-of-likes screen. Plus, Gold and Platinum give unlimited likes.
- Liking everyone also pushes your profile down Tinder's ranking, so you may end up shown to fewer people.
- Tinder changes its web page often. If the bot stops finding the feed, the button labels
  and text checks in `autoswipe.py` may need updating.
