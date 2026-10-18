# Food Fight development version

`Food_Fight_Development.html` is copied from the most advanced recovered source,
`source/Food_Fight_Classic_Anonymous_Admin.html`. Both recovered originals are
preserved. The development version is self-contained: HTML, CSS and JavaScript,
with no build, external assets, backend, or package dependencies at runtime.
The classic CSS and all 12 puzzle templates are unchanged.

## Changes

- Track one active pointer, capture it during dragging, and cancel aiming safely
  on pointer cancellation, lost capture, navigation or rotation. A second finger
  cannot fire the first finger's shot. Endless movement requires dragging.
- Scale world coordinates and obstacle sizes with viewport changes so rotation
  does not leave targets outside the new canvas.
- Count puzzle projectile lifetime in simulation time instead of collision
  substeps, avoiding different ranges at different frame rates.
- Award Endless coins from the final score (10 per full 100 points), including
  crash-frame milestones. Ignore duplicate game-over calls.
- Retain the anonymous-play admin toggle in memory if storage writes fail, and
  synchronize changes from other tabs in the same browser origin.

Existing `bulletDashSave` progress and equipment remain compatible. Saves and
admin controls are local to this browser/site. The prototype password shown on
the admin screen is not secure authentication. If storage is blocked, settings
and progression can work during play but cannot be retained across page loads.

## Run locally

From the repository directory:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `/Food_Fight_Development.html` on that server in your browser.
No installation or build is needed to play.

## Run on iPad with Ship.page

1. Upload **only** `Food_Fight_Development.html` as the site's HTML entry file.
   If the host requires `index.html`, rename an upload copy to `index.html`;
   keep the development file and recovered originals in the repository.
2. Publish through Ship.page and open the published HTTPS address in iPad Safari.
3. Tap **PLAY ANONYMOUSLY**. Try Endless Run by dragging, then Puzzle Mode by
   dragging toward a target and releasing. Rotate the iPad during a puzzle.
4. Clear a puzzle, replay it, and verify coins are awarded only on its first
   clear. Try the shop after earning enough coins, then reload to check saves.
5. Optionally use Safari's Share → Add to Home Screen.

Progress is stored per browser/site origin. Changing hosting domains or clearing
Safari website data does not transfer the old save to the new site. Private
browsing may not retain progress after the session ends.

## Automated checks

Requires Python Playwright and Chromium (`/usr/bin/chromium` in the prepared
cloud environment). With the local server above running:

```sh
python3 tests/browser_checks.py
```

The suite covers desktop, iPad portrait and iPad landscape viewports: home/guest
navigation, all 12 level initializations, first-level physical clear and replay
rewards, out-of-shots/retry/reset, projectile lifetime at simulated 30/60/120 Hz,
rotation, multitouch ownership/cancellation, native Chromium touch dispatch,
Endless coin boundaries and duplicate game-over, insufficient funds, launcher
and food purchase/equip, save reload compatibility, wrong/correct admin login,
toggle/logout, cross-tab toggle changes and storage failure fallback. Coin
boundary and level-initialization checks use test-only browser instrumentation;
the shipped HTML has no test hooks or free-currency controls.

The suite does not solve every puzzle or replace physical iPad/Safari testing.

## Local admin catalogue and reward codes

From Home, tap **ADMIN PANEL**, enter `RGE123`, and log in. This is the existing
browser-local prototype password, visible in the HTML; it is not secure access
control.

- **Add a store item:** choose Blaster / launcher or Food projectile, enter a
  unique name, emoji/symbol and whole-number coin price, then tap **ADD TO STORE**.
  Zero makes an item free. These are cosmetic items using the existing gameplay.
- **Add a reward code:** enter a code using letters, numbers, `-` or `_`, choose
  coins or a store item as its reward, then tap **ADD CODE**. Letter case is
  ignored. The panel lists saved items and codes.
- Return Home, choose anonymous play, and open the shop. Custom items appear
  alongside the originals. Enter codes in **Reward code** and tap **REDEEM CODE**.
  Coin rewards add to the balance; item rewards unlock the item for equipping.
  Each code can be used once per local save. An already-owned item leaves its
  code unused. Codes have no expiry in this version.

Catalogue data uses `foodFightLocalCatalogueV1`; redemptions remain part of the
compatible `bulletDashSave` progress record. Additions persist on this browser
and site only: they are not embedded in the HTML, shared with other iPads or
published to GitHub/Ship.page. Refresh other open tabs after creating content.
Clearing website data removes local content and progress. A failed save displays
an error and does not report an item/code added or consume a redemption.

Additional public-UI regression tests:

```sh
python3 tests/admin_checks.py
```

Both suites accept `FOODFIGHT_BASE_URL` to test a server on a different port.
The admin suite exercises taps at desktop and iPad portrait/landscape sizes,
wrong/correct password, custom blasters and foods, duplicate/invalid entries,
text-safe rendering, coin/item redemption, purchase/equip, reload persistence,
gameplay rendering with custom equipment and storage-write failure recovery.
Physical iPad/Safari testing remains necessary before release.

## Guest player details

**PLAY ANONYMOUSLY** now opens a form for first name, last name and username
before enabling gameplay. Names are required (up to 40 characters each);
usernames use 3–24 letters, numbers or underscores. Cancel leaves play locked
unless an existing guest session was already active. The Home button changes to
**EDIT PLAYER DETAILS** during a session, and **END SESSION** clears those details.

The password-protected local admin panel shows **Current local player** with the
session's username and full name. Details stay in memory in this tab only and
clear on reload, End Session, or when anonymous play is disabled. They are not
written to browser storage or sent to a server. This is a guest session, not an
account: existing coins and progress remain shared in the browser. Other tabs
and devices are not shown in this local player panel.

Run `python3 tests/guest_checks.py` with the static server running to verify the
form, required fields, editing/cancellation, gameplay, admin display, literal
text rendering, session cleanup and operation with storage blocked. The existing
browser and admin suites also cover the new guest-entry step.
