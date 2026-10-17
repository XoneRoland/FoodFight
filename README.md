# Food Fight — Codex handover (17 October 2026)

## Start here
This archive contains two **recovered original HTML files** and a product/development brief. The most advanced recovered source is `source/Food_Fight_Classic_Anonymous_Admin.html` (39,196 bytes). The earlier `source/Food_Fight_Classic_Colour.html` (34,528 bytes) is included as a fallback. These files have not been rewritten for this handover.

Open the primary HTML file in a browser to inspect the current prototype. The project is a standalone canvas game with inline CSS and JavaScript; no build step is required. The files are not evidence of a working backend.

Read `REQUIREMENTS.md` and `CODEX_START_PROMPT.md` before modifying code.

## Confirmed decisions
- Product: Food Fight, a browser game suitable for desktop, iPad and mobile.
- Host: Ship.page (user has a free plan; static HTML/CSS/JS hosting).
- Backend: **not Supabase**. Firebase was proposed and the user agreed to start its setup, but **no Firebase project configuration or completed integration has been provided in this conversation**.
- Preserve the simple/classic home-screen style and existing gameplay.
- Work incrementally, do the coding for the user where possible, and explain setup in small steps.

## Current implementation (verified by reading the primary HTML)
- Endless Run and Puzzle Mode; 12 puzzle levels.
- Launcher/food projectile shop, coin balance, unlocks, equipped items.
- Browser-local save in `localStorage` key `bulletDashSave`.
- Anonymous play button and browser-local toggle stored under `foodFightAnonymousPlayEnabled`.
- Prototype admin login; the password is hardcoded in client-side source and **must not be used as production authentication**.
- No Firebase SDK, server-side authorization, real cloud accounts, shared leaderboards or cross-device synchronization in the recovered primary file.

## Important discrepancies to fix
- Current puzzle code gives 10 coins only on the **first** clear; the agreed requirement is coins on **every successful clear**, including replay.
- Current guest progress is stored locally; the agreed requirement is **no persistent anonymous progress**.
- Current anonymous-play toggle only applies to one browser; agreed requirement is globally enforced and effective for active guest sessions.
- Current admin prototype has a client-side password; replace with Firebase Authentication and server-enforced admin permissions before public deployment.
- Endless Run rewards should be granted at run end based on final score, but exact conversion formula is still to be confirmed.

## Security and deployment
Never put service-account private keys, admin passwords or other server secrets into static HTML or the repo. Firebase web config is not a secret, but use strict Firestore Security Rules, authenticated access, and trusted server-side validation for economy/leaderboards. Treat all browser-generated scores and coin claims as untrusted. Do not claim tamper-proof scoring without a defensible validation approach. Protect children’s privacy: public usernames only; do not expose names/emails. Test on local browser and on Ship.page after deployment.
