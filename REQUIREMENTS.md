# Food Fight — Product requirements and backlog

## Gameplay and rewards
- Preserve current Endless Run and 12-level Puzzle Mode, pointer/touch controls, and mobile/iPad/desktop layout.
- Endless Run awards coins at the end of a run based on final score. Current intended rule: 10 coins per 100 points, awarded at run end.
- Puzzle Mode awards coins on first-time level clears only unless the user later changes this rule.
- Player currency is game-earned coins only; no real-money purchases.

## Current architecture
- Static HTML/CSS/JavaScript hosted on Ship.page.
- No Supabase.
- No Firebase.
- No external backend in the current phase.
- Save progress locally on the iPad/browser using local storage.
- Anonymous play does not need cross-device persistence.

## Accounts and profiles — local prototype only
The desired product direction includes account-style screens and profiles, but with no backend these must be treated as local-device prototypes rather than secure real accounts.

Desired fields/features:
- Signup fields: first name, last name, username, email, password.
- Login flow: email + password.
- Username should be permanent once created.
- Duplicate local usernames should be rejected.
- Optional Remember Me behavior.
- Preset avatars.
- Public-facing profile should expose username/avatar and game statistics, not real names or email.
- Profile statistics: highest Endless score, total Endless score, total coins earned, puzzle levels completed, achievements, owned/equipped items, best puzzle times, account creation date.

## Anonymous play
- Anonymous play exists and can be enabled/disabled from the local admin prototype.
- Disabling anonymous play should take effect immediately within the current browser/device session.
- Because there is no backend, the toggle is not global across devices.
- Anonymous mode should avoid long-term persistent progression where practical.

## Shop and inventory
- Items: launchers, food projectiles, skins.
- Rarities: Common, Uncommon, Rare, Epic, Legendary.
- One ownership instance per item.
- Equip one launcher, one projectile and one skin at a time.
- Currency: game-earned coins only.
- Admin prototype may manage local catalogue/pricing data.

## Codes and announcements — local prototype
- Manual code entry.
- Rewards may include coins, items or skins.
- Optional expiry.
- One redemption per local player/profile.
- No overall redemption cap.
- Announcements may be displayed locally to all modes on the device.

## Friends and leaderboards — future/backend-dependent
Desired future features include friend requests, friend codes, global/friends-only leaderboards, public profiles and cross-device data. These cannot be genuinely shared or securely enforced with static hosting/local storage alone. Do not fake them as global services.

A local single-device mockup is acceptable if clearly labelled as such.

## Admin — local prototype only
Desired controls include:
- Player/profile management.
- Account moderation concepts.
- Shop item management.
- Shop code management.
- Anonymous-play toggle.
- Announcements.
- Leaderboard moderation.
- Overall game statistics.

With no backend, these controls are local only. Do not describe client-side passwords or permissions as secure production authentication.

## Development constraints
- Preserve classic gameplay and visual style.
- Keep iPad/mobile and desktop support.
- Prefer one HTML file for deployment.
- Work incrementally and test after each meaningful change.
- Do not introduce Supabase, Firebase or another backend unless the user explicitly requests a new architecture.
- Never put secrets or real credentials in client-side source.

## Suggested implementation order
1. Audit the recovered primary HTML and identify broken or incomplete behavior.
2. Copy it to `Food_Fight_Development.html`; preserve the originals.
3. Verify Endless, Puzzle, shop, touch controls and local save still work.
4. Fix coin/reward rules and anonymous-mode behavior.
5. Improve local account/profile prototype without pretending it is server-secure.
6. Improve local admin controls and announcements.
7. Add/refine achievements, shop content, puzzle levels and UX.
8. Test on iPad/mobile and desktop.
9. Produce a clean single-file Ship.page deployment build.

## Future architecture decision
If the user later wants genuine cross-device accounts, global leaderboards, friends, shared codes, secure admin roles or global moderation, stop and discuss adding a backend before implementing those features as production functionality.
