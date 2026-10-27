# AVOC v0.23.0 — verification record

## Final result

- **123/123** current local compilation targets passed.
- **1184/1184** exact-name axiom reports passed.
- **55/55** deliberately invalid proof files were substantively rejected.
- **52** new theorem/lemma declarations in three modules.
- **110/110** inherited non-audit mathematical source modules are byte-identical to v0.22.
- Independent comment-aware source census agrees with the inventory.
- Positive source contains no proof placeholders, project axioms, native evaluation
  shortcuts, or unsafe declarations. Axiom union: propext, Classical.choice, Quot.sound.

The baseline input SHA-256 is `8fc95d7a9fce9461f51a07d335cb2de692887e323e87f52bdd986f69e3a46f63`. Its original 4,594 payload
hashes matched before modification. The original release was not edited.

## Build and trust scope

Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d;
mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. All nine recorded external
revision pins match. The seven portable parts passed their payload CRC/SHA checks,
and the assembled archive matched SHA-256
66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34 before extraction.

After finalizing the mathematical sources, the local build was deleted and all 123
targets rebuilt. External binary caches were retained, not rebuilt from source.
The helper records source-before/source-after, direct local import hashes, output
hashes, actual argv, logs, return codes and timeouts. Descendants of changed local
imports are invalidated. The final collector rechecks those exact hashes.

This does not independently verify Lean's kernel/compiler, cached dependencies,
Python or the host. Counts include auxiliary lemmas and examples, not independent
mathematical discoveries.

## Current executed regression

The actual Lean `UpgradeRuntime.execute` was compared with an independent Python
ledger/score oracle on **1442** finite campaign cases.
The outputs contain 376 promoted transitions,
3202 funded rejected transitions, and 821
unfunded transitions. These counts include repeated states and are not counts of
unique improvements. The suite checks intermediate ledgers, scores, charges,
revision/authority binding, final selected-component decisions and state-visit counts.

It covers all proposal sequences of length at most two over seven declared request
patterns at 20 budgets, 300 seeded sequences of length 3–12 (seed 230023), and two
additional cost/staleness sequences. There are also **13** wrapper-defense cases
and **11** malformed raw-wire rejections. A controlled source-drift test restores
exact workspace bytes in `finally`; no original release or user registry is changed.

Four example configurations were run again against final compiled sources. They
cover successful promotion, expensive failed search, changed authority/objective
requests, and insufficient switching credit. The 70-to-7 work comparison is a
counted state-visit result, not a wall-clock or empirical LLM speedup.

The old live filesystem, crash and retry suites were NOT rerun in this block.
Their retained evidence is historical. The new executable does not write to those
systems and is not claimed to be a durable deployment coordinator.

## New negative tests

- FalseUpgradeContract: rejects promotion of the contract-violating cheap candidate.
- FalseUpgradeFreeRejection: reduces erased evaluation cost to the false equality 3=0.
- FalseUpgradeGuaranteedProfit: refutes nonnegative campaign net return in the -13 witness.
- FalseUpgradeObjectiveChange: rejects promotion under a changed objective identifier.
- FalseUpgradeUniversalThreshold: refutes removing NoRevival in a checked improving-service example.

Positive library theorems separately establish the relevant obstructions. A failed
proof script alone is not a theorem of negation. Missing imports and timeouts were
not accepted as mathematical negative evidence.

## Evidence locations

Current records are in `results/v0.23.0/`: summary.json, source_counts.json,
declaration_inventory.json, new_declarations.json, clean_*.json/log,
full_axiom_audit.*, negative_*.json/log, upgrade_test_*.json,
upgrade_requests_*.json, upgrade_output_*.jsonl, upgrade_defense_tests.json,
and demo_*.json. Package CRC/SHA checks are independent delivery checks, not proofs.
