# EzyPlay implementation record

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
Every run had zero recovery resets. tests/racer_paths.json records quantized
control streams and sampled paths; the test replays them independently and
checks a SHA-256 of simulation/track/controller sources. No controller is shipped
in the website. Geometry validation checks continuity, widths, slopes, start,
finish, ordered gates and ramp landing runouts. Roads have no required gaps;
ramps produce real gravity-driven jumps while remaining drivable at low speed.
The automated runs reached 3.48m, 5.80m and 3.11m above the road on tracks 7, 10
and 12 respectively. Medal times are tuned against these successful runs; a
bronze finish always advances progression.
