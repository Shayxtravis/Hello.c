#!/usr/bin/env python3
"""Auto-like every profile in your Tinder web feed.

Drives tinder.com in a real Chromium window via Playwright. You log in by hand
the first time; the session is kept in a local profile folder so later runs
start already signed in. The bot never sees your password.

The 50-mile radius is a Tinder setting, not something the bot decides: set
Settings -> Discovery -> Maximum Distance to 50 mi (the bot can also check it
for you with --check-distance) and the feed only shows profiles in range.
"""

import argparse
import random
import sys
import time
from pathlib import Path

from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright

BASE_URL = "https://tinder.com"
PROFILE_DIR = Path(__file__).with_name(".tinder-profile")

# Text that means Tinder has stopped serving likes or profiles.
OUT_OF_LIKES = ("You're Out of Likes", "out of likes", "Get Tinder Gold", "Get Tinder Plus")
NO_PROFILES = ("There's no one new around you", "no one new", "Expand your search")


def page_text(page) -> str:
    try:
        return page.inner_text("body", timeout=2000)
    except PWTimeout:
        return ""


def dismiss_popups(page) -> None:
    """Close the match screen, 'add to home screen' prompts and similar."""
    for label in ("Back to Tinder", "Not interested", "Maybe later", "No Thanks", "Close"):
        btn = page.get_by_role("button", name=label)
        if btn.count():
            try:
                btn.first.click(timeout=1000)
            except PWTimeout:
                pass
    page.keyboard.press("Escape")


def wait_for_login(page, base: str) -> None:
    print("Waiting for you to log in to Tinder in the browser window...")
    while "/app/recs" not in page.url or not page.locator("[aria-label='Like'], button:has-text('Like')").count():
        if "/app" in page.url and "/app/recs" not in page.url:
            page.goto(base + "/app/recs")
        time.sleep(2)
    print("Logged in, feed is loaded.")


def check_distance(page, base: str, miles: int) -> None:
    page.goto(base + "/app/profile/settings")
    time.sleep(3)
    text = page_text(page)
    if f"{miles} mi" in text:
        print(f"Maximum Distance is {miles} mi. Good.")
    else:
        print(f"Couldn't confirm Maximum Distance is {miles} mi. "
              "Check Settings -> Discovery -> Maximum Distance in the window, then press Enter.")
        input()
    page.goto(base + "/app/recs")
    time.sleep(3)


def run(max_likes: int, min_delay: float, max_delay: float, distance: int | None,
        base: str = BASE_URL, headless: bool = False) -> None:
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(PROFILE_DIR), headless=headless, viewport={"width": 1200, "height": 900},
            geolocation=None, permissions=["geolocation"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(base + "/app/recs")
        wait_for_login(page, base)
        if distance:
            check_distance(page, base, distance)

        liked = 0
        try:
            while max_likes <= 0 or liked < max_likes:
                text = page_text(page)
                if any(s in text for s in OUT_OF_LIKES):
                    print("Tinder says you're out of likes. Stopping.")
                    break
                if any(s in text for s in NO_PROFILES):
                    print("No more profiles in range. Stopping.")
                    break

                # Right arrow is Tinder web's built-in shortcut for Like.
                page.keyboard.press("ArrowRight")
                time.sleep(random.uniform(min_delay, max_delay))

                # Only count the like if Tinder didn't answer it with the paywall.
                text = page_text(page)
                if any(s in text for s in OUT_OF_LIKES):
                    print("Tinder says you're out of likes. Stopping.")
                    break
                liked += 1
                print(f"Liked {liked}")
                if "It's a Match" in text:
                    print("  It's a match!")
                dismiss_popups(page)
        except KeyboardInterrupt:
            print("\nStopped by you.")
        finally:
            print(f"Done. Liked {liked} profiles.")
            ctx.close()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max-likes", type=int, default=0, help="stop after this many likes (0 = no limit)")
    ap.add_argument("--min-delay", type=float, default=1.5, help="minimum seconds between likes")
    ap.add_argument("--max-delay", type=float, default=4.0, help="maximum seconds between likes")
    ap.add_argument("--check-distance", type=int, metavar="MILES", default=50,
                    help="confirm Maximum Distance is set to this before swiping (0 to skip)")
    ap.add_argument("--base-url", default=BASE_URL, help=argparse.SUPPRESS)  # for testing against a mock
    ap.add_argument("--headless", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args.min_delay > args.max_delay:
        ap.error("--min-delay must be <= --max-delay")
    run(args.max_likes, args.min_delay, args.max_delay, args.check_distance or None,
        args.base_url.rstrip("/"), args.headless)
    return 0


if __name__ == "__main__":
    sys.exit(main())
