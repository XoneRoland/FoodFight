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
