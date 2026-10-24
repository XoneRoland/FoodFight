# Small feature expansion

Baseline: commit `530fb1e`, protected by branch `feature/small-expansion-20261024`.
The source of truth is Food_Fight_Development.html; recovered files remain unchanged.

Audit: all code is in one HTML file. Existing save: bulletDashSave; catalogue:
foodFightLocalCatalogueV1. Coins were changed directly in puzzle completion,
Endless results, codes and shop purchases. Puzzle shots already have unique
hitTargets, a remaining-shot count and lifetime; Endless launches one food at
run start and dodges obstacles (it has no target-shooting mechanic). The current
shop has launcher/food skins and custom admin items; it does not contain a
separate rarity implementation. Existing keyboard support is native buttons,
forms and admin Enter; gameplay uses dragging. No existing controls are removed.

Implementation plan: shared recorded statistics/coin credits; achievements;
local daily rewards/missions; puzzle best stars; backgrounds; per-projectile
combos; final compatibility and interaction checks. Each step gets a commit.

Step 2: statistics and a shared creditCoins function now use real launches,
unique projectile/target contacts and run starts. Puzzle selection/reset alone
is not counted as play. New historical counters start at zero; existing high
scores and completion data remain their source of truth. New data is namespaced
as featuresV1 within bulletDashSave, deliberately using one atomic storage write
for coins and claims rather than two independent records. Initialization does
not write a migration back to storage. Targeted stats/malformed-data/legacy-save
checks and the existing browser suite passed.

Step 3: six achievements now show progress, Locked/Completed/Claimed state and
manual one-time rewards. Existing distinct puzzle clears count; shots, hits and
lifetime coin earnings use recorded counters only. Statistics include claims.
Targeted achievement/refresh/duplicate/storage-failure checks passed. Claims and
the existing coin balance are committed together; failed writes grant nothing.

Step 4: local-calendar daily rewards follow the requested seven amounts, retain
cycle position after missed days and block same-day repeated claims. Missions
use a deterministic rotation of three different IDs per date, reset only their
daily counters and share actual gameplay events. Reward/code earnings count for
lifetime coins; only puzzle/Endless/combo earnings count for gameplay missions.
Tests passed across local midnight in Australia/Perth, refresh, skipped dates,
cycle wrap, mission progress/claims/reset, and failed-storage reward claims.

Step 5: existing cleared puzzles conservatively receive one star in memory,
without an initialization write. Completed runs get shots-used ratings and keep
their best. Level cards explain each level's thresholds; win results and stats
show stars. Unlock/completion mechanics and all level templates are unchanged.
The short levels can legitimately award two stars even with their full shot
budget; Finale uses six/seven shots for three/two stars. Any clear still wins.
Migration, improved clear, lower-rated replay and refresh checks passed.

Step 6: shop background cards use the existing card style, coin balance and
single-write purchase transaction. Classic retains the original canvas fill;
Kitchen Chaos (250) and Midnight Snack (500) use lightweight gradients and keep
all collision geometry untouched. Buying, switching without paying again,
refresh persistence and lifetime-earnings separation checks passed.

Step 7: combos use successful target contacts only and credit each projectile
once, preserving existing target piercing/multi-hit physics. Every third hit
projectile adds 10 gameplay coins. A projectile retiring without a target hit
resets the chain; restarting/leaving a round also clears it. Combo indicators
are subtle and only shown in active Puzzle gameplay; Endless has no hit event.
Targeted tests passed for milestone credits, repeated contacts, actual existing
multi-target contacts, miss reset, navigation reset and atomic reward storage.

Final checks: browser_checks.py, admin_checks.py and guest_checks.py passed at
 desktop and iPad portrait/landscape sizes, including storage failure scenarios.
expansion_checks.py passed all feature stages. expansion_edges.py passed failed
writes for daily/mission/background rewards, repeated stale button events,
Los Angeles midnight/date rollback, stale mission dates, malformed new data and
stale-tab protection. expansion_ui_checks.py passed at desktop, iPad portrait,
iPad landscape and phone sizes with actual browser touch/mouse input and native
keyboard button activation, a real puzzle clear, all new panels and refresh.
No JavaScript exceptions occurred in these runs. JavaScript syntax and diff
whitespace checks passed. Original puzzle physics is byte-identical after removing
additive event hooks; all 12 templates and recovered originals are unchanged.

Limitations: real iPad/Safari and a full manual solve of all 12 puzzles remain
unrun. Old saves have no lifetime shots/hits/earnings history, and the baseline
has no separate rarity system or keyboard movement controls; existing skins,
pointer gameplay and native keyboard controls are retained. The storage layout
is additive and tested with representative legacy progress, not a read of the
user's actual iPad data. Local device-date manipulation remains possible.

A repeated phone-sized UI run initially exposed a test-input timing issue: an
instant CDP drag/release was followed by pointer/touch events without a native
click. The test now uses six paced finger-movement steps and captures input
traces on failure. Five consecutive phone runs passed. The game's original touch
handlers were retained; no touch workaround or physics change was shipped.
