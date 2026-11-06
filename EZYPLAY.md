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
