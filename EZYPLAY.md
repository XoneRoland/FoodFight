# EzyPlay implementation record

This records the original EzyPlay integration. The later Netlify registration
update intentionally changes Food Fight's guest/admin interface and adds a
privacy page; all Racer files and Food Fight's gameplay/save handlers remain
unchanged from integration commit b20444e. See `NETLIFY_FORMS.md` for current
registration behavior and verification limits.

Baseline: a299daa. Dedicated branch: feature/ezyplay-racer. Food Fight's canonical
HTML and all recovered files remain unchanged. /food-fight/ embeds that file at
the same origin, retaining bulletDashSave and the local catalogue keys. Racer
uses its own ezyplay_racer_v1 key. No backend or account service is added.

Inspection found Netlify configuration publishing dist and no Cloudflare Pages
configuration. The existing build command necessarily changes because its old
copy command would replace the new home page with Food Fight. publish remains
dist. No production settings are changed externally, and this branch must not
be merged without approval. Cloudflare Pages can build with node scripts/build.mjs
and publish dist; the repository also has a working root index.html.

Driving verification: all 12 courses were driven to a legitimate finish through
RaceSession.step using the actual physics, boundaries, jumps and checkpoints.
Every run had zero recovery resets and zero wall contacts. tests/racer_paths.json records quantized
control streams and sampled paths; the test replays them independently and
checks a SHA-256 of simulation/track/controller sources. No controller is shipped
in the website. Geometry validation checks continuity, widths, slopes, start,
finish, ordered gates and ramp landing runouts. Roads have no required gaps;
ramps produce real gravity-driven jumps while remaining drivable at low speed.
The automated runs reached 3.48m, 5.80m and 3.11m above the road on tracks 7, 10
and 12 respectively. Medal times are tuned against these successful runs; a
bronze finish always advances progression.

## Recorded successful drives

| Track | Time | Ordered gates | Recoveries |
|---|---:|---:|---:|
| 1. First Gear | 16.917s | 4 | 0 |
| 2. Coastal Sprint | 25.692s | 6 | 0 |
| 3. Desert Dash | 27.942s | 7 | 0 |
| 4. Forest Run | 38.258s | 6 | 0 |
| 5. Sunset Speedway | 33.842s | 7 | 0 |
| 6. Canyon Crossing | 29.817s | 7 | 0 |
| 7. Skyline Circuit | 38.958s | 7 | 0 |
| 8. Mountain Rush | 39.050s | 7 | 0 |
| 9. Neon Nights | 43.325s | 7 | 0 |
| 10. Turbo Valley | 41.717s | 7 | 0 |
| 11. Apex Challenge | 55.175s | 7 | 0 |
| 12. Final Velocity | 62.167s | 7 | 0 |

Source SHA-256: `cf761a3b9c4c2298720f7fb8e491fece518f85945412742a48bb87f2fb59635a`. These are automated actual-physics
finishes, not a claim that a person manually drove every track.

## Validation results

- Four Node suites passed: foundation/vehicle behavior, race timing/checkpoints,
  progress/storage and all-track geometry/driving/recorded replays.
- The six existing Food Fight browser suites passed against the built site:
  browser_checks, admin_checks, guest_checks, expansion_checks, expansion_edges
  and expansion_ui_checks. Food Fight's source and recovered originals are
  byte-for-byte identical to the audited main baseline c5dd2e6 for the current integration.
- Built-site browser integration passed at 1280x800 desktop, 1180x820 iPad
  landscape 820x1180 iPad portrait and 390x844 phone sizes using Chromium. Each case rendered
  all 12 Racer tracks, completed their recorded input streams through the live
  advance loop, verified sequential unlocks/results/save reloads, and checked
  Food Fight's saved coins/high score/unlocks. Actual native WASD/restart/pause
  input and touch acceleration/steering, simultaneous holds, partial release,
  out-of-button release, cancellation, mixed keyboard/touch and lost-focus
  behavior were tested. A real touch-aimed Food Fight puzzle was cleared inside
  the wrapper, preserving its own Home behavior.
- Unsupported/lost WebGL and denied-storage fallback checks passed. No uncaught
  JavaScript exceptions or failed asset requests occurred in normal tested play.
- Both games and root navigation worked through direct URLs in the built output.
  The build contains 15 site files, about 129 KB uncompressed, and ships no
  controller, replay recording, test hook, framework or external runtime library.

The browser suite caught a platform link being intercepted by menu overlays;
raising that navigation above the overlay fixed it. Tiled terrain fixed vertex
fog washing out the ground. Adaptive canvas resolution, batched scenery, removal
of touch-pad backdrop blur and freezing idle scenes reduce rendering cost. The
HTML HUD/touch hit areas retain full resolution. Render budget is two draw calls,
under 120,000 vertices, device pixel ratio at most 1.5 and at most 1.4 million
canvas pixels, with a reduced scale available on slow renderers.

Software-rendered Chromium samples varied around 21–32 rendered frames/second
at adaptive scales 0.5–0.8 on the larger viewports; the phone-sized run reached
about 51 frames/second at full scale. This is a software-GPU/cloud measurement, **not** a
physical iPad performance claim. Safari/WebKit was not available in the test
machine. Real iPad Safari, real-device landscape rotation and a person's manual
full lap of each course remain release checks. All 12 tracks have demonstrated
simulated successful drives; no track is marked complete based on geometry alone.

## Publishing and review

Branch: feature/ezyplay-racer. Production main is not merged or changed by this
work. Review and explicitly approve the PR before merging. If Cloudflare Pages
already watches main with automatic production builds enabled, that approved
merge triggers a deployment. If it is not connected, connect XoneRoland/FoodFight,
select main, framework None, build `node scripts/build.mjs`, output `dist`, root
repository directory. A free pages.dev address is sufficient. No production URL
has been verified and the site is not being claimed live.

Keep the same website origin to retain Food Fight saves. A new pages.dev domain
has different browser storage from an old netlify.app or other domain; changing
hosts does not automatically transfer those local saves.

## Files

Created: index.html; style.css; food-fight/index.html; assets/food-fight.svg;
assets/racer.svg; scripts/build.mjs; racer/index.html; racer/racer.css;
racer/racer.mjs; racer/renderer.mjs; racer/physics.mjs; racer/race.mjs;
racer/tracks.mjs; racer/controls.mjs; racer/progress.mjs; tests/racer_foundation.mjs;
tests/racer_race.mjs; tests/racer_progress.mjs; tests/racer_driver.mjs;
tests/racer_tracks.mjs; tests/racer_paths.json; tests/ezyplay_browser.py; EZYPLAY.md.

Modified existing files: README.md, DEVELOPMENT.md and netlify.toml. The existing
Netlify publish folder is preserved; its shared build command is changed for the
new root entry and routes. No Food Fight game source, recovered original,
existing test or unrelated user file was overwritten.

Final keyboard alias checks also passed for ArrowUp/Down/Left/Right and for
independent W/ArrowUp holds. Every recorded course had zero wall contacts.
The canonical Food Fight file and both recovered originals passed byte-for-byte
comparison again before publication.

## Current integration baseline

The November integration starts from c5dd2e6 and preserves its merged PR #2
admin-message edit. The older platform baseline a299daa remains historical;
tests now protect the latest main Food Fight file rather than restoring that
older presentation. See INTEGRATION_AUDIT.md. Food Fight still has 12 levels;
no accessible 100-level implementation was found.
