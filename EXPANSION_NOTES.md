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
