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
