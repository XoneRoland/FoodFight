# EzyPlay

Two original browser games in one lightweight static website:

- **Food Fight** — the existing food-launching arcade and 12-level puzzle game.
- **Racer** — original low-poly 3D time trials with 12 increasingly technical tracks.

Open the site root to choose a game. Direct routes are `/food-fight/` and
`/racer/`. Both games include **BACK TO EZYPLAY** navigation. Racer also retains
its own menus, pause/restart controls and track selection.

## Verified release scope

The integrated Food Fight release has **12 puzzle levels**, including its
achievements, shop, daily rewards and other existing expansion features. A
100-level expansion was not found in the accessible repository/workspace history.
Racer has all 12 implemented tracks. See `INTEGRATION_AUDIT.md` for the source
inventory, preserved main-branch edits and remaining verification limits.

## Run locally

From the repository root, with Node 18+ and Python 3 available:

```sh
node scripts/build.mjs
python3 -m http.server 8051 --bind 127.0.0.1 --directory dist
```

Open the server in your browser. The repository root can also be served directly
without a build; it contains the same root `index.html` and relative routes.
ES modules need HTTP(S), so opening Racer directly through a `file:` URL is not
a supported way to run it. No npm install, framework or external runtime
dependency is needed. Optional nickname registration uses Netlify Forms on
Netlify hosting; playing without registering needs no submission service.

## Deploy to Cloudflare Pages

Connect this GitHub repository in Cloudflare Pages, then use:

- Framework preset: **None**
- Production branch: **main** (after reviewing and approving the EzyPlay PR)
- Build command: **node scripts/build.mjs**
- Build output directory: **dist**
- Root directory: repository root

No custom paid domain or server functions are needed. Pages supplies an HTTPS
`pages.dev` address. If your existing Pages project already watches main with
automatic deployments enabled, merging the approved PR triggers a production
build. Branch previews depend on the project's preview settings. No live
production deployment is claimed until the public URL has been verified.

The existing Netlify configuration is retained with its publish directory still
`dist`. Its build command is necessarily updated to the shared build script;
the old command would overwrite EzyPlay's landing page with Food Fight. No
Cloudflare configuration file has been added because no such file is needed.
Only explicit website files are copied; tests, recorded drives and documentation
are not published.

## Food Fight preservation

`Food_Fight_Development.html` is the single maintained Food Fight game file.
It and both recovered HTML originals were unchanged by the EzyPlay expansion.
The subsequent optional registration update changes only Food Fight's guest
entry and local admin interface; its gameplay, saves and recovered originals
remain preserved.
The `/food-fight/` wrapper embeds that file at the same origin and adds platform
navigation without replacing Food Fight's own Home button. Existing modes,
12 puzzle levels, custom local admin catalogue, coins, rewards, achievements,
backgrounds and controls remain available.

Food Fight keeps its original storage keys, including `bulletDashSave`,
`foodFightLocalCatalogueV1` and `foodFightAnonymousPlayEnabled`. Racer uses only
`ezyplay_racer_v1`. Root/platform navigation does not clear saves. Keep the same
website origin to retain existing progress: a new domain or separate hosting
provider does not automatically receive the old browser data. Clearing site data
can remove saves. Profiles and admin controls remain local prototypes. Optional
consenting nickname registrations are stored privately by Netlify Forms, not
in browser saves or a public list. There is no account service or shared game state.

## Optional guest registration on Netlify

Food Fight's **Play Anonymously** screen offers **Play without registering**, or
an unchecked consent choice to submit only a nickname to the administrator.
First/last names, emails and passwords are not requested. Existing gameplay
saves are unchanged. The local admin screen links to the signed-in Netlify
Forms dashboard; its prototype password is not secure authentication.

For project **ezygame**, enable Form Detection at
<https://app.netlify.com/projects/ezygame/forms>, then deploy this version.
View consenting entries under **Forms → ezyplay-guest-registration**. Follow
[NETLIFY_FORMS.md](NETLIFY_FORMS.md) for setup, delivery testing and manual
deletion within 30 days. The public notice is [privacy.html](privacy.html).
Cloudflare Pages can still host both games, but does not process Netlify Forms.

Before changing Food Fight, read `AGENTS.md`, `REQUIREMENTS.md`,
`CODEX_START_PROMPT.md` and `DEVELOPMENT.md`. Never overwrite recovered originals.

## Racer controls

| Action | Keyboard | Touch |
|---|---|---|
| Accelerate | W / Up | Hold GO |
| Brake, then reverse | S / Down | Hold BRAKE / REVERSE |
| Steer | A / D or Left / Right | Hold LEFT / RIGHT |
| Restart whole race | R | RESTART |
| Pause / resume | Escape | PAUSE / RESUME |

Hold steering and a pedal together on iPad. Pointer release/cancel, lost capture,
blur and page visibility changes release inputs. Losing focus pauses the timer.
Landscape provides the widest driving view; portrait is also supported.
Pass checkpoint gates in order. Off-track recovery returns to the last valid
checkpoint with a three-second penalty. Any legitimate finish earns bronze and
unlocks the next track; gold/silver reward faster times. Best times and medals
never decrease. Four vehicle colors and local race statistics are saved.

Racer uses original WebGL 1 geometry and shaders, two batched draw calls, no
textures, capped device pixel ratio/pixel count, and a 120 Hz fixed physics step.
Rendering is capped at 60 fps during play and 30 fps in menus, then idle scenes
stop rendering. Canvas resolution adapts on slow renderers; actual performance
depends on the device. Unsupported/lost WebGL shows a clear recovery message.

## Verification

```sh
node tests/racer_foundation.mjs
node tests/racer_race.mjs
node tests/racer_progress.mjs
node tests/racer_tracks.mjs
```

The track suite drives all 12 courses using actual movement/collision rules,
then independently replays recorded control streams from
`tests/racer_paths.json`. It checks the recording's source hash. Regenerate only
after intentional simulation changes with `node tests/racer_tracks.mjs --record`.
The development controller is never included in the website.

With the built server running, Python Playwright and system Chromium installed:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/ezyplay_browser.py
```

`EZYPLAY_BASE_URL` overrides its default server address. This suite checks the
actual 3D renderer, native keyboard and multitouch, pause/restart, all 12 tracks
through recorded-input replay in the live game loop, results, unlocks, saves,
Food Fight isolation and platform navigation. Test-only hooks are injected into
the browser response; no autoplay or test hook ships in the game.

Food Fight's existing six browser suites remain under `tests/`. Set
`FOODFIGHT_BASE_URL=http://127.0.0.1:8051` to run against the built game file.
See `EZYPLAY.md` for verification outcomes and limitations, and `DEVELOPMENT.md`
for the existing Food Fight feature and storage documentation.
