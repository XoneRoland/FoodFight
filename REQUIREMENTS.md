# Food Fight — Product requirements and backlog

## Gameplay and rewards
- Preserve current Endless Run and 12-level Puzzle Mode, pointer/touch controls, mobile/iPad/desktop layout.
- Endless Run awards coins at the end of a run, calculated from final score. **Conversion formula TBD**.
- Puzzle Mode awards coins on every successful clear, including replay. Current prototype first-clear-only logic must change. Guard against duplicate network submission, not intentional replays.
- Player coins earned through gameplay and redeemable codes; shop is not real-money based.

## Accounts and privacy
- Registration: first name, last name, unique case-insensitive permanent username, email, password.
- Sign in: email and password; optional Remember Me.
- Email-based password reset; never expose passwords to admins.
- Permanent account deletion and suspension. Suspended users cannot log in/use online features.
- Public profile: username, preset avatar, highest Endless Run score, total Endless Run score, total coins earned, puzzle clears, achievements, owned/equipped items, best puzzle times, creation date.
- Real name and email visible only to authorized admins, not public users.
- Anonymous play can be switched on/off globally by admin; disabling it must affect active guest sessions. Anonymous play must not save persistent progress.

## Shop and inventory
- Launchers, food projectiles, cosmetic skins.
- Rarity tiers: Common, Uncommon, Rare, Epic, Legendary.
- At most one ownership instance per item per account; one launcher, one projectile, one skin equipped at a time.
- Admin can manage catalogue and pricing.

## Codes and announcements
- Admin creates a specific code manually; rewards can be coins, items or skins; optional expiry.
- Each player can redeem each code once; **no global redemption limit**.
- Admin announcements are visible to all users, including guests.

## Social and rankings
- Find friends by username or unique friend code; friend requests must be accepted; support remove/block.
- Global and friends-only leaderboards: best Endless Run score, total Endless Run score, puzzle levels completed, best puzzle times.
- Search/view public profiles by username/avatar.

## Admin
- Separate admin access using authorized user roles, not a hardcoded HTML password.
- View users’ first/last name, username, email and statistics; suspend/delete accounts.
- Manage catalogue, codes, anonymous-play toggle, announcements, leaderboard moderation, overall statistics.
- Use server-side security rules/privileged functions for admin operations.

## Architecture constraints
- Ship.page static front end; Firebase is the proposed backend, not yet configured.
- Avoid Supabase: user explicitly rejected it as too complex.
- Prefer free-tier-friendly services and minimal manual configuration.
- Use incremental changes with functional tests and clear deploy steps.

## Suggested implementation order
1. Audit existing HTML; preserve working game and visual design; identify broken behaviors.
2. Add Firebase initialization (after obtaining Firebase web app config); set up email/password Authentication.
3. Design Firestore collections and strict security rules; distinguish public and private user fields.
4. Account registration/login, profile setup, username uniqueness and password reset.
5. Persist authenticated progress; implement guest session-only progress.
6. Secure coin awards, inventory purchase/equip, puzzle repeat awards and code redemption.
7. Leaderboards, public profiles, friend system.
8. Admin authorization, global guest toggle, announcements, moderation.
9. End-to-end tests, iPad/mobile QA, Ship.page deployment.

## Open questions
- Exact Endless Run score-to-coin conversion.
- Coin payout for every puzzle clear (currently prototype first clear = 10; 10 per clear is a reasonable proposal but not separately confirmed).
- Firebase project details/config and whether free-tier limits suffice for chosen server-side verification features.
- Production admin account provisioning and account deletion process.
