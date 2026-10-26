# Food Fight — Codex project

## Start here
Food Fight is a standalone browser game for iPad/mobile and desktop. The recovered project is intentionally simple: HTML, CSS and JavaScript with no build step required.

The primary recovered source is `source/Food_Fight_Classic_Anonymous_Admin.html`. The earlier `source/Food_Fight_Classic_Colour.html` is retained as a fallback reference. Do not overwrite either recovered original when beginning development.

Read `AGENTS.md`, `REQUIREMENTS.md`, and `CODEX_START_PROMPT.md` before modifying code.

## Current release and deployment
The current playable release is `Food_Fight_Development.html`, including the
seven-feature expansion and all 12 original puzzle levels. Recovered source
files remain preserved.

For Netlify, connect this GitHub repository and select `main` as the production
branch with the repository root as the base directory. `netlify.toml` copies the
current game to `dist/index.html` and publishes only `dist`. No build dependencies
are required. The site root opens the complete single-file game. See
`DEVELOPMENT.md` for local reproduction and validation.


## Final architecture decision
- Host: Netlify static hosting (the game remains compatible with Ship.page).
- Backend: **none for the current phase**.
- Do **not** add Supabase or Firebase unless the user explicitly changes this decision later.
- Persistence: browser/iPad local storage only for now.
- Prefer a single deployable HTML file unless there is a strong reason to split the project.

## Current implementation
- Endless Run and Puzzle Mode with 12 puzzle levels.
- Launcher/food projectile shop, coins, unlocks and equipped items.
- Pointer/touch controls suitable for iPad/mobile and desktop.
- Browser-local save using `localStorage`.
- Anonymous play and a browser-local anonymous-play toggle.
- Prototype admin login exists in the recovered HTML.

## Important limitations
Because the current project has no backend, features that require shared server data cannot be truly global or secure. This includes real multi-device accounts, global leaderboards, globally enforced admin controls, secure password recovery, shared friend systems and tamper-resistant economy validation.

Treat the current login/admin screens as local prototypes only. Never claim a hardcoded client-side password is secure authentication. Do not add secrets, private keys or real passwords to this repository.

## Development rules
- Preserve the classic Food Fight look and existing gameplay unless a task specifically changes them.
- Keep iPad touch controls working.
- Work incrementally and keep each change testable.
- Create a development copy before major changes; preserve the recovered originals.
- Prefer local-only implementations that work on Ship.page without external services.
- If a requested feature cannot be securely implemented without a backend, explain that clearly and build only a safe local prototype unless the user changes the architecture decision.

## Recommended first Codex task
Audit the primary source without changing it. Create a development copy named `Food_Fight_Development.html`, verify that the existing game still runs, then make one small testable improvement at a time.
