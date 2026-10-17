# Paste this into Codex

You are continuing an existing browser game project named Food Fight.

Before changing anything, read:
- `README.md`
- `REQUIREMENTS.md`
- `AGENTS.md`
- `source/Food_Fight_Classic_Anonymous_Admin.html`

The recovered primary HTML is the working baseline. Preserve its classic UI, Endless Run, 12 puzzle levels, shop, touch controls and overall game feel. `source/Food_Fight_Classic_Colour.html` is a fallback reference and must also remain untouched.

## Architecture decision
The current project uses:
- Ship.page static hosting
- HTML/CSS/JavaScript
- browser/iPad local storage
- no Supabase
- no Firebase
- no external backend

Do not add or configure a backend unless the user explicitly changes this decision. Do not invent API keys, cloud services or server infrastructure.

## First task
1. Audit the primary recovered HTML without modifying it.
2. Summarize the current game structure and any obvious bugs or fragile areas.
3. Create a development copy named `Food_Fight_Development.html` from the primary recovered source.
4. Make only the smallest useful, testable improvement first.
5. Keep all changes compatible with iPad/mobile and desktop.
6. Preserve a simple single-file deployment path for Ship.page.

Treat login/admin/account features as local prototypes only. Do not claim client-side passwords, localStorage or browser-only permissions are secure production authentication. If a requested feature genuinely requires a backend, explain that rather than faking a global or secure implementation.

Work incrementally, test the affected behavior, and clearly state which file changed and how to verify it.
