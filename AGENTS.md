# AGENTS.md — Food Fight Codex instructions

## Project goal
Continue developing Food Fight as a simple, reliable browser game that works well on iPad/mobile and desktop and can be deployed to Ship.page as static files.

## Source of truth
Read these before making changes:
1. `README.md`
2. `REQUIREMENTS.md`
3. `source/Food_Fight_Classic_Anonymous_Admin.html`

Use `source/Food_Fight_Classic_Colour.html` only as a fallback visual/reference source.

## Architecture guardrails
- Current architecture is static HTML/CSS/JavaScript only.
- Persistence is local browser storage.
- Do not add Supabase.
- Do not add Firebase.
- Do not add another backend or external database unless the user explicitly changes the architecture.
- Do not introduce secrets, API keys, service credentials, or real passwords into client-side files.

## File safety
- Never overwrite the recovered source files in `source/`.
- Create and work in `Food_Fight_Development.html` for active development unless the user asks for a different structure.
- Keep the project deployable as a single HTML file where practical.
- Make small commits with clear descriptions.

## UX and gameplay priorities
- Preserve the classic Food Fight look unless the task specifically asks for a redesign.
- Preserve Endless Run, Puzzle Mode, shop, coins, launcher/projectile selection and touch controls.
- Keep tap/drag interaction comfortable on iPad.
- Avoid desktop-only hover interactions for important controls.
- Avoid regressions in existing puzzle levels.

## Local-only account/admin features
- Treat login, profiles, admin controls, announcements, codes and leaderboards as local-device prototypes unless a backend is later introduced.
- Never describe a hardcoded password or localStorage gate as secure authentication.
- Never pretend data is global, cross-device, tamper-proof or server-validated when it is not.
- If a requested feature genuinely needs shared server state, state that limitation clearly and implement only a clearly labelled local prototype unless the user changes architecture.

## Testing expectations
After each meaningful change:
- Check the HTML still loads without syntax errors.
- Test the specific changed feature.
- Re-test home navigation, Endless Run, Puzzle Mode, shop and touch/pointer controls when relevant.
- Preserve local save compatibility where possible.
- Explain how the user can verify the change on iPad/browser.

## Codex working style
- Inspect first, then edit.
- Prefer the smallest useful change.
- Do not refactor large sections just for style.
- Preserve working behavior unless the task intentionally changes it.
- Tell the user which file changed and what was tested.
