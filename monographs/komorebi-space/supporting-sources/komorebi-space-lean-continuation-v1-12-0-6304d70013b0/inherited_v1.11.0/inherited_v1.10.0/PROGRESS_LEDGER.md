# Komorebi Space — progress v1.10.0

Accepted checkpoint: **KS-v1.10.0-WR03-WR05-complete**. Parent: v1.9.0 full monograph. Acceptance recorded 2026-10-12T21:50:53.685949+00:00.

## Completed in this block

| Group | Result |
| --- | --- |
| WR03 | Every nonnegative budget has an attained minimum; monotonicity, convexity, the full Lipschitz estimate, the real-budget limit, and both exact feasibility equivalences are formalized. |
| WR04 | The dual formula is an attained maximum at every budget, with a unit-ball witness and strict exclusion certificate. |
| WR05 | Both profiles use one correction space and ball; the full operator/data perturbation allowance and nominal witness certificates are formalized. |

The four modules add **39 explicit theorems and 43 named public declarations**. The actual complete types were independently reviewed. No finite-dimensionality, separability, closed-range, injectivity, positive-budget, or assumed-optimizer hypothesis was added. The printed proof audit also found all three target theorem groups valid as written.

## Verification

- Clean cumulative build: **151 targets**, comprising **148 production modules and three roots**, starting with no project object files.
- Complete environment audit: **4,935 declarations**; cumulative explicit theorem/lemma count **1,619**. Only `propext`, `Classical.choice`, and `Quot.sound` appear in the accepted axiom union.
- **30 control files**: 8 positive, 20 intended compiler rejections, and 2 policy rejections. Invalid cases must fail at the intended obligation, rather than from a missing import or resource failure.
- **219 recorded commands** passed their required outcomes, followed by independent terminal validation. Sources, compiled project objects, and **130,284 runtime/cache files** passed their recorded endpoint identity checks.
- Exact source, command, type, axiom, review, and runtime identities are retained in the handoff. The full monograph was rebuilt and visually checked after its status and erratum changes.

## Mistakes found and corrected

The printed text incorrectly called the residual the projection. The new edition distinguishes the nearest reachable image from the datum-minus-image residual. No theorem statement changed. The original source and explicit erratum are retained.

Development attempts exposed Lean API, notation, expression-order, strict-linter, documentation-placement, and object-path errors. All were corrected without weakening the target or disabling strict checks. Positive boundary tests initially exposed additional simplification/linter errors, also corrected. Every numbered failed source and diagnostic is preserved alongside the successful attempt.

Independent verification review caught provenance gaps in cached Python helper loading, runtime/cache endpoint checks, exporter binding, and terminal evidence binding. These were fixed before the accepted clean replay. Package review added explicit receipt/source/publication binding and direct comparison with the hash-pinned predecessor archive, and caught an omitted historical scripts directory before release. The records distinguish these corrected tooling failures from mathematical gaps.

The detailed type/axiom export took about 386 seconds, longer than estimated. A proposed interruption to optimize inherited type printing was overtaken by the export's successful completion: the signal attempt found no process and affected none. The original run and frozen helpers were retained. No interrupted replay or mathematical failure is claimed for this coordination event.

## Current coverage and next work

**Nine of sixteen WR groups are complete:** WR01–WR07, WR13, and WR14. **Two are partial:** WR09 and WR16 retain written limiting conclusions. **Five remain written-only:** WR08, WR10–WR12, and WR15.

The next major block is **WR08**, the complete regularization limit alternative: convergence of fitted data and residuals, vanishing weighted penalty, strong convergence in the attained case, and norm divergence otherwise. Its strong-convergence branch is the principal next obligation. WR09 and WR16 limits follow naturally after that block. The exact restart contract is `budget_v1.10.0/NEXT_RESEARCH_BLOCK.md`.

The global independent monograph audit, executable certificate refinement, application-specific model identification, and updated companion guides remain separate work. This release does not claim they are finished.

## Evidence and trust

The accepted formal receipt SHA-256 is `42ded58f00f816a1f7895039e6521b9e510f652baf9b6e86acd1eaa47d49f376`; terminal postflight SHA-256 is `b1d47aeab1cbe838109a751edd9bba55a57593d9e9ce0e852dc0f8988983f2f2`. `VERIFICATION_SUMMARY.json` supplies the rest of the identities, and `budget_v1.10.0/records/EVENTS.jsonl` preserves the event history.

The Lean compiler/kernel, standard axioms, pinned precompiled dependencies, and supporting runtime remain trusted. All project sources were compiled afresh; the dependencies were not rebuilt from source. Endpoint hashes do not detect a temporary change restored between checks. The focused printed-proof and statement audits do not certify every sentence or executable example in the full monograph.
