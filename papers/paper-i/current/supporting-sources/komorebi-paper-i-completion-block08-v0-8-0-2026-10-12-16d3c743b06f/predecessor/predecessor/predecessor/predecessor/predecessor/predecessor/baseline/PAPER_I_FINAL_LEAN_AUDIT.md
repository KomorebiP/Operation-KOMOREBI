# Paper I: final Lean audit

**Result: PASS for the complete current 35-row formal contract.**  
**Date:** 10 October 2026  
**Component:** Projector-Resolved Seed Calculus I, formal v1.0.2  
**Source changes:** none

The current Paper I formalization was rebuilt from its actual source rather than accepted on the strength of an old PASS report. All twenty source files compiled into a previously empty local object directory under the pinned compiler and dependency state. The explicit audit, declaration inventory, same-kernel module replay, and negative controls also completed.

## Results

| Check | Actual result |
|---|---:|
| Predecessor manifest entries checked | 837 / 837 |
| Production Lean files rebuilt | 20 / 20 |
| Production source lines | 7,125 |
| Completion-contract rows | 35 / 35 |
| Mapped declaration names resolved | 84 / 84 |
| Mapped theorem declarations | 73 |
| Mapped definitions or equivalences | 11 |
| Inherited namespace gate | 1,126 entries passed |
| Expanded source-owned gate | 1,152 entries passed |
| Compiled modules replayed through the kernel | 20 / 20 |
| Intended rejection controls | 4 / 4 rejected correctly |
| Positive foreign-namespace gate control | Passed |
| Exact boundary-consumer theorems | 4 / 4 |
| Final source and object identity checks | 20 / 20 |
| Successful expected-outcome command checks | 52 |

Two source files are import-only modules. The 1,152-entry inventory includes definitions, constructors, recursors, and generated proof helpers. It is not a count of 1,152 independent or novel mathematical theorems. Its 720 theorem-kind entries also include generated helpers. The mapped public contract contains 73 theorem declarations and 11 definitions or equivalences.

## What improved in this audit

The existing fail-closed audit filtered names under the `Komorebi` and `KomorebiVerification` namespaces. That correctly inspected 1,126 entries but did not enumerate every declaration owned by the source modules. The new audit uses source-module ownership. It includes **25 private declarations and one generated declaration in another namespace**, bringing the checked inventory to 1,152. Every one passed.

This is an improvement to the axiom inventory, not a claim that 26 missing mathematical proofs were supplied. Their source already compiled. No production definition, statement, proof body, or dependency pin needed alteration.

The only reported transitive axioms were `propext`, `Classical.choice`, and `Quot.sound`. No production declaration depended on `sorryAx` or an additional custom axiom. The production-source policy found no active proof placeholders, unsafe declarations, opaque declarations, or native-decision proof shortcuts among the forbidden patterns. Deliberately invalid fixtures are kept separately under `tests/fixtures` and are not part of that production-source claim.

## What was actually executed

The exact compiler is Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`. Mathlib is pinned to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All nine dependency manifest entries were checked against the actual cached Git HEADs. Source files were compiled serially with warnings treated as errors and automatic implicit-variable invention disabled.

The main build also compiled the root aggregator and the standalone audit module. All 84 mapped names were resolved in a separately elaborated file, and their types and axioms were printed. The standalone gate was then executed explicitly. This matters because the root library does not import that audit gate.

A subsequent run replayed the constants of each of the twenty compiled modules using the pinned official `replayFromImports` function. The wrapper selects exactly one module per process, avoiding the command-line checker's prefix-wide parallel behavior. This is a **same-kernel replay**, not an independently implemented external verifier. Upstream cached imports were reused. Mathlib was not freshly rebuilt or fully replayed.

The main successful run took 512.167 seconds of recorded command time. The ownership and replay run took 410.975 seconds. The added guard and boundary controls took 28.857 seconds. These totals exclude recovery, inspection, packaging, and failed attempts.

## Controls and mathematical boundaries

The normal strict compiler rejected a false natural-number equality and a placeholder proof. The expanded gate then rejected a deliberately imported custom axiom in a nonproject namespace and an imported placeholder that had been compiled with warnings-as-errors deliberately disabled. A clean theorem in that same nonproject namespace was accepted. This checks that the new gate follows module ownership rather than rejecting names merely for being outside a prefix.

Four additional consumer theorems passed: every entry of the rational matrix `[[1,1],[-1,-1]]` is nonzero, that matrix squares to zero, the zero module has seed rank zero, and the natural two-dimensional full-matrix module has rank one. The first pair illustrates exact cancellation despite dense support. These are audit regressions, not new contract rows.

The type and source review confirms that generation uses actual submodule spans, packet coordinates use actual projector ranges, and transfer blocks are actual composed linear maps. The report retains the distinction between shared and independent actions, algebraic and topological results, and obstruction and sufficiency. See `audit/SEMANTIC_REVIEW.md` and the complete declaration crosswalk.

## Scope that must remain explicit

**The 35-row formal contract is not the expanded monograph's 108-record inventory.** Rows 10, 13, 14, 32, and 35 retain supplied decomposition, extraction, quotient, canonical-form, or spectral certificates as stated in the normative map.

In particular, the cyclic-matrix result takes the minpoly/charpoly bridge as an input and assembles the displayed equivalence. It does not independently construct that bridge for an arbitrary matrix. The split-semisimple result transports a concrete formula through supplied equivalences; it does not construct a Wedderburn decomposition or the nonsplit division-algebra case. The exact graph-rank specification does not provide a verified executable eigensolver.

These are declared scope boundaries, not newly discovered compiler failures. No unresolved proof obligation remains within the audited current contract. No completion claim is made for its excluded extensions, the historical v0.2.0 ancestor tranche, Python implementations, or Papers II–XII in this audit sweep.

## Failures and recovery

Not every attempt succeeded. The direct compiler download failed because the container could not resolve GitHub. The matching offline runtime was recovered from Library and authenticated against its archive hash.

The first foreground build was interrupted by the 180-second container command limit after one module compiled. The accepted build restarted from a separate empty output directory. A diagnostic `leanchecker --help` invocation also failed: that pinned checker has no help flag, so it selected a broad default target, launched concurrent replay, and was killed under the 4 GiB memory ceiling.

Two new audit-instrumentation attempts were not accepted as final runs. The first extra audit was deliberately stopped and refactored to cache module names. The first exact-replay wrapper then failed type inference between BaseIO and IO; adding an explicit IO result type fixed the wrapper. The final ownership audit and all twenty replays were rerun after that correction.

The original logs, source snapshots, and incident records remain in the package. None of these recoveries changed Paper I's mathematical sources. `evidence/RUN_INDEX.json` distinguishes raw interrupted receipts from current run status. No process remains running after this handoff.

## Reproduction and handoff

Run `bash scripts/run_audit.sh /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 /absolute/path/to/new-output` from Linux or WSL with Python 3 available. The output path must not already exist. The matching compiler and dependency cache are external prerequisites, not included in this compact source/evidence ZIP. Do not run `lake update` when reproducing this pinned state.

The three constituent verifiers were actually executed. The composed shell launcher was syntax-checked but was not used to duplicate the entire accepted run. The original mathematical component and its license-status record are preserved without selecting a new publication license.

The package contains all twenty current Lean sources, project configuration and manifest, the normative contract, exact compiler logs and objects, complete source-owned inventory, all mapped declaration locators, semantic notes, controls, failed attempts, hashes, and the progress ledger.

**Next restart: Paper II. Paper I's audited formal component can remain frozen.**
