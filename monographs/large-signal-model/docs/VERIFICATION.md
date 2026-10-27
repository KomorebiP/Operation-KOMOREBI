# Verification and reproducibility

The formal companion is preserved byte for byte under `Lean/`. Its existing `MANIFEST.json`, coverage bindings, source checkpoint and accepted execution report remain unchanged. Repository support and the current publication are outside that immutable subtree.

The accepted execution checks all 254 mathematical modules through fresh compilation and individual kernel replay. It checks the complete root import, every explicitly named declaration's axiom dependencies, exact rational program examples and 183 isolated rejection controls. Current receipts also bind their source and output hashes. Three inherited negative controls were repaired because unrelated elaboration errors had obscured their intended false goals. Their original source, original diagnostics, repaired source and clean results remain in the lineage evidence.

The source index counts 4,454 explicitly named declarations and 2,887 named theorems. These are different units from the 87 manuscript propositions. Compiler-generated declarations are outside the named-source count and are covered by module checking. The 331 example-theorem count uses the explicitly documented dedicated-example-module convention.

## Exact scope

Read `Lean/COVERAGE.md` for mathematical hypotheses and mapped endpoints. The complete set is P1 through P87. This count does not imply that every narrative sentence, every empirical assumption or every implementation outside the formal project was proved in Lean.

The source snapshots under `Lean/source/` and historical receipts preserve their earlier frontmatter and status text as reviewed inputs. The current monograph and current coverage map report the completed scope. The mathematical body of the publication is unchanged by its formal-status update.

## Repeating checks

First validate the delivered file inventory. Then run metadata and source-guard checks. A complete new Lean run requires the separately restored pinned runtime or the GitHub full-verification environment adapter. Installing Lean and running only `lake build` does not reproduce the additional axiom audit, individual kernel replays and rejection checks.

The full checker uses sequential module execution and a 900-second per-stage timeout by default. Fresh build output and new reports should be kept outside the accepted receipt location. The shipped receipts attest to the delivered source; a future run should retain its own source-bound result.

Upstream Lean and Mathlib remain pinned dependencies. Their entire source trees are not rebuilt or replayed by this project's checker. Historical author probes, failures, timeouts and interrupted jobs remain historical and do not substitute for the final accepted current-source execution.

## Distribution integrity

The outer release manifest covers the complete repository package, including hidden `.github` files. The frozen Lean manifest covers its subtree independently. Git attributes preserve checked Lean bytes instead of performing platform line-ending conversion. The final ZIP is extracted and checked against both inventories before delivery.
